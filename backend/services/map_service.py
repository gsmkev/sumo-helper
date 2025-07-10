"""
Map Service - Network Data Processing and Management
Handles SUMO network data extraction, analysis, and visualization
"""

import os
import json
import tempfile
import zipfile
import logging
import xml.etree.ElementTree as ET
import re
from typing import Dict, Any, List, Optional

import sumolib

logger = logging.getLogger(__name__)

class MapService:
    """Service for handling SUMO network data processing and visualization"""
    
    def __init__(self):
        """Initialize the Map service with directories"""
        self.networks_dir = "static/networks"
        self.simulations_dir = "static/simulations"
        
        # Create necessary directories
        os.makedirs(self.networks_dir, exist_ok=True)
        os.makedirs(self.simulations_dir, exist_ok=True)
        
        logger.info("MapService initialized")
    
    async def get_network_data(self, network_id: str) -> Dict[str, Any]:
        """
        Get network data (nodes, edges, coordinates) for visualization
        
        Args:
            network_id: Unique network identifier
            
        Returns:
            Dictionary containing network data for visualization
            
        Raises:
            Exception: If network file not found or parsing fails
        """
        try:
            logger.info(f"Getting network data for: {network_id}")
            
            net_file = os.path.join(self.networks_dir, network_id, f"{network_id}.net.xml")
            if not os.path.exists(net_file):
                raise Exception("Network file not found")
            
            # Parse XML directly to extract network data
            nodes, edges, bounds = await self._parse_network_xml(net_file, network_id)
            
            # Filter nodes and edges by bounding box if available
            if bounds:
                nodes, edges = self._filter_by_bounds(nodes, edges, bounds)
            
            # Calculate normalized bounds for visualization
            bounds_dict = self._calculate_normalized_bounds(nodes)
            
            logger.info(f"Network data extracted: {len(nodes)} nodes, {len(edges)} edges")
            
            return {
                "id": network_id,
                "name": network_id,
                "nodes": nodes,
                "edges": edges,
                "bounds": bounds_dict,
                "status": "converted",
                "message": "Network data extracted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting network data for {network_id}: {e}")
            raise Exception(f"Error getting network data: {str(e)}")
    
    async def _parse_network_xml(self, net_file: str, network_id: str) -> tuple:
        """
        Parse SUMO network XML file to extract nodes and edges
        
        Args:
            net_file: Path to SUMO network XML file
            network_id: Network identifier for bounds extraction
            
        Returns:
            Tuple of (nodes, edges, bounds)
        """
        try:
            tree = ET.parse(net_file)
            root = tree.getroot()
            
            # Extract nodes
            nodes = []
            node_latlon_map = {}
            
            for node_elem in root.findall('.//node'):
                node_data = self._parse_node_element(node_elem)
                if node_data:
                    nodes.append(node_data)
                    if node_data.get('lat') and node_data.get('lon'):
                        node_latlon_map[node_data['id']] = (node_data['lat'], node_data['lon'])
            
            # Extract edges
            edges = []
            for edge_elem in root.findall('.//edge'):
                edge_data = self._parse_edge_element(edge_elem, node_latlon_map, nodes)
                if edge_data:
                    edges.append(edge_data)
            
            # Extract bounds from network_id
            bounds = self._extract_bounds_from_id(network_id)
            
            return nodes, edges, bounds
            
        except Exception as e:
            logger.error(f"Error parsing network XML: {e}")
            raise Exception(f"Error parsing network XML: {str(e)}")
    
    def _parse_node_element(self, node_elem) -> Optional[Dict[str, Any]]:
        """Parse a node XML element"""
        try:
            node_id = node_elem.get('id')
            x_str = node_elem.get('x')
            y_str = node_elem.get('y')
            
            if not all([node_id, x_str, y_str]):
                logger.warning(f"Node {node_id} has missing coordinates, skipping")
                return None
            
            x = float(x_str)
            y = float(y_str)
            node_type = node_elem.get('type', 'priority')
            lat = float(node_elem.get('lat')) if node_elem.get('lat') else None
            lon = float(node_elem.get('lon')) if node_elem.get('lon') else None
            
            return {
                "id": node_id,
                "x": x,
                "y": y,
                "type": node_type,
                "lat": lat,
                "lon": lon
            }
            
        except ValueError as e:
            logger.warning(f"Node {node_id} has invalid coordinates: {e}")
            return None
    
    def _parse_edge_element(self, edge_elem, node_latlon_map: Dict, nodes: List[Dict]) -> Optional[Dict[str, Any]]:
        """Parse an edge XML element"""
        try:
            edge_id = edge_elem.get('id')
            from_node = edge_elem.get('from')
            to_node = edge_elem.get('to')
            
            if not all([edge_id, from_node, to_node]):
                logger.warning(f"Edge {edge_id} has missing attributes, skipping")
                return None
            
            # Get edge properties
            num_lanes = int(edge_elem.get('numLanes', '2'))
            speed = float(edge_elem.get('speed', '13.89'))
            length = float(edge_elem.get('length', '100'))
            
            # Calculate shape coordinates
            shape_coords = self._calculate_edge_shape(from_node, to_node, node_latlon_map, nodes)
            if not shape_coords:
                logger.warning(f"Edge {edge_id} has missing node coordinates, skipping")
                return None
            
            return {
                "id": edge_id,
                "from": from_node,
                "to": to_node,
                "shape": shape_coords,
                "length": length,
                "speed": speed,
                "lanes": num_lanes
            }
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Edge {edge_id} has invalid properties: {e}")
            return None
    
    def _calculate_edge_shape(self, from_node: str, to_node: str, node_latlon_map: Dict, nodes: List[Dict]) -> Optional[List]:
        """Calculate edge shape coordinates"""
        # Try to use lat/lon coordinates first
        from_coords = node_latlon_map.get(from_node)
        to_coords = node_latlon_map.get(to_node)
        
        if from_coords and to_coords:
            return [from_coords, to_coords]
        
        # Fallback to normalized x/y coordinates
        from_xy = next((n['x'], n['y']) for n in nodes if n['id'] == from_node)
        to_xy = next((n['x'], n['y']) for n in nodes if n['id'] == to_node)
        
        if from_xy and to_xy:
            return [from_xy, to_xy]
        
        return None
    
    def _extract_bounds_from_id(self, network_id: str) -> Optional[Dict[str, float]]:
        """Extract bounding box from network ID"""
        m = re.match(r"map_([\d-]+)_([\d-]+)_([\d-]+)_([\d-]+)", network_id)
        if m:
            north = float(m.group(1)) / 1000
            south = float(m.group(2)) / 1000
            east = float(m.group(3)) / 1000
            west = float(m.group(4)) / 1000
            
            return {
                'north': max(north, south),
                'south': min(north, south),
                'east': max(east, west),
                'west': min(east, west)
            }
        return None
    
    def _filter_by_bounds(self, nodes: List[Dict], edges: List[Dict], bounds: Dict[str, float]) -> tuple:
        """Filter nodes and edges by bounding box"""
        def in_bbox(node):
            return (node.get('lon') is not None and node.get('lat') is not None and
                    bounds['west'] <= node['lon'] <= bounds['east'] and
                    bounds['south'] <= node['lat'] <= bounds['north'])
        
        filtered_nodes = [n for n in nodes if in_bbox(n)]
        node_ids = set(n['id'] for n in filtered_nodes)
        filtered_edges = [e for e in edges if e['from'] in node_ids and e['to'] in node_ids]
        
        return filtered_nodes, filtered_edges
    
    def _calculate_normalized_bounds(self, nodes: List[Dict]) -> Dict[str, float]:
        """Calculate normalized bounds for visualization"""
        if not nodes:
            return {"xmin": 0, "ymin": 0, "xmax": 0, "ymax": 0}
        
        x_coords = [node["x"] for node in nodes]
        y_coords = [node["y"] for node in nodes]
        
        bounds_dict = {
            "xmin": min(x_coords),
            "ymin": min(y_coords),
            "xmax": max(x_coords),
            "ymax": max(y_coords)
        }
        
        # Normalize coordinates for better visualization
        x_range = bounds_dict["xmax"] - bounds_dict["xmin"]
        y_range = bounds_dict["ymax"] - bounds_dict["ymin"]
        
        if x_range > 0 and y_range > 0:
            scale_factor = min(200 / x_range, 200 / y_range)
            
            for node in nodes:
                node["x"] = (node["x"] - bounds_dict["xmin"] - x_range / 2) * scale_factor
                node["y"] = (node["y"] - bounds_dict["ymin"] - y_range / 2) * scale_factor
            
            bounds_dict = {"xmin": -100, "ymin": -100, "xmax": 100, "ymax": 100}
        
        return bounds_dict
    
    async def get_entry_points(self, network_id: str) -> List[Dict[str, Any]]:
        """
        Get available entry points for the network
        
        Args:
            network_id: Unique network identifier
            
        Returns:
            List of entry points with coordinates
        """
        try:
            logger.info(f"Getting entry points for: {network_id}")
            
            net_file = os.path.join(self.networks_dir, network_id, f"{network_id}.net.xml")
            if not os.path.exists(net_file):
                raise Exception("Network file not found")
            
            net = sumolib.net.readNet(net_file)
            
            entry_points = []
            for edge in net.getEdges():
                # Consider edges with no incoming connections as entry points
                if len(edge.getIncoming()) == 0:
                    from_node = edge.getFromNode()
                    if from_node is not None:
                        try:
                            x, y = from_node.getCoord()
                            entry_points.append({
                                "id": edge.getID(),
                                "x": x,
                                "y": y,
                                "name": edge.getID()
                            })
                        except Exception as coord_error:
                            logger.warning(f"Could not get coordinates for edge {edge.getID()}: {coord_error}")
                            # Add entry point without coordinates
                            entry_points.append({
                                "id": edge.getID(),
                                "x": 0,
                                "y": 0,
                                "name": edge.getID()
                            })
            
            logger.info(f"Found {len(entry_points)} entry points")
            return entry_points
            
        except Exception as e:
            logger.error(f"Error getting entry points for {network_id}: {e}")
            raise Exception(f"Error getting entry points: {str(e)}")
    
    async def get_exit_points(self, network_id: str) -> List[Dict[str, Any]]:
        """
        Get available exit points for the network
        
        Args:
            network_id: Unique network identifier
            
        Returns:
            List of exit points with coordinates
        """
        try:
            logger.info(f"Getting exit points for: {network_id}")
            
            net_file = os.path.join(self.networks_dir, network_id, f"{network_id}.net.xml")
            if not os.path.exists(net_file):
                raise Exception("Network file not found")
            
            net = sumolib.net.readNet(net_file)
            
            exit_points = []
            for edge in net.getEdges():
                # Consider edges with no outgoing connections as exit points
                if len(edge.getOutgoing()) == 0:
                    to_node = edge.getToNode()
                    if to_node is not None:
                        try:
                            x, y = to_node.getCoord()
                            exit_points.append({
                                "id": edge.getID(),
                                "x": x,
                                "y": y,
                                "name": edge.getID()
                            })
                        except Exception as coord_error:
                            logger.warning(f"Could not get coordinates for edge {edge.getID()}: {coord_error}")
                            # Add exit point without coordinates
                            exit_points.append({
                                "id": edge.getID(),
                                "x": 0,
                                "y": 0,
                                "name": edge.getID()
                            })
            
            logger.info(f"Found {len(exit_points)} exit points")
            return exit_points
            
        except Exception as e:
            logger.error(f"Error getting exit points for {network_id}: {e}")
            raise Exception(f"Error getting exit points: {str(e)}")
    
    async def configure_routes(self, network_id: str, routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Configure routes between entry and exit points
        
        Args:
            network_id: Unique network identifier
            routes: List of route configurations
            
        Returns:
            Dictionary containing route configuration results
        """
        try:
            logger.info(f"Configuring routes for network: {network_id}")
            
            net_file = os.path.join(self.networks_dir, network_id, f"{network_id}.net.xml")
            if not os.path.exists(net_file):
                raise Exception("Network file not found")
            
            net = sumolib.net.readNet(net_file)
            
            # Create simulation directory
            sim_dir = os.path.join(self.simulations_dir, network_id)
            os.makedirs(sim_dir, exist_ok=True)
            
            # Generate route file
            route_file = os.path.join(sim_dir, f"{network_id}.rou.xml")
            self._generate_route_file(net, routes, route_file)
            
            # Generate configuration file
            config_file = os.path.join(sim_dir, f"{network_id}.sumocfg")
            self._generate_config_file(net_file, route_file, config_file)
            
            logger.info(f"Routes configured successfully: {len(routes)} routes")
            
            return {
                "network_id": network_id,
                "route_file": route_file,
                "config_file": config_file,
                "routes_count": len(routes),
                "status": "configured"
            }
            
        except Exception as e:
            logger.error(f"Error configuring routes for {network_id}: {e}")
            raise Exception(f"Error configuring routes: {str(e)}")
    
    def _generate_route_file(self, net, routes: List[Dict[str, Any]], route_file: str):
        """Generate SUMO route file"""
        try:
            with open(route_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<routes>\n')
                
                # Write vehicle types
                f.write('  <vType id="passenger" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>\n')
                f.write('  <vType id="bus" accel="1.2" decel="4.5" sigma="0.5" length="12" minGap="3" maxSpeed="13.89" guiShape="bus"/>\n')
                f.write('  <vType id="truck" accel="1.3" decel="4.5" sigma="0.5" length="8" minGap="3" maxSpeed="11.11" guiShape="truck"/>\n')
                
                # Write routes
                for i, route in enumerate(routes):
                    route_id = f"route_{i}"
                    f.write(f'  <route id="{route_id}" edges="{route["from"]} {route["to"]}"/>\n')
                
                # Write vehicles
                for i, route in enumerate(routes):
                    vehicle_id = f"vehicle_{i}"
                    route_id = f"route_{i}"
                    vehicle_type = route.get("vehicle_type", "passenger")
                    depart_time = route.get("depart_time", i * 2)
                    
                    f.write(f'  <vehicle id="{vehicle_id}" type="{vehicle_type}" route="{route_id}" depart="{depart_time}"/>\n')
                
                f.write('</routes>\n')
            
            logger.info(f"Route file generated: {route_file}")
            
        except Exception as e:
            logger.error(f"Error generating route file: {e}")
            raise Exception(f"Error generating route file: {str(e)}")
    
    def _generate_config_file(self, net_file: str, route_file: str, config_file: str):
        """Generate SUMO configuration file"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<configuration>\n')
                f.write('  <input>\n')
                f.write(f'    <net-file value="{os.path.basename(net_file)}"/>\n')
                f.write(f'    <route-files value="{os.path.basename(route_file)}"/>\n')
                f.write('  </input>\n')
                f.write('  <time>\n')
                f.write('    <begin value="0"/>\n')
                f.write('    <end value="3600"/>\n')
                f.write('  </time>\n')
                f.write('  <processing>\n')
                f.write('    <time-to-teleport value="-1"/>\n')
                f.write('  </processing>\n')
                f.write('  <routing>\n')
                f.write('    <device.rerouting.probability value="0.1"/>\n')
                f.write('  </routing>\n')
                f.write('</configuration>\n')
            
            logger.info(f"Configuration file generated: {config_file}")
            
        except Exception as e:
            logger.error(f"Error generating configuration file: {e}")
            raise Exception(f"Error generating configuration file: {str(e)}")
    
    async def export_sumo_network(self, network_id: str) -> str:
        """
        Export network in SUMO format
        
        Args:
            network_id: Unique network identifier
            
        Returns:
            Path to exported network file
        """
        try:
            logger.info(f"Exporting SUMO network: {network_id}")
            
            net_file = os.path.join(self.networks_dir, network_id, f"{network_id}.net.xml")
            if not os.path.exists(net_file):
                raise Exception("Network file not found")
            
            return net_file
            
        except Exception as e:
            logger.error(f"Error exporting SUMO network {network_id}: {e}")
            raise Exception(f"Error exporting network: {str(e)}")
    
    async def export_traci_ready(self, network_id: str) -> str:
        """
        Export network ready for TraCI usage
        
        Args:
            network_id: Unique network identifier
            
        Returns:
            Path to exported ZIP file
        """
        try:
            logger.info(f"Exporting TraCI-ready network: {network_id}")
            
            network_dir = os.path.join(self.networks_dir, network_id)
            if not os.path.exists(network_dir):
                raise Exception("Network directory not found")
            
            # Create ZIP file
            zip_file = os.path.join(self.networks_dir, f"{network_id}_traci.zip")
            with zipfile.ZipFile(zip_file, 'w') as zipf:
                for root, dirs, files in os.walk(network_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, network_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"TraCI-ready network exported: {zip_file}")
            return zip_file
            
        except Exception as e:
            logger.error(f"Error exporting TraCI-ready network {network_id}: {e}")
            raise Exception(f"Error exporting TraCI-ready network: {str(e)}")
    
    async def process_uploaded_network(self, file_path: str) -> Dict[str, Any]:
        """
        Process uploaded network file
        
        Args:
            file_path: Path to uploaded network file
            
        Returns:
            Dictionary containing processing results
        """
        try:
            logger.info(f"Processing uploaded network: {file_path}")
            
            # Validate file
            if not file_path.endswith('.net.xml'):
                raise Exception("Only .net.xml files are supported")
            
            if not os.path.exists(file_path):
                raise Exception("Uploaded file not found")
            
            # Generate network ID from filename
            filename = os.path.basename(file_path)
            network_id = filename.replace('.net.xml', '')
            
            # Create network directory
            network_dir = os.path.join(self.networks_dir, network_id)
            os.makedirs(network_dir, exist_ok=True)
            
            # Copy file to network directory
            dest_file = os.path.join(network_dir, filename)
            with open(file_path, 'rb') as src, open(dest_file, 'wb') as dst:
                dst.write(src.read())
            
            logger.info(f"Uploaded network processed: {network_id}")
            
            return {
                "network_id": network_id,
                "file_path": dest_file,
                "status": "uploaded",
                "message": "Network uploaded successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing uploaded network: {e}")
            raise Exception(f"Error processing uploaded network: {str(e)}") 