"""
OSMNX Service - OpenStreetMap Network Processing
Handles OSM data download, processing, and conversion to SUMO format
"""

import os
import json
import asyncio
import logging
import tempfile
import subprocess
import shutil
import signal
import math
from typing import Dict, Any, Optional

import osmnx as ox
import folium
import sumolib

logger = logging.getLogger(__name__)

class OSMNXService:
    """Service for handling OpenStreetMap data processing and SUMO conversion"""
    
    def __init__(self):
        """Initialize the OSMNX service with directories and configuration"""
        self.maps_dir = "static/maps"
        self.networks_dir = "static/networks"
        
        # Create necessary directories
        os.makedirs(self.maps_dir, exist_ok=True)
        os.makedirs(self.networks_dir, exist_ok=True)
        
        # Configure OSMnx settings
        ox.settings.use_cache = True
        ox.settings.log_console = False
        
        logger.info("OSMNXService initialized")
    
    async def select_area(self, north: float, south: float, east: float, west: float, place_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Select an area on the map and download OSM data
        
        Args:
            north: Northern boundary latitude
            south: Southern boundary latitude
            east: Eastern boundary longitude
            west: Western boundary longitude
            place_name: Optional name for the area
            
        Returns:
            Dictionary containing map information and metadata
            
        Raises:
            Exception: If area is too large or download fails
        """
        try:
            logger.info(f"Selecting area: {place_name or 'Custom area'} ({north:.4f}, {south:.4f}, {east:.4f}, {west:.4f})")
            
            # Validate area size - Increased to 1km x 1km
            area_size = abs((north - south) * (east - west))
            if area_size > 0.01:  # Approximately 1km x 1km
                raise Exception("Selected area is too large. Please select a smaller area (approximately 1km x 1km or less).")
            
            # Download roads including secondary streets and traffic lights
            custom_filter = '["highway"~"motorway|trunk|primary|secondary|tertiary|residential|service"]'
            
            # Download with timeout
            G = await self._download_osm_data(north, south, east, west, custom_filter)
            
            # Generate unique ID for this map
            map_id = f"map_{int(north*1000)}_{int(south*1000)}_{int(east*1000)}_{int(west*1000)}"
            
            # Save OSM data as GraphML
            graphml_file = os.path.join(self.maps_dir, f"{map_id}.graphml")
            ox.save_graphml(G, graphml_file)
            logger.info(f"Saved GraphML file: {graphml_file}")
            
            # Create preview map
            preview_file = await self._create_preview_map(G, map_id)
            
            # Get basic statistics
            node_count = len(G.nodes)
            edge_count = len(G.edges)
            
            logger.info(f"Map created successfully: {map_id} ({node_count} nodes, {edge_count} edges)")
            
            return {
                "id": map_id,
                "name": place_name or f"Map {map_id}",
                "graphml_file": graphml_file,
                "preview_url": f"/static/maps/{map_id}_preview.html",
                "bounds": {"north": north, "south": south, "east": east, "west": west},
                "node_count": node_count,
                "edge_count": edge_count,
                "status": "ready"
            }
            
        except Exception as e:
            logger.error(f"Error selecting area: {e}")
            raise Exception(f"Error selecting area: {str(e)}")
    
    async def _download_osm_data(self, north: float, south: float, east: float, west: float, custom_filter: str):
        """Download OSM data with timeout and error handling"""
        def timeout_handler(signum, frame):
            raise TimeoutError("Download timeout - please try a smaller area")
        
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                # Download road network
                G = ox.graph_from_bbox(
                    north, south, east, west,
                    custom_filter=custom_filter,
                    simplify=True
                )
                
                # Download traffic signals nodes
                tags = {'highway': 'traffic_signals'}
                traffic_signals = ox.geometries_from_bbox(north, south, east, west, tags)
                
                # Add traffic signal information to nodes
                for node_id, data in G.nodes(data=True):
                    # Check if this node has traffic signals nearby
                    node_lat = data.get('y')
                    node_lon = data.get('x')
                    if node_lat and node_lon:
                        # Look for traffic signals within 50 meters
                        for signal_id, signal_data in traffic_signals.iterrows():
                            signal_lat = signal_data.geometry.y
                            signal_lon = signal_data.geometry.x
                            distance = math.sqrt((node_lat - signal_lat)**2 + (node_lon - signal_lon)**2)
                            if distance < 0.0005:  # Approximately 50 meters
                                data['traffic_signals'] = True
                                break
                
                return G
            finally:
                signal.alarm(0)
                
        except TimeoutError:
            raise Exception("Download timeout - please try a smaller area or check your internet connection")
        except Exception as osm_error:
            error_msg = str(osm_error).lower()
            
            if "too many nodes" in error_msg:
                raise Exception("Selected area contains too many nodes. Please select a smaller area (approximately 1km x 1km or less).")
            elif "no data elements" in error_msg:
                # Try with broader filter if no main roads found
                logger.warning("No main roads found, trying with broader filter")
                return await self._download_osm_data_fallback(north, south, east, west)
            else:
                raise Exception(f"Error downloading map data: {str(osm_error)}")
    
    async def _download_osm_data_fallback(self, north: float, south: float, east: float, west: float):
        """Fallback download with broader filter"""
        def timeout_handler(signum, frame):
            raise TimeoutError("Download timeout")
        
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                G = ox.graph_from_bbox(
                    north, south, east, west,
                    network_type='drive',
                    simplify=True
                )
                return G
            finally:
                signal.alarm(0)
                
        except Exception as fallback_error:
            raise Exception("No roads found in the selected area. Try selecting a larger area or a different location with more roads.")
    
    async def _create_preview_map(self, G, map_id: str) -> str:
        """
        Create a preview map using folium
        
        Args:
            G: OSMnx graph object
            map_id: Unique map identifier
            
        Returns:
            Path to the created preview HTML file
        """
        try:
            # Calculate center coordinates
            center_lat, center_lon = self._calculate_graph_center(G)
            
            # Create folium map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
            
            # Add the network to the map
            ox.plot_graph_folium(
                G, 
                graph_map=m, 
                edge_color='blue', 
                edge_width=2, 
                node_color='red', 
                node_size=3
            )
            
            # Save the map
            preview_file = os.path.join(self.maps_dir, f"{map_id}_preview.html")
            m.save(preview_file)
            
            logger.info(f"Preview map created: {preview_file}")
            return preview_file
            
        except Exception as e:
            logger.error(f"Error creating preview map: {e}")
            raise Exception(f"Error creating preview map: {str(e)}")
    
    def _calculate_graph_center(self, G) -> tuple:
        """Calculate center coordinates from graph nodes"""
        # Check if graph has bbox properties
        if all(key in G.graph for key in ['bbox_north', 'bbox_south', 'bbox_east', 'bbox_west']):
            center_lat = (G.graph['bbox_north'] + G.graph['bbox_south']) / 2
            center_lon = (G.graph['bbox_east'] + G.graph['bbox_west']) / 2
            return center_lat, center_lon
        
        # Calculate center from actual node coordinates
        if len(G.nodes) == 0:
            raise Exception("No nodes found in the selected area. Try selecting a different area with main roads.")
        
        lats = [data['y'] for node, data in G.nodes(data=True) if 'y' in data]
        lons = [data['x'] for node, data in G.nodes(data=True) if 'x' in data]
        
        if not lats or not lons:
            raise Exception("No valid coordinates found in the selected area. Try selecting a different area.")
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        return center_lat, center_lon
    
    async def get_map_preview(self, map_id: str) -> Dict[str, Any]:
        """
        Get preview data for a specific map
        
        Args:
            map_id: Unique map identifier
            
        Returns:
            Dictionary containing map preview information
        """
        try:
            logger.info(f"Getting map preview for: {map_id}")
            
            graphml_file = os.path.join(self.maps_dir, f"{map_id}.graphml")
            if not os.path.exists(graphml_file):
                raise Exception("Map not found")
            
            # Load the graph
            G = ox.load_graphml(graphml_file)
            
            # Get bounds
            bounds = self._calculate_graph_bounds(G)
            
            return {
                "id": map_id,
                "preview_url": f"/static/maps/{map_id}_preview.html",
                "bounds": bounds,
                "node_count": len(G.nodes),
                "edge_count": len(G.edges)
            }
            
        except Exception as e:
            logger.error(f"Error getting map preview for {map_id}: {e}")
            raise Exception(f"Error getting map preview: {str(e)}")
    
    def _calculate_graph_bounds(self, G) -> Dict[str, float]:
        """Calculate bounds from graph nodes"""
        # Check if graph has bbox properties
        if all(key in G.graph for key in ['bbox_north', 'bbox_south', 'bbox_east', 'bbox_west']):
            return {
                "north": G.graph['bbox_north'],
                "south": G.graph['bbox_south'],
                "east": G.graph['bbox_east'],
                "west": G.graph['bbox_west']
            }
        
        # Calculate bounds from actual node coordinates
        if len(G.nodes) == 0:
            raise Exception("No nodes found in the network")
        
        lats = [data['y'] for node, data in G.nodes(data=True) if 'y' in data]
        lons = [data['x'] for node, data in G.nodes(data=True) if 'x' in data]
        
        if not lats or not lons:
            raise Exception("No valid coordinates found in the network")
        
        return {
            "north": max(lats),
            "south": min(lats),
            "east": max(lons),
            "west": min(lons)
        }
    
    async def convert_to_sumo(self, map_id: str) -> Dict[str, Any]:
        """
        Convert OSM data to SUMO .net.xml format
        
        Args:
            map_id: Unique map identifier
            
        Returns:
            Dictionary containing conversion results
        """
        try:
            logger.info(f"Converting map to SUMO format: {map_id}")
            
            graphml_file = os.path.join(self.maps_dir, f"{map_id}.graphml")
            if not os.path.exists(graphml_file):
                raise Exception("Map file not found")
            
            # Create network directory
            network_dir = os.path.join(self.networks_dir, map_id)
            os.makedirs(network_dir, exist_ok=True)
            
            # Load the graph
            G = ox.load_graphml(graphml_file)
            
            # Convert to SUMO format
            net_file = os.path.join(network_dir, f"{map_id}.net.xml")
            self._create_sumo_network(G, net_file)
            
            # Validate the generated network
            if not self._validate_sumo_network(net_file):
                raise Exception("Generated SUMO network is invalid")
            
            logger.info(f"SUMO conversion completed successfully: {net_file}")
            
            return {
                "network_id": map_id,
                "net_file": net_file,
                "status": "converted",
                "message": "Network converted to SUMO format successfully"
            }
            
        except Exception as e:
            logger.error(f"Error converting map {map_id} to SUMO: {e}")
            raise Exception(f"Error converting to SUMO: {str(e)}")
    
    def _create_sumo_network(self, G, net_file: str):
        """
        Create SUMO network file from OSMnx graph
        
        Args:
            G: OSMnx graph object
            net_file: Output SUMO network file path
        """
        try:
            # Validate that we have nodes and edges
            if len(G.nodes) == 0:
                raise Exception("No nodes found in the graph")
            if len(G.edges) == 0:
                raise Exception("No edges found in the graph")
            
            # Convert coordinates from longitude/latitude to local coordinates
            # Find the center point to use as origin
            all_x = [data.get('x', 0) for _, data in G.nodes(data=True) if 'x' in data]
            all_y = [data.get('y', 0) for _, data in G.nodes(data=True) if 'y' in data]
            
            if not all_x or not all_y:
                raise Exception("No valid coordinates found in graph")
            
            # Use the center as origin for local coordinates
            center_x = sum(all_x) / len(all_x)
            center_y = sum(all_y) / len(all_y)
            
            # Scale factor to convert degrees to meters (approximate)
            # 1 degree latitude ≈ 111,000 meters
            # 1 degree longitude ≈ 111,000 * cos(latitude) meters
            lat_scale = 111000  # meters per degree latitude
            lon_scale = 111000 * abs(math.cos(math.radians(center_y)))  # meters per degree longitude
            
            # Create SUMO network XML
            with open(net_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<net version="1.16" junctionCornerDetail="5" limitTurnSpeed="5.50" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">\n')
                
                # Write nodes (junctions)
                f.write('    <nodes>\n')
                node_count = 0
                for node_id, data in G.nodes(data=True):
                    if 'x' in data and 'y' in data:
                        # Convert to local coordinates
                        local_x = (data["x"] - center_x) * lon_scale
                        local_y = (data["y"] - center_y) * lat_scale
                        # Round to 2 decimal places to avoid parsing issues
                        local_x_rounded = round(local_x, 2)
                        local_y_rounded = round(local_y, 2)
                        # Save original lat/lon
                        lat = data["y"]
                        lon = data["x"]
                        # Check if this node has traffic signals
                        node_type = "traffic_light" if data.get('traffic_signals', False) else "priority"
                        f.write(f'        <node id="{node_id}" x="{local_x_rounded}" y="{local_y_rounded}" lat="{lat}" lon="{lon}" type="{node_type}"/>' + "\n")
                        node_count += 1
                
                if node_count == 0:
                    raise Exception("No valid nodes with coordinates found")
                    
                f.write('    </nodes>\n')
                
                # Write edges
                f.write('    <edges>\n')
                edge_count = 0
                edge_id_counter = 0
                for u, v, data in G.edges(data=True):
                    edge_id = f"edge_{edge_id_counter}_{u}_{v}"
                    edge_id_counter += 1
                    # Get default values with better defaults and handle list values
                    lanes_raw = data.get('lanes', 2)
                    if isinstance(lanes_raw, list):
                        if lanes_raw and len(lanes_raw) > 0:
                            try:
                                lanes = max(1, int(lanes_raw[0]))
                            except (ValueError, TypeError):
                                lanes = 2
                        else:
                            lanes = 2
                    else:
                        try:
                            lanes = max(1, int(lanes_raw))
                        except (ValueError, TypeError):
                            lanes = 2
                    
                    speed_raw = data.get('speed', 13.89)
                    if isinstance(speed_raw, list):
                        speed = max(5.56, float(speed_raw[0]) if speed_raw else 13.89)
                    else:
                        speed = max(5.56, float(speed_raw))
                    
                    length_raw = data.get('length', 100)
                    if isinstance(length_raw, list):
                        length = max(10, float(length_raw[0]) if length_raw else 100)
                    else:
                        length = max(10, float(length_raw))
                    
                    f.write(f'        <edge id="{edge_id}" from="{u}" to="{v}" numLanes="{lanes}" speed="{speed}" length="{length}"/>\n')
                    edge_count += 1
                
                if edge_count == 0:
                    raise Exception("No valid edges found")
                    
                f.write('    </edges>\n')
                
                # Skip connections section to avoid validation issues
                # SUMO will auto-generate connections based on the network topology
                connection_count = 0
                
                f.write('</net>\n')
            
            # Log some statistics
            logger.info(f"Created SUMO network with {node_count} nodes, {edge_count} edges, {connection_count} connections")
            
        except Exception as e:
            logger.error(f"Error creating SUMO network: {e}")
            raise Exception(f"Error creating SUMO network: {str(e)}")
    
    def _validate_sumo_network(self, net_file: str) -> bool:
        """
        Validate generated SUMO network using sumolib
        
        Args:
            net_file: Path to SUMO network file
            
        Returns:
            True if network is valid, False otherwise
        """
        try:
            # Check if file exists and has content
            if not os.path.exists(net_file):
                logger.error(f"Network file not found: {net_file}")
                return False
            
            file_size = os.path.getsize(net_file)
            if file_size == 0:
                logger.error(f"Network file is empty: {net_file}")
                return False
            
            logger.info(f"Network file size: {file_size} bytes")
            
            # Check if file has basic XML structure
            with open(net_file, 'r') as f:
                first_line = f.readline().strip()
                if not first_line.startswith('<?xml'):
                    logger.error(f"File does not start with XML declaration: {first_line}")
                    return False
                
                # Check for net tag
                content = f.read()
                if '<net' not in content:
                    logger.error("No <net> tag found in file")
                    return False
                if '</net>' not in content:
                    logger.error("No </net> tag found in file")
                    return False
            
            # Try to load with sumolib
            logger.info("Attempting to load with sumolib...")
            net = sumolib.net.readNet(net_file)
            edge_count = len(net.getEdges())
            node_count = len(net.getNodes())
            
            logger.info(f"SUMO network validation: {edge_count} edges, {node_count} nodes")
            
            if edge_count == 0:
                logger.error("No edges found in SUMO network")
                return False
            
            if node_count == 0:
                logger.error("No nodes found in SUMO network")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"SUMO network validation failed: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return False
    
    async def get_network_statistics(self, map_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a network
        
        Args:
            map_id: Unique map identifier
            
        Returns:
            Dictionary containing network statistics
        """
        try:
            logger.info(f"Getting network statistics for: {map_id}")
            
            graphml_file = os.path.join(self.maps_dir, f"{map_id}.graphml")
            if not os.path.exists(graphml_file):
                raise Exception("Map not found")
            
            # Load the graph
            G = ox.load_graphml(graphml_file)
            
            # Calculate statistics
            node_count = len(G.nodes)
            edge_count = len(G.edges)
            
            # Calculate total length
            total_length = sum(data.get('length', 0) for u, v, data in G.edges(data=True))
            
            # Calculate average speed
            speeds = [data.get('speed', 13.89) for u, v, data in G.edges(data=True)]
            avg_speed = sum(speeds) / len(speeds) if speeds else 13.89
            
            return {
                "id": map_id,
                "node_count": node_count,
                "edge_count": edge_count,
                "total_length": total_length,
                "average_speed": avg_speed,
                "density": edge_count / (node_count if node_count > 0 else 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting network statistics for {map_id}: {e}")
            raise Exception(f"Error getting network statistics: {str(e)}") 