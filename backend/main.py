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
import json

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
    RouteConfig, 
    VehicleType,
    SimulationExportConfig
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
    config: SimulationExportConfig
):
    """Export simulation as SUMO-compatible files in ZIP format with vehicle distribution."""
    try:
        logger.info(f"Exporting simulation for network: {network_id}")
        
        # Get network data
        network_data = await map_service.get_network_data(network_id)
        
        # Validate entry and exit points
        if not config.selected_entry_points:
            raise HTTPException(status_code=400, detail="No entry points selected")
        if not config.selected_exit_points:
            raise HTTPException(status_code=400, detail="No exit points selected")
        
        # Generate routes with vehicle distribution
        routes_data = await sumo_export_service.generate_routes_with_vehicles(
            network_data=network_data,
            total_vehicles=config.total_vehicles,
            vehicle_distribution=config.vehicle_distribution,
            entry_points=config.selected_entry_points,
            exit_points=config.selected_exit_points,
            simulation_time=config.simulation_time,
            random_seed=config.random_seed
        )
        
        if not routes_data:
            raise HTTPException(status_code=400, detail="No valid routes could be generated for this network.")

        # Prepare simulation config
        config_data = {
            "simulation_time": config.simulation_time,
            "name": f"simulation_{network_id}"
        }
        
        # Export simulation
        zip_path = await sumo_export_service.export_simulation(
            network_data=network_data,
            routes=routes_data,
            simulation_config=config_data,
            selected_entry_points=config.selected_entry_points,
            selected_exit_points=config.selected_exit_points,
            vehicle_distribution=config.vehicle_distribution
        )
        
        # Return the ZIP file directly
        filename = os.path.basename(zip_path)
        return FileResponse(
            zip_path,
            filename=filename,
            media_type="application/zip"
        )
        
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

@app.post("/api/simulations/run/{network_id}")
async def run_simulation_with_gui(
    network_id: str,
    config: SimulationExportConfig
):
    """Run simulation with SUMO GUI using exported files."""
    try:
        logger.info(f"Running simulation with GUI for network: {network_id}")
        
        # Get network data
        network_data = await map_service.get_network_data(network_id)
        
        # Validate entry and exit points
        if not config.selected_entry_points:
            raise HTTPException(status_code=400, detail="No entry points selected")
        if not config.selected_exit_points:
            raise HTTPException(status_code=400, detail="No exit points selected")
        
        # Generate routes with vehicle distribution
        routes_data = await sumo_export_service.generate_routes_with_vehicles(
            network_data=network_data,
            total_vehicles=config.total_vehicles,
            vehicle_distribution=config.vehicle_distribution,
            entry_points=config.selected_entry_points,
            exit_points=config.selected_exit_points,
            simulation_time=config.simulation_time,
            random_seed=config.random_seed
        )
        
        if not routes_data:
            raise HTTPException(status_code=400, detail="No valid routes could be generated for this network.")

        # Prepare simulation config
        config_data = {
            "simulation_time": config.simulation_time,
            "name": f"simulation_{network_id}"
        }
        
        # Run simulation with GUI
        result = await sumo_export_service.run_simulation_with_gui(
            network_data=network_data,
            routes=routes_data,
            simulation_config=config_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to run simulation for {network_id}: {e}")
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

@app.post("/api/simulations/load-metadata")
async def load_simulation_metadata(file: UploadFile = File(...)):
    """Load simulation metadata from ZIP file or JSON file for reconstruction"""
    try:
        logger.info(f"Loading simulation metadata from: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Check if it's a ZIP file
        if file.filename.endswith('.zip'):
            import zipfile
            import io
            
            try:
                # Open ZIP file
                with zipfile.ZipFile(io.BytesIO(content), 'r') as zipf:
                    # Look for simulation_metadata.json in the ZIP
                    metadata_file_name = None
                    for file_name in zipf.namelist():
                        if file_name == 'simulation_metadata.json':
                            metadata_file_name = file_name
                            break
                    
                    if not metadata_file_name:
                        raise HTTPException(status_code=400, detail="No simulation_metadata.json found in ZIP file")
                    
                    # Read the JSON file from ZIP
                    with zipf.open(metadata_file_name) as json_file:
                        json_content = json_file.read().decode('utf-8')
                        metadata = json.loads(json_content)
                
                logger.info(f"Extracted metadata from ZIP: {file.filename}")
                
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="Invalid ZIP file format")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading ZIP file: {str(e)}")
        
        # Check if it's a JSON file
        elif file.filename.endswith('.json'):
            try:
                metadata = json.loads(content.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Only .zip or .json files are supported")
        
        # Validate metadata structure
        required_fields = ['simulation_info', 'network_data', 'nodes', 'edges', 'simulation_config', 'selected_points', 'routes']
        for field in required_fields:
            if field not in metadata:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        logger.info(f"Simulation metadata loaded successfully: {metadata['simulation_info']['name']}")
        
        return {
            "status": "success",
            "message": "Simulation metadata loaded successfully",
            "metadata": metadata,
            "simulation_name": metadata['simulation_info']['name'],
            "network_id": metadata['network_data']['id'],
            "node_count": metadata['network_data']['node_count'],
            "edge_count": metadata['network_data']['edge_count']
        }
        
    except Exception as e:
        logger.error(f"Failed to load simulation metadata: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting SUMO Helper API on {HOST}:{PORT}")
    uvicorn.run(
        app, 
        host=HOST, 
        port=PORT,
        log_level="info" if DEBUG else "warning"
    ) 