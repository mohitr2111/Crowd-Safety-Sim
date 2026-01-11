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

class InterventionRequest(BaseModel):
    """PHASE 2: Request to execute an approved intervention"""
    node_id: str
    action: str  # CLOSE_TEMPORARILY, REDUCE_FLOW, REROUTE
    priority: Optional[str] = None  # CRITICAL, WARNING, INFO

class AutoExecutionSettings(BaseModel):
    """PHASE 3: Auto-execution settings"""
    auto_execute_enabled: bool = True
    disabled_nodes: Optional[List[str]] = None
    max_pending_actions: Optional[int] = None

class SpawnRateControlRequest(BaseModel):
    """PHASE 4: Spawn rate control request"""
    node_id: str
    rate_multiplier: float  # 0.0 to 1.0
    duration: Optional[float] = None  # How long to apply (None = permanent)

class CapacityAdjustmentRequest(BaseModel):
    """PHASE 4: Capacity adjustment request"""
    node_id: str
    adjustment_type: str  # expand_area, increase_flow, block_zone, restore
    factor: Optional[float] = None  # Expansion/increase factor
    duration: Optional[float] = None  # How long to apply (None = permanent)

class SafetyConstraintsSettings(BaseModel):
    """PHASE 4: Safety constraints settings"""
    max_interventions_per_minute: Optional[float] = None
    min_interval_seconds: Optional[float] = None
    max_active_interventions: Optional[int] = None
    enable_rollback: Optional[bool] = None
    enable_manual_override: Optional[bool] = None

class RollbackRequest(BaseModel):
    """PHASE 4: Rollback request"""
    intervention_id: Optional[str] = None  # None = rollback most recent