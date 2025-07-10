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
from typing import Dict, List, Any, Optional
from pathlib import Path

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
        
        # Add vehicle types
        if vehicle_types:
            for vtype in vehicle_types:
                vtype_id = vtype.get('id', 'car')
                accel = vtype.get('accel', 2.6)
                decel = vtype.get('decel', 4.5)
                sigma = vtype.get('sigma', 0.5)
                length = vtype.get('length', 5)
                min_gap = vtype.get('minGap', 2.5)
                max_speed = vtype.get('maxSpeed', 16.67)
                gui_shape = vtype.get('guiShape', 'passenger')
                
                route_content += f"""
    <vType id="{vtype_id}" accel="{accel}" decel="{decel}" sigma="{sigma}" length="{length}" minGap="{min_gap}" maxSpeed="{max_speed}" guiShape="{gui_shape}"/>"""
        else:
            # Default vehicle type (same as simple_network_robust_gui.py)
            route_content += """
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>"""
        
        # Add routes
        for route in routes:
            route_id = route.get('id', f'route_{len(routes)}')
            edges = route.get('edges', '')
            vehicle_count = route.get('vehicle_count', 10)
            vehicle_type = route.get('vehicle_type', 'car')
            start_time = route.get('start_time', 0)
            end_time = route.get('end_time', 3600)
            
            route_content += f"""
    <route id="{route_id}" edges="{edges}"/>
    <flow id="flow_{route_id}" begin="{start_time}" end="{end_time}" vehsPerHour="{vehicle_count}" route="{route_id}" type="{vehicle_type}"/>"""
        
        route_content += """
</routes>"""
        return route_content
    
    def create_sumo_config(self, net_file: str, route_file: str, simulation_time: int = 200) -> str:
        """
        Create SUMO configuration file content
        
        Args:
            net_file: Network file name
            route_file: Route file name
            simulation_time: Simulation duration in seconds
            
        Returns:
            XML content for SUMO configuration file
        """
        config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{net_file}"/>
        <route-files value="{route_file}"/>
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
        "--no-turnarounds"
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
        return script_content
    
    async def export_simulation(
        self, 
        network_data: Dict[str, Any], 
        routes: List[Dict[str, Any]], 
        simulation_config: Dict[str, Any]
    ) -> str:
        """
        Export simulation as a ZIP file with all necessary SUMO files
        
        Args:
            network_data: Network data with nodes and edges
            routes: Route configurations
            simulation_config: Simulation configuration
            
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
            route_content = self.create_route_file(routes)
            config_content = self.create_sumo_config("network.net.xml", "routes.rou.xml", simulation_time)
            run_script = self.create_run_script(simulation_name)
            
            # Write files to temporary directory
            files_to_create = [
                ("nodes.nod.xml", nodes_content),
                ("edges.edg.xml", edges_content),
                ("routes.rou.xml", route_content),
                ("simulation.sumocfg", config_content),
                ("run_simulation.py", run_script)
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