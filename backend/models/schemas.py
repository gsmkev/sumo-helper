from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class MapSelection(BaseModel):
    north: float = Field(..., description="North boundary latitude")
    south: float = Field(..., description="South boundary latitude")
    east: float = Field(..., description="East boundary longitude")
    west: float = Field(..., description="West boundary longitude")
    place_name: Optional[str] = Field(None, description="Optional place name")

class NetworkData(BaseModel):
    id: str
    name: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    bounds: Dict[str, float]

class RouteConfig(BaseModel):
    id: str
    from_edge: str
    to_edge: str
    vehicle_count: int = Field(..., ge=1, le=1000)
    vehicle_type: str = "passenger"
    start_time: int = 0
    end_time: int = 3600

class VehicleType(BaseModel):
    id: str
    name: str
    length: float
    max_speed: float
    accel: float = 2.6
    decel: float = 4.5
    sigma: float = 0.5
    min_gap: float = 2.5
    gui_shape: str = "passenger"

class SimulationConfig(BaseModel):
    """Simulation configuration (skeleton - not implemented)"""
    network_id: str
    routes: List[RouteConfig] = []
    simulation_time: int = Field(3600, ge=60, le=7200)
    step_length: float = 1.0
    use_gui: bool = False
    random_seed: Optional[int] = None
    output_prefix: str = "simulation"

class SimulationResult(BaseModel):
    """Simulation result (skeleton - not implemented)"""
    id: str
    status: str = "not_implemented"
    progress: float = 0.0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None
    output_files: List[str] = []

class Point(BaseModel):
    id: str
    x: float
    y: float
    edge_id: str
    type: str  # "entry" or "exit"

class NetworkPreview(BaseModel):
    id: str
    name: str
    preview_url: str
    bounds: Dict[str, float]
    node_count: int
    edge_count: int 