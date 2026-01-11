"""
PHASE 4: Spawn Rate Control Module
Manages dynamic throttling of agent spawning at entry nodes
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SpawnRate(Enum):
    """Spawn rate levels"""
    NORMAL = 1.0  # 100% spawn rate
    REDUCED_25 = 0.75  # 75% spawn rate
    REDUCED_50 = 0.5  # 50% spawn rate
    REDUCED_75 = 0.25  # 25% spawn rate
    BLOCKED = 0.0  # 0% spawn rate (complete block)


@dataclass
class SpawnSchedule:
    """Scheduled spawn configuration for time-based spawning"""
    start_node: str
    goal_node: str
    agent_type: str
    total_count: int  # Total agents to spawn
    spawn_rate: float  # Agents per second
    start_time: float  # When to start spawning
    end_time: Optional[float] = None  # When to stop spawning (None = until all spawned)
    spawned_count: int = 0  # How many have been spawned so far
    is_active: bool = True


@dataclass
class SpawnControlState:
    """State of spawn control for a node"""
    node_id: str
    base_rate: float  # Base spawn rate (agents/second)
    current_rate: float  # Current effective spawn rate
    rate_multiplier: float = 1.0  # Multiplier (0.0 to 1.0)
    is_blocked: bool = False
    blocked_until: Optional[float] = None  # Timestamp when block expires
    scheduled_spawns: List[SpawnSchedule] = field(default_factory=list)
    total_spawned: int = 0
    total_blocked: int = 0


class SpawnRateController:
    """
    PHASE 4: Spawn Rate Controller
    
    Manages dynamic throttling of agent spawning at entry nodes.
    Allows reducing or blocking spawn rates based on density conditions.
    """
    
    def __init__(self):
        """Initialize spawn rate controller"""
        self.node_states: Dict[str, SpawnControlState] = {}
        self.default_spawn_rate = 10.0  # Default: 10 agents per second per entry node
        
    def initialize_node(self, node_id: str, base_rate: Optional[float] = None):
        """Initialize spawn control for an entry node"""
        if node_id not in self.node_states:
            self.node_states[node_id] = SpawnControlState(
                node_id=node_id,
                base_rate=base_rate or self.default_spawn_rate,
                current_rate=base_rate or self.default_spawn_rate,
            )
    
    def set_spawn_rate(
        self,
        node_id: str,
        rate_multiplier: float,
        duration: Optional[float] = None,
        current_time: float = 0.0
    ):
        """
        Set spawn rate multiplier for a node (0.0 to 1.0)
        
        Args:
            node_id: Entry node ID
            rate_multiplier: Spawn rate multiplier (0.0 = blocked, 1.0 = normal)
            duration: How long to apply (None = permanent until changed)
            current_time: Current simulation time
        """
        if node_id not in self.node_states:
            self.initialize_node(node_id)
        
        state = self.node_states[node_id]
        state.rate_multiplier = max(0.0, min(1.0, rate_multiplier))
        state.current_rate = state.base_rate * state.rate_multiplier
        
        if state.rate_multiplier == 0.0:
            state.is_blocked = True
            if duration:
                state.blocked_until = current_time + duration
            else:
                state.blocked_until = None
        else:
            state.is_blocked = False
            if duration:
                state.blocked_until = current_time + duration
            else:
                state.blocked_until = None
    
    def block_spawn(
        self,
        node_id: str,
        duration: Optional[float] = None,
        current_time: float = 0.0
    ):
        """Completely block spawning at a node"""
        self.set_spawn_rate(node_id, 0.0, duration, current_time)
        if node_id in self.node_states:
            self.node_states[node_id].total_blocked += 1
    
    def unblock_spawn(self, node_id: str):
        """Restore normal spawn rate"""
        self.set_spawn_rate(node_id, 1.0)
    
    def reduce_spawn_rate(
        self,
        node_id: str,
        reduction_percent: float,  # 0-100
        duration: Optional[float] = None,
        current_time: float = 0.0
    ):
        """Reduce spawn rate by percentage"""
        rate_multiplier = 1.0 - (reduction_percent / 100.0)
        self.set_spawn_rate(node_id, rate_multiplier, duration, current_time)
    
    def get_effective_spawn_rate(self, node_id: str, current_time: float = 0.0) -> float:
        """Get effective spawn rate for a node at current time"""
        if node_id not in self.node_states:
            return self.default_spawn_rate
        
        state = self.node_states[node_id]
        
        # Check if block has expired
        if state.blocked_until is not None and current_time >= state.blocked_until:
            state.is_blocked = False
            state.rate_multiplier = 1.0
            state.current_rate = state.base_rate
            state.blocked_until = None
        
        return state.current_rate
    
    def can_spawn(
        self,
        node_id: str,
        current_time: float = 0.0
    ) -> Tuple[bool, float]:
        """
        Check if an agent can be spawned at this node
        
        Returns:
            (can_spawn: bool, effective_rate: float)
        """
        if node_id not in self.node_states:
            self.initialize_node(node_id)
            return True, self.default_spawn_rate
        
        state = self.node_states[node_id]
        effective_rate = self.get_effective_spawn_rate(node_id, current_time)
        
        if state.is_blocked or effective_rate == 0.0:
            return False, 0.0
        
        return True, effective_rate
    
    def update_time(self, current_time: float):
        """Update controller time (check for expired blocks)"""
        for state in self.node_states.values():
            if state.blocked_until is not None and current_time >= state.blocked_until:
                state.is_blocked = False
                state.rate_multiplier = 1.0
                state.current_rate = state.base_rate
                state.blocked_until = None
    
    def get_state(self, node_id: str) -> Optional[Dict]:
        """Get current state of spawn control for a node"""
        if node_id not in self.node_states:
            return None
        
        state = self.node_states[node_id]
        return {
            "node_id": state.node_id,
            "base_rate": state.base_rate,
            "current_rate": state.current_rate,
            "rate_multiplier": state.rate_multiplier,
            "is_blocked": state.is_blocked,
            "blocked_until": state.blocked_until,
            "total_spawned": state.total_spawned,
            "total_blocked": state.total_blocked,
        }
    
    def get_all_states(self) -> Dict[str, Dict]:
        """Get states for all nodes"""
        return {
            node_id: self.get_state(node_id)
            for node_id in self.node_states.keys()
        }
    
    def reset(self):
        """Reset all spawn control states"""
        for state in self.node_states.values():
            state.rate_multiplier = 1.0
            state.current_rate = state.base_rate
            state.is_blocked = False
            state.blocked_until = None
            state.total_spawned = 0
            state.total_blocked = 0


# Global instance
spawn_rate_controller = SpawnRateController()

