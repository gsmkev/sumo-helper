"""
SUMO Helper API - Main Application
Web-based traffic simulation tool with OSM integration

This module provides the FastAPI application with endpoints for:
- Map selection and OSM data processing
- Network analysis and visualization
- Simulation configuration and execution
- File upload and export functionality
"""

import os
import logging
import shutil
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from services.map_service import MapService
from services.simulation_service import SimulationService
from services.osmnx_service import OSMNXService
from services.sumo_export_service import SUMOExportService
from models.schemas import (
    MapSelection, 
    NetworkData, 
    RouteConfig, 
    SimulationConfig,
    VehicleType,
    SimulationResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sumo_helper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

# Global services
map_service: Optional[MapService] = None
simulation_service: Optional[SimulationService] = None
osmnx_service: Optional[OSMNXService] = None
sumo_export_service: Optional[SUMOExportService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown"""
    global map_service, simulation_service, osmnx_service, sumo_export_service
    
    # Startup
    logger.info("Starting SUMO Helper API...")
    try:
        map_service = MapService()
        simulation_service = SimulationService()
        osmnx_service = OSMNXService()
        sumo_export_service = SUMOExportService()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SUMO Helper API...")
    # Cleanup resources if needed

# Create FastAPI application
app = FastAPI(
    title="SUMO Helper API",
    description="Web-based traffic simulation tool with OSM integration",
    version="1.0.0",
    debug=DEBUG,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket connected. Total connections: {len(active_connections)}")
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"WebSocket message received: {data}")
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(active_connections)}")

async def broadcast_message(message: str):
    """Send message to all connected WebSocket clients"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.warning(f"Failed to send message to WebSocket: {e}")
            disconnected.append(connection)
    
    # Remove disconnected connections
    for connection in disconnected:
        active_connections.remove(connection)

# Health and status endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SUMO Helper API",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services are available
        services_status = {
            "map_service": map_service is not None,
            "simulation_service": simulation_service is not None,
            "osmnx_service": osmnx_service is not None,
            "sumo_export_service": sumo_export_service is not None
        }
        
        all_healthy = all(services_status.values())
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "services": services_status,
            "websocket_connections": len(active_connections)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Map Selection and OSM Integration
@app.post("/api/maps/select-area")
async def select_map_area(selection: MapSelection):
    """Select an area on the map and generate OSM data"""
    try:
        logger.info(f"Selecting map area: {selection.place_name or 'Custom area'}")
        result = await osmnx_service.select_area(
            north=selection.north,
            south=selection.south,
            east=selection.east,
            west=selection.west,
            place_name=selection.place_name
        )
        logger.info(f"Map area selected successfully: {result.get('map_id', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"Failed to select map area: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/maps/preview/{map_id}")
async def get_map_preview(map_id: str):
    """Get a preview of the selected map area"""
    try:
        logger.info(f"Getting map preview for: {map_id}")
        preview_data = await osmnx_service.get_map_preview(map_id)
        return preview_data
    except Exception as e:
        logger.error(f"Failed to get map preview for {map_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/maps/convert-to-sumo/{map_id}")
async def convert_to_sumo(map_id: str):
    """Convert OSM data to SUMO .net.xml format"""
    try:
        logger.info(f"Converting map to SUMO format: {map_id}")
        result = await osmnx_service.convert_to_sumo(map_id)
        logger.info(f"Map converted successfully: {map_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to convert map {map_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Network Analysis
@app.get("/api/networks/{network_id}")
async def get_network_data(network_id: str):
    """Get network data (nodes, edges, coordinates)"""
    try:
        logger.info(f"Getting network data for: {network_id}")
        network_data = await map_service.get_network_data(network_id)
        logger.info(f"Network data retrieved: {len(network_data.get('nodes', []))} nodes, {len(network_data.get('edges', []))} edges")
        return network_data
    except Exception as e:
        logger.error(f"Failed to get network data for {network_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/networks/{network_id}/entry-points")
async def get_entry_points(network_id: str):
    """Get available entry points for the network"""
    try:
        logger.info(f"Getting entry points for: {network_id}")
        entry_points = await map_service.get_entry_points(network_id)
        logger.info(f"Found {len(entry_points)} entry points")
        return entry_points
    except Exception as e:
        logger.error(f"Failed to get entry points for {network_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/networks/{network_id}/exit-points")
async def get_exit_points(network_id: str):
    """Get available exit points for the network"""
    try:
        logger.info(f"Getting exit points for: {network_id}")
        exit_points = await map_service.get_exit_points(network_id)
        logger.info(f"Found {len(exit_points)} exit points")
        return exit_points
    except Exception as e:
        logger.error(f"Failed to get exit points for {network_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

# Route Configuration
@app.post("/api/networks/{network_id}/routes")
async def configure_routes(network_id: str, routes: List[RouteConfig]):
    """Configure routes between entry and exit points"""
    try:
        logger.info(f"Configuring routes for network: {network_id}")
        result = await map_service.configure_routes(network_id, routes)
        logger.info(f"Routes configured successfully: {len(routes)} routes")
        return result
    except Exception as e:
        logger.error(f"Failed to configure routes for {network_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Vehicle Types
@app.get("/api/vehicle-types")
async def get_vehicle_types():
    """Get available vehicle types"""
    vehicle_types = [
        VehicleType(id="passenger", name="Passenger Car", length=5.0, max_speed=16.67),
        VehicleType(id="bus", name="Bus", length=12.0, max_speed=13.89),
        VehicleType(id="truck", name="Truck", length=8.0, max_speed=11.11),
        VehicleType(id="motorcycle", name="Motorcycle", length=2.5, max_speed=20.83),
        VehicleType(id="bicycle", name="Bicycle", length=1.6, max_speed=5.56)
    ]
    logger.info(f"Returning {len(vehicle_types)} vehicle types")
    return vehicle_types

# Simulation Configuration (Skeleton - Not Implemented)
@app.post("/api/simulations/configure")
async def configure_simulation(config: SimulationConfig):
    """Configure simulation parameters (skeleton - not implemented)"""
    try:
        logger.info(f"Simulation configuration requested (skeleton mode)")
        result = await simulation_service.configure_simulation(config.dict())
        return result
    except Exception as e:
        logger.error(f"Simulation configuration error: {e}")
        raise HTTPException(status_code=400, detail="Simulation configuration not implemented yet")

@app.post("/api/simulations/start/{simulation_id}")
async def start_simulation(simulation_id: str):
    """Start a simulation (skeleton - not implemented)"""
    try:
        logger.info(f"Simulation start requested for {simulation_id} (skeleton mode)")
        result = await simulation_service.start_simulation(simulation_id)
        return result
    except Exception as e:
        logger.error(f"Simulation start error: {e}")
        raise HTTPException(status_code=400, detail="Simulation start not implemented yet")

@app.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get simulation status and progress (skeleton - not implemented)"""
    try:
        logger.debug(f"Simulation status requested for {simulation_id} (skeleton mode)")
        status = await simulation_service.get_simulation_status(simulation_id)
        return status
    except Exception as e:
        logger.error(f"Simulation status error: {e}")
        raise HTTPException(status_code=404, detail="Simulation status not implemented yet")

@app.get("/api/simulations/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    """Get simulation results (skeleton - not implemented)"""
    try:
        logger.info(f"Simulation results requested for {simulation_id} (skeleton mode)")
        results = await simulation_service.get_simulation_results(simulation_id)
        return results
    except Exception as e:
        logger.error(f"Simulation results error: {e}")
        raise HTTPException(status_code=404, detail="Simulation results not implemented yet")

# Export functionality
@app.get("/api/networks/{network_id}/export")
async def export_network(network_id: str, format: str = "sumo"):
    """Export network in specified format"""
    try:
        logger.info(f"Exporting network {network_id} in format: {format}")
        
        if format == "sumo":
            file_path = await map_service.export_sumo_network(network_id)
            return FileResponse(file_path, filename=f"{network_id}.net.xml")
        elif format == "traci":
            file_path = await map_service.export_traci_ready(network_id)
            return FileResponse(file_path, filename=f"{network_id}_traci.zip")
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
    except Exception as e:
        logger.error(f"Failed to export network {network_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/simulations/export/{network_id}")
async def export_simulation(
    network_id: str,
    data: Dict[str, Any]
):
    """Export simulation as SUMO-compatible files in ZIP format, siempre usando entry/exit edges válidos."""
    try:
        logger.info(f"Exporting simulation for network: {network_id}")
        
        # Get network data
        network_data = await map_service.get_network_data(network_id)
        all_edges = set(e['id'] for e in network_data.get('edges', []))

        # Get entry and exit points
        entry_points = await map_service.get_entry_points(network_id)
        exit_points = await map_service.get_exit_points(network_id)
        entry_ids = [e['id'] for e in entry_points]
        exit_ids = [e['id'] for e in exit_points]

        # Extract data from request
        routes = data.get('routes', [])
        simulation_config = data.get('simulation_config', {})
        routes_data = []

        if not routes:
            # Si no hay rutas, generar rutas de ejemplo para todos los pares entry-exit
            for entry in entry_ids:
                for exit in exit_ids:
                    if entry != exit:
                        routes_data.append({
                            "id": f"route_{entry}_to_{exit}",
                            "edges": f"{entry} {exit}",
                            "vehicle_count": 30,
                            "vehicle_type": "car",
                            "start_time": 0,
                            "end_time": simulation_config.get('simulation_time', 3600)
                        })
        else:
            # Si hay rutas, validar y corregir los IDs
            for route in routes:
                from_edge = route.get('from_edge')
                to_edge = route.get('to_edge')
                # Si el edge no existe, usar el primero de la lista
                if from_edge not in all_edges:
                    from_edge = entry_ids[0] if entry_ids else None
                if to_edge not in all_edges:
                    to_edge = exit_ids[0] if exit_ids else None
                if not from_edge or not to_edge:
                    continue  # No se puede crear la ruta
                routes_data.append({
                    "id": route.get('id', f"route_{from_edge}_to_{to_edge}"),
                    "edges": f"{from_edge} {to_edge}",
                    "vehicle_count": route.get('vehicle_count', 10),
                    "vehicle_type": route.get('vehicle_type', 'car'),
                    "start_time": route.get('start_time', 0),
                    "end_time": route.get('end_time', simulation_config.get('simulation_time', 3600))
                })

        if not routes_data:
            raise HTTPException(status_code=400, detail="No valid routes could be generated for this network.")

        # Prepare simulation config
        config_data = {
            "simulation_time": simulation_config.get('simulation_time', 3600),
            "name": f"simulation_{network_id}"
        }
        
        # Export simulation
        zip_path = await sumo_export_service.export_simulation(
            network_data=network_data,
            routes=routes_data,
            simulation_config=config_data
        )
        
        # Get export info
        export_info = await sumo_export_service.get_export_info(zip_path)
        
        logger.info(f"Simulation exported successfully: {export_info['file_name']}")
        return export_info
        
    except Exception as e:
        logger.error(f"Failed to export simulation for {network_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/simulations/download/{filename}")
async def download_simulation(filename: str):
    """Download exported simulation file"""
    try:
        file_path = os.path.join("static/exports", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            file_path, 
            filename=filename,
            media_type="application/zip"
        )
        
    except Exception as e:
        logger.error(f"Failed to download simulation file {filename}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# File upload
@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file (e.g., existing .net.xml)"""
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Validate file type
        if not file.filename.endswith('.net.xml'):
            raise HTTPException(status_code=400, detail="Only .net.xml files are supported")
        
        # Save uploaded file
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process file
        result = await map_service.process_uploaded_network(file_path)
        logger.info(f"File uploaded and processed successfully: {file.filename}")
        return result
    except Exception as e:
        logger.error(f"Failed to upload file {file.filename}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting SUMO Helper API on {HOST}:{PORT}")
    uvicorn.run(
        app, 
        host=HOST, 
        port=PORT,
        log_level="info" if DEBUG else "warning"
    ) 