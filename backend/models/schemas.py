from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SpawnConfig(BaseModel):
    start: str
    goal: str
    count: int
    type: str = "normal"

class NodeData(BaseModel):
    id: str
    position: tuple
    type: str
    capacity: int
    area_m2: float

class SimulationRequest(BaseModel):
    scenario: str
    spawn_config: List[SpawnConfig]
    time_step: float = 1.0
    crowd_preset: Optional[str] = None
    use_dynamic_spawning: Optional[bool] = False

class SimulationStepRequest(BaseModel):
    simulation_id: str
    steps: int = 1

class SimulationState(BaseModel):
    """Flexible simulation state that accepts various field formats"""
    class Config:
        extra = "allow"  # Allow extra fields from simulator
    
    time: float
    
    # Support both old and new field names
    nodes: Optional[Dict[str, Any]] = {}
    agents: Optional[Dict[str, Any]] = {}
    node_densities: Optional[Dict[str, float]] = {}
    
    total_agents: Optional[int] = 0
    active_agents: Optional[int] = 0
    reached_goal: Optional[int] = 0
    max_density: Optional[float] = 0.0
    danger_violations: Optional[int] = 0
    danger_zones: Optional[List[str]] = []

class SimulationResponse(BaseModel):
    simulation_id: str
    message: str
    initial_state: SimulationState
