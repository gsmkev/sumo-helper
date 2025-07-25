"""
SUMO Export Service - Generate SUMO simulation files
Handles the generation of SUMO-compatible files for simulation export

This service generates the same file format as simple_network_robust_gui.py:
- nodes.nod.xml
- edges.edg.xml  
- routes.rou.xml
- simulation.sumocfg
"""

import os
import json
import logging
import tempfile
import zipfile
import time
import random
import math
from typing import Dict, List, Any, Optional
from pathlib import Path
import heapq

from models.schemas import VehicleDistribution

logger = logging.getLogger(__name__)

class SUMOExportService:
    """Service for generating SUMO simulation files"""
    
    def __init__(self):
        """Initialize the SUMO Export service"""
        self.exports_dir = "static/exports"
        os.makedirs(self.exports_dir, exist_ok=True)
        
        logger.info("SUMOExportService initialized")
    
    def create_nodes_file(self, nodes: List[Dict[str, Any]]) -> str:
        """
        Create SUMO nodes file content
        
        Args:
            nodes: List of node dictionaries with id, x, y coordinates
            
        Returns:
            XML content for nodes file
        """
        nodes_content = """<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">"""
        
        for node in nodes:
            node_id = node.get('id', 'unknown')
            x = node.get('x', 0)
            y = node.get('y', 0)
            node_type = node.get('type', 'priority')
            
            nodes_content += f"""
    <node id="{node_id}" x="{x}" y="{y}" type="{node_type}"/>"""
        
        nodes_content += """
</nodes>"""
        return nodes_content
    
    def create_edges_file(self, edges: List[Dict[str, Any]]) -> str:
        """
        Create SUMO edges file content
        
        Args:
            edges: List of edge dictionaries with id, from, to, lanes, speed
            
        Returns:
            XML content for edges file
        """
        edges_content = """<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">"""
        
        for edge in edges:
            edge_id = edge.get('id', 'unknown')
            from_node = edge.get('from', 'unknown')
            to_node = edge.get('to', 'unknown')
            num_lanes = edge.get('numLanes', 1)
            speed = edge.get('speed', 13.89)  # Default 50 km/h
            
            edges_content += f"""
    <edge id="{edge_id}" from="{from_node}" to="{to_node}" numLanes="{num_lanes}" speed="{speed}"/>"""
        
        edges_content += """
</edges>"""
        return edges_content
    
    def create_traffic_lights_file(self, nodes: List[Dict[str, Any]]) -> str:
        """
        Create SUMO traffic lights file content
        
        Args:
            nodes: List of node dictionaries with id, x, y coordinates
            
        Returns:
            XML content for traffic lights file
        """
        # For now, create an empty additional file since SUMO will auto-generate traffic lights
        # when using netconvert with the --tls.guess=true option
        traffic_lights_content = """<?xml version="1.0" encoding="UTF-8"?>
<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">
    <!-- Traffic lights will be auto-generated by SUMO netconvert -->
</additional>"""
        
        logger.info("Generated empty traffic lights file - SUMO will auto-generate traffic lights")
        return traffic_lights_content
    
    def create_route_file(self, routes: List[Dict[str, Any]], vehicle_types: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Create SUMO routes file content
        
        Args:
            routes: List of route configurations
            vehicle_types: List of vehicle type definitions
            
        Returns:
            XML content for routes file
        """
        route_content = """<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">"""
        
        # Add vehicle types based on pinv01-25-traffic-sim.txt reference
        route_content += """
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
    <vType id="motorcycle" accel="2.6" decel="4.5" sigma="0.5" length="2.5" minGap="1.5" maxSpeed="20.83" guiShape="motorcycle"/>
    <vType id="bus" accel="1.2" decel="4.5" sigma="0.5" length="12" minGap="3" maxSpeed="13.89" guiShape="bus"/>
    <vType id="truck" accel="1.3" decel="4.5" sigma="0.5" length="8" minGap="3" maxSpeed="11.11" guiShape="truck"/>"""
        
        # Sort routes by departure time to avoid warnings
        sorted_routes = sorted(routes, key=lambda x: x.get('start_time', 0))
        
        # Add routes and vehicles
        for route in sorted_routes:
            route_id = route.get('id', f'route_{len(routes)}')
            edges = route.get('edges', '')
            vehicle_count = route.get('vehicle_count', 1)
            vehicle_type = route.get('vehicle_type', 'car')
            start_time = route.get('start_time', 0)
            end_time = route.get('end_time', 3600)
            color = route.get('color', 'yellow')
            attributes = route.get('attributes', '')
            vehicle_id = route.get('vehicle_id', f'vehicle_{route_id}')
            
            # Add route
            route_content += f"""
    <route id="{route_id}" edges="{edges}"/>"""
            
            # Add individual vehicle or flow
            if vehicle_count == 1:
                # Single vehicle - only include valid SUMO attributes
                vehicle_attrs = f'color="{color}"'
                # Only include attributes that are valid for SUMO vehicles
                if attributes and 'length' not in attributes:
                    vehicle_attrs += f' {attributes}'
                route_content += f"""
    <vehicle id="{vehicle_id}" type="{vehicle_type}" route="{route_id}" depart="{start_time}" {vehicle_attrs}/>"""
            else:
                # Flow of vehicles
                route_content += f"""
    <flow id="flow_{route_id}" begin="{start_time}" end="{end_time}" vehsPerHour="{vehicle_count}" route="{route_id}" type="{vehicle_type}" color="{color}"/>"""
        
        route_content += """
</routes>"""
        return route_content
    
    def create_sumo_config(self, net_file: str, route_file: str, additional_file: str = None, simulation_time: int = 200) -> str:
        """
        Create SUMO configuration file content
        
        Args:
            net_file: Network file name
            route_file: Route file name
            additional_file: Additional file name (for traffic lights)
            simulation_time: Simulation duration in seconds
            
        Returns:
            XML content for SUMO configuration file
        """
        # Handle additional file input safely
        if additional_file is not None and additional_file != "":
            additional_input = f"""
        <additional-files value="{additional_file}"/>"""
        else:
            additional_input = ""
        
        config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{net_file}"/>
        <route-files value="{route_file}"/>{additional_input}
    </input>
    <time>
        <begin value="0"/>
        <end value="{simulation_time}"/>
    </time>
    <processing>
        <ignore-route-errors value="true"/>
        <collision.action value="warn"/>
    </processing>
    <report>
        <verbose value="true"/>
        <no-step-log value="true"/>
    </report>
</configuration>"""
        return config_content
    
    def create_run_script(self, simulation_name: str) -> str:
        """
        Create a Python script to run the simulation
        
        Args:
            simulation_name: Name of the simulation
            
        Returns:
            Python script content
        """
        script_content = f'''#!/usr/bin/env python3
"""
Simulación de tráfico generada por SUMO Helper
Archivo: {simulation_name}

Para ejecutar esta simulación:
1. Asegúrate de tener SUMO instalado: sudo apt-get install sumo sumo-tools sumo-gui sumo-doc
2. Ejecuta: python3 run_simulation.py
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def run_simulation():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    print(f"=== Simulación de Tráfico: {simulation_name} ===")
    print(f"Directorio: {{script_dir}}")
    print()
    
    # Check if SUMO is installed
    try:
        result = subprocess.run(["sumo-gui", "--version"], check=True, capture_output=True, text=True)
        print(f"SUMO-GUI encontrado: {{result.stdout.split()[1]}}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: sumo-gui no está instalado o no está en el PATH")
        print("Instala SUMO con: sudo apt-get install sumo sumo-tools sumo-gui sumo-doc")
        return False
    
    # Generate network with netconvert
    print("\\nGenerando red con netconvert...")
    netconvert_cmd = [
        "netconvert",
        "--node-files", "nodes.nod.xml",
        "--edge-files", "edges.edg.xml",
        "--output-file", "network.net.xml",
        "--no-turnarounds",
        "--tls.guess", "true"
    ]
    
    result = subprocess.run(netconvert_cmd, cwd=script_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Error generando la red:")
        print(result.stderr)
        return False
    
    print("✅ Red generada: network.net.xml")
    
    # Start simulation
    print("\\nIniciando simulación en SUMO-GUI...")
    sumo_cmd = ["sumo-gui", "-c", "simulation.sumocfg", "--no-step-log", "true"]
    subprocess.run(sumo_cmd, cwd=script_dir)
    
    return True

if __name__ == "__main__":
    run_simulation()
'''
        return script_content
    

    
    async def generate_routes_with_vehicles(
        self,
        network_data: Dict[str, Any],
        total_vehicles: int,
        vehicle_distribution: List[VehicleDistribution],
        entry_points: List[str],
        exit_points: List[str],
        simulation_time: int,
        random_seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate routes with vehicle distribution from entry to exit points
        - depart times are strictly increasing globally
        - only color is allowed as vehicle attribute
        - Dijkstra is used for valid routes
        """
        try:
            if random_seed is not None:
                random.seed(random_seed)
            total_percentage = sum(vd.percentage for vd in vehicle_distribution)
            if abs(total_percentage - 100.0) > 0.01:
                raise Exception(f"Vehicle distribution percentages must sum to 100%, got {total_percentage}%")
            vehicle_counts = {}
            for vd in vehicle_distribution:
                vehicle_type = vd.vehicle_type
                percentage = vd.percentage
                count = int((percentage / 100.0) * total_vehicles)
                vehicle_counts[vehicle_type] = count
            actual_total = sum(vehicle_counts.values())
            if actual_total < total_vehicles:
                first_type = vehicle_distribution[0].vehicle_type
                vehicle_counts[first_type] += (total_vehicles - actual_total)
            logger.info(f"Vehicle distribution: {vehicle_counts}")
            # Build graph for Dijkstra
            edges = network_data.get('edges', [])
            graph = {}
            for edge in edges:
                from_node = edge.get('from')
                to_node = edge.get('to')
                edge_id = edge.get('id')
                if from_node not in graph:
                    graph[from_node] = []
                graph[from_node].append((to_node, edge_id))
            # Dijkstra shortest path
            def dijkstra(start, goal):
                queue = [(0, start, [])]
                visited = set()
                while queue:
                    cost, node, path = heapq.heappop(queue)
                    if node == goal:
                        return path
                    if node in visited:
                        continue
                    visited.add(node)
                    for neighbor, edge_id in graph.get(node, []):
                        if neighbor not in visited:
                            heapq.heappush(queue, (cost+1, neighbor, path + [edge_id]))
                return None
            # Generate routes
            routes_data = []
            vehicle_id_counter = 0
            global_depart = 0.0
            depart_step = simulation_time / max(1, total_vehicles)
            for vehicle_type, count in vehicle_counts.items():
                if count == 0:
                    continue
                vd_config = next((vd for vd in vehicle_distribution if vd.vehicle_type == vehicle_type), None)
                if not vd_config:
                    continue
                for i in range(count):
                    entry_point = random.choice(entry_points)
                    closest_exit = random.choice(exit_points)
                    # Find valid path using Dijkstra
                    route_path = dijkstra(entry_point, closest_exit)
                    if not route_path:
                        continue
                    depart_time = global_depart
                    global_depart += depart_step
                    route_id = f"route_{vehicle_type}_{vehicle_id_counter}"
                    routes_data.append({
                        "id": route_id,
                        "edges": " ".join(route_path),
                        "vehicle_count": 1,
                        "vehicle_type": vehicle_type,
                        "start_time": depart_time,
                        "end_time": depart_time + 1,
                        "color": vd_config.color,
                        "attributes": "",  # Only color allowed
                        "vehicle_id": f"{vehicle_type}_{vehicle_id_counter}"
                    })
                    vehicle_id_counter += 1
            logger.info(f"Generated {len(routes_data)} routes for {total_vehicles} vehicles")
            return routes_data
        except Exception as e:
            logger.error(f"Error generating routes with vehicles: {e}")
            raise Exception(f"Error generating routes: {str(e)}")
    
    def _find_closest_exit_point(
        self, 
        network_data: Dict[str, Any], 
        entry_point: str, 
        exit_points: List[str]
    ) -> Optional[str]:
        """Find the closest exit point to a given entry point"""
        try:
            # For now, use simple random selection
            # TODO: Implement actual distance calculation using network topology
            return random.choice(exit_points)
        except Exception as e:
            logger.warning(f"Error finding closest exit point: {e}")
            return None
    
    def _calculate_route_path(
        self, 
        network_data: Dict[str, Any], 
        entry_point: str, 
        exit_point: str
    ) -> Optional[List[str]]:
        """Calculate route path from entry to exit point using real edge IDs"""
        try:
            edges = network_data.get('edges', [])
            
            # Create a mapping from node pairs to edge IDs
            edge_mapping = {}
            for edge in edges:
                edge_id = edge.get('id', '')
                from_node = edge.get('from', '')
                to_node = edge.get('to', '')
                
                # Store both directions
                edge_mapping[(from_node, to_node)] = edge_id
                # Also store reverse direction if it's a bidirectional edge
                if edge.get('bidirectional', False):
                    edge_mapping[(to_node, from_node)] = edge_id
            
            # Try to find a direct edge from entry to exit
            direct_edge = edge_mapping.get((entry_point, exit_point))
            if direct_edge:
                return [direct_edge]
            
            # If no direct edge, try to find a path through intermediate nodes
            # For now, use a simple approach: find any edge that starts from entry_point
            # and any edge that ends at exit_point, then connect them
            entry_edges = []
            exit_edges = []
            
            for edge in edges:
                edge_id = edge.get('id', '')
                from_node = edge.get('from', '')
                to_node = edge.get('to', '')
                
                if from_node == entry_point:
                    entry_edges.append((edge_id, to_node))
                if to_node == exit_point:
                    exit_edges.append((edge_id, from_node))
            
            # If we have both entry and exit edges, try to find a connection
            if entry_edges and exit_edges:
                # Pick a random entry edge and a random exit edge
                entry_edge_id, entry_to_node = random.choice(entry_edges)
                exit_edge_id, exit_from_node = random.choice(exit_edges)
                
                # If they connect through the same intermediate node, great!
                if entry_to_node == exit_from_node:
                    return [entry_edge_id, exit_edge_id]
                
                # Otherwise, try to find a connecting edge
                connecting_edge = edge_mapping.get((entry_to_node, exit_from_node))
                if connecting_edge:
                    return [entry_edge_id, connecting_edge, exit_edge_id]
                
                # If no direct connection, just use the entry and exit edges
                # (this might create an invalid route, but it's better than nothing)
                return [entry_edge_id, exit_edge_id]
            
            # If we can't find a proper path, return None
            logger.warning(f"Could not find valid route from {entry_point} to {exit_point}")
            return None
            
        except Exception as e:
            logger.warning(f"Error calculating route path: {e}")
            return None
    
    async def export_simulation(
        self, 
        network_data: Dict[str, Any], 
        routes: List[Dict[str, Any]], 
        simulation_config: Dict[str, Any],
        selected_entry_points: List[str] = None,
        selected_exit_points: List[str] = None,
        vehicle_distribution: List[Dict[str, Any]] = None
    ) -> str:
        """
        Export simulation as a ZIP file with all necessary SUMO files and metadata JSON
        
        Args:
            network_data: Network data with nodes and edges
            routes: Route configurations
            simulation_config: Simulation configuration
            selected_entry_points: List of selected entry point IDs
            selected_exit_points: List of selected exit point IDs
            vehicle_distribution: Vehicle distribution configuration
            
        Returns:
            Path to the generated ZIP file
        """
        try:
            # Create temporary directory for file generation
            temp_dir = tempfile.mkdtemp(prefix="sumo_export_")
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # Extract data
            nodes = network_data.get('nodes', [])
            edges = network_data.get('edges', [])
            simulation_time = simulation_config.get('simulation_time', 200)
            simulation_name = simulation_config.get('name', 'simulation')
            
            # Generate SUMO files
            nodes_content = self.create_nodes_file(nodes)
            edges_content = self.create_edges_file(edges)
            traffic_lights_content = self.create_traffic_lights_file(nodes)
            route_content = self.create_route_file(routes)
            config_content = self.create_sumo_config("network.net.xml", "routes.rou.xml", "traffic_lights.add.xml", simulation_time)
            run_script = self.create_run_script(simulation_name)
            
            # Generate metadata JSON
            metadata_json = self.create_simulation_metadata_json(
                network_data=network_data,
                routes=routes,
                simulation_config=simulation_config,
                selected_entry_points=selected_entry_points or [],
                selected_exit_points=selected_exit_points or [],
                vehicle_distribution=vehicle_distribution or []
            )
            
            # Write files to temporary directory
            files_to_create = [
                ("nodes.nod.xml", nodes_content),
                ("edges.edg.xml", edges_content),
                ("traffic_lights.add.xml", traffic_lights_content),
                ("routes.rou.xml", route_content),
                ("simulation.sumocfg", config_content),
                ("run_simulation.py", run_script),
                ("simulation_metadata.json", metadata_json)
            ]
            
            for filename, content in files_to_create:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created file: {filename}")
            
            # Create ZIP file
            zip_filename = f"simulation_{int(time.time())}.zip"
            zip_path = os.path.join(self.exports_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, _ in files_to_create:
                    file_path = os.path.join(temp_dir, filename)
                    zipf.write(file_path, filename)
            
            logger.info(f"Created ZIP file: {zip_path}")
            
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir)
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Error exporting simulation: {e}")
            raise Exception(f"Export error: {str(e)}")
    
    async def get_export_info(self, zip_path: str) -> Dict[str, Any]:
        """
        Get information about an exported simulation
        
        Args:
            zip_path: Path to the ZIP file
            
        Returns:
            Dictionary with export information
        """
        try:
            file_size = os.path.getsize(zip_path)
            file_name = os.path.basename(zip_path)
            
            return {
                "file_path": zip_path,
                "file_name": file_name,
                "file_size": file_size,
                "download_url": f"/static/exports/{file_name}"
            }
            
        except Exception as e:
            logger.error(f"Error getting export info: {e}")
            raise Exception(f"Error getting export info: {str(e)}") 

    async def run_simulation_with_gui(
        self, 
        network_data: Dict[str, Any], 
        routes: List[Dict[str, Any]], 
        simulation_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run simulation with SUMO GUI using temporary files
        
        Args:
            network_data: Network data with nodes and edges
            routes: Route configurations
            simulation_config: Simulation configuration
            
        Returns:
            Dictionary containing simulation run results
        """
        try:
            # Create temporary directory for simulation files
            temp_dir = tempfile.mkdtemp(prefix="sumo_simulation_")
            logger.info(f"Created temporary directory for simulation: {temp_dir}")
            
            # Extract data
            nodes = network_data.get('nodes', [])
            edges = network_data.get('edges', [])
            simulation_time = simulation_config.get('simulation_time', 200)
            simulation_name = simulation_config.get('name', 'simulation')
            
            # Generate SUMO files
            nodes_content = self.create_nodes_file(nodes)
            edges_content = self.create_edges_file(edges)
            traffic_lights_content = self.create_traffic_lights_file(nodes)
            route_content = self.create_route_file(routes)
            config_content = self.create_sumo_config("network.net.xml", "routes.rou.xml", "traffic_lights.add.xml", simulation_time)
            
            # Write files to temporary directory
            files_to_create = [
                ("nodes.nod.xml", nodes_content),
                ("edges.edg.xml", edges_content),
                ("traffic_lights.add.xml", traffic_lights_content),
                ("routes.rou.xml", route_content),
                ("simulation.sumocfg", config_content)
            ]
            
            for filename, content in files_to_create:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created simulation file: {filename}")
            
            # Generate network with netconvert
            logger.info("Generating network with netconvert...")
            netconvert_cmd = [
                "netconvert",
                "--node-files", "nodes.nod.xml",
                "--edge-files", "edges.edg.xml",
                "--output-file", "network.net.xml",
                "--no-turnarounds",
                "--tls.guess", "true"
            ]
            
            import subprocess
            result = subprocess.run(netconvert_cmd, cwd=temp_dir, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error generating network: {result.stderr}")
                raise Exception(f"Failed to generate network: {result.stderr}")
            
            logger.info("Network generated successfully")
            
            # Start SUMO GUI simulation in background
            logger.info("Starting SUMO GUI simulation...")
            sumo_cmd = ["sumo-gui", "-c", "simulation.sumocfg", "--no-step-log", "true"]
            
            # Run SUMO GUI in background process
            process = subprocess.Popen(
                sumo_cmd, 
                cwd=temp_dir, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment to check if process started successfully
            import time
            time.sleep(1)
            
            if process.poll() is not None:
                # Process has already terminated
                stdout, stderr = process.communicate()
                logger.error(f"SUMO GUI failed to start: {stderr}")
                raise Exception(f"SUMO GUI failed to start: {stderr}")
            
            logger.info(f"SUMO GUI simulation started successfully (PID: {process.pid})")
            
            return {
                "status": "running",
                "message": "SUMO GUI simulation started successfully",
                "process_id": process.pid,
                "temp_directory": temp_dir,
                "simulation_name": simulation_name,
                "simulation_time": simulation_time,
                "total_vehicles": len(routes)
            }
            
        except Exception as e:
            logger.error(f"Error running simulation with GUI: {e}")
            # Clean up temporary directory if it exists
            if 'temp_dir' in locals():
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except:
                    pass
            raise Exception(f"Error running simulation: {str(e)}") 

    def create_simulation_metadata_json(
        self,
        network_data: Dict[str, Any],
        routes: List[Dict[str, Any]],
        simulation_config: Dict[str, Any],
        selected_entry_points: List[str],
        selected_exit_points: List[str],
        vehicle_distribution: List[Dict[str, Any]]
    ) -> str:
        """
        Create a JSON file with all simulation metadata for reconstruction
        
        Args:
            network_data: Network data with nodes and edges
            routes: Route configurations
            simulation_config: Simulation configuration
            selected_entry_points: List of selected entry point IDs
            selected_exit_points: List of selected exit point IDs
            vehicle_distribution: Vehicle distribution configuration
            
        Returns:
            JSON content as string
        """
        try:
            # Extract data
            nodes = network_data.get('nodes', [])
            edges = network_data.get('edges', [])
            bounds = network_data.get('bounds', {})
            
            # Create comprehensive metadata
            metadata = {
                "simulation_info": {
                    "name": simulation_config.get('name', 'simulation'),
                    "created_at": time.time(),
                    "version": "1.0",
                    "description": "SUMO simulation metadata for reconstruction"
                },
                "network_data": {
                    "id": network_data.get('id', ''),
                    "name": network_data.get('name', ''),
                    "bounds": bounds,
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                },
                "nodes": [
                    {
                        "id": node.get('id'),
                        "x": node.get('x'),
                        "y": node.get('y'),
                        "lat": node.get('lat'),
                        "lon": node.get('lon'),
                        "type": node.get('type', 'priority'),
                        "is_entry_point": node.get('id') in selected_entry_points,
                        "is_exit_point": node.get('id') in selected_exit_points
                    }
                    for node in nodes
                ],
                "edges": [
                    {
                        "id": edge.get('id'),
                        "from": edge.get('from'),
                        "to": edge.get('to'),
                        "shape": edge.get('shape'),
                        "length": edge.get('length'),
                        "speed": edge.get('speed'),
                        "lanes": edge.get('lanes')
                    }
                    for edge in edges
                ],
                "simulation_config": {
                    "total_vehicles": simulation_config.get('total_vehicles', 100),
                    "simulation_time": simulation_config.get('simulation_time', 3600),
                    "random_seed": simulation_config.get('random_seed'),
                    "vehicle_distribution": [
                        {
                            "vehicle_type": vd.get("vehicle_type") if isinstance(vd, dict) else vd.vehicle_type,
                            "percentage": vd.get("percentage") if isinstance(vd, dict) else vd.percentage,
                            "color": vd.get("color") if isinstance(vd, dict) else vd.color,
                            "period": vd.get("period") if isinstance(vd, dict) else vd.period,
                            "attributes": vd.get("attributes") if isinstance(vd, dict) else vd.attributes
                        }
                        for vd in vehicle_distribution
                    ]
                },
                "selected_points": {
                    "entry_points": selected_entry_points,
                    "exit_points": selected_exit_points
                },
                "routes": [
                    {
                        "id": route.get('id'),
                        "edges": route.get('edges', []),
                        "vehicle_type": route.get('vehicle_type', 'car'),
                        "depart_time": route.get('depart_time', 0),
                        "color": route.get('color', 'yellow')
                    }
                    for route in routes
                ],
                "reconstruction_info": {
                    "instructions": "Para reconstruir esta simulación:",
                    "steps": [
                        "1. Cargar el archivo simulation_metadata.json",
                        "2. Usar los datos de nodes y edges para recrear la red",
                        "3. Aplicar la configuración de simulación",
                        "4. Configurar los puntos de entrada y salida seleccionados",
                        "5. Aplicar la distribución de vehículos",
                        "6. Generar las rutas basadas en los datos de routes"
                    ],
                    "file_structure": {
                        "nodes.nod.xml": "Definición de nodos de la red",
                        "edges.edg.xml": "Definición de aristas de la red",
                        "routes.rou.xml": "Rutas y flujos de vehículos",
                        "simulation.sumocfg": "Configuración de la simulación",
                        "traffic_lights.add.xml": "Semáforos detectados",
                        "run_simulation.py": "Script para ejecutar la simulación",
                        "simulation_metadata.json": "Metadatos completos para reconstrucción"
                    }
                }
            }
            
            return json.dumps(metadata, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error creating simulation metadata JSON: {e}")
            raise Exception(f"Error creating metadata JSON: {str(e)}") 