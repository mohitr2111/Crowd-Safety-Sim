import random
from typing import List, Optional, Tuple

class Agent:
    """Represents a single person in the crowd simulation"""
    
    # Agent types with different movement characteristics
    AGENT_TYPES = {
        "normal": {"speed": 0.3, "patience": 0.7},      # Was 1.4 - TOO FAST
        "family": {"speed": 0.2, "patience": 0.5},      # Was 0.9
        "elderly": {"speed": 0.15, "patience": 0.3},    # Was 0.6
        "rushing": {"speed": 0.4, "patience": 0.9},     # Was 2.0
    }
    
    def __init__(self, agent_id: int, start_node: str, goal_node: str, 
                 agent_type: str = "normal"):
        self.id = agent_id
        self.current_node = start_node
        self.goal_node = goal_node
        self.agent_type = agent_type
        
        # Movement characteristics
        self.speed = self.AGENT_TYPES[agent_type]["speed"]  # meters/second
        self.base_speed = self.speed  # Store original speed for panic recovery
        self.patience = self.AGENT_TYPES[agent_type]["patience"]  # 0-1 scale
        
        # Navigation state
        self.path: Optional[List[str]] = None
        self.path_index = 0
        self.wait_time = 0  # Seconds spent waiting (for statistics)
        self.blocked_until_time = 0.0  # Timestamp when intervention block expires (PHASE 2: Causal blocking)
        self.has_reached_goal = False
        self.total_travel_time = 0
        
        # Decision making
        self.preferred_personal_space = 2.0  # Preferred density (people/m²)
        self.panic_threshold = 4.0  # Density that triggers alternative routing
        self.base_panic_threshold = self.panic_threshold  # Store original
        
        # ============================================================
        # PHASE 2.2: Panic Propagation State
        # ============================================================
        self.panic_level = 0.0  # Current panic level (0.0 - 1.0)
        self.panic_source_id: Optional[str] = None  # ID of trigger causing panic
        self.panic_influenced_until = 0.0  # Timestamp when panic starts decaying
        self.panic_decay_rate = 0.02  # Panic reduction per second when safe
        
    def set_path(self, path: List[str]):
        """Set navigation path from current location to goal"""
        self.path = path
        self.path_index = 0
        
    def get_next_node(self) -> Optional[str]:
        """Get the next node in the planned path"""
        if not self.path or self.has_reached_goal:
            return None
            
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None
    
    def move_to_next_node(self) -> bool:
        """
        Attempt to move to next node in path
        Returns True if successful, False if blocked/waiting
        """
        next_node = self.get_next_node()
        if not next_node:
            return False
        
        # Movement is NOT instant - based on speed
        # Lower speed = more time steps needed to move
        import random
        if random.random() > self.speed:
            return False  # Agent didn't move this timestep
        
        self.current_node = next_node
        self.path_index += 1
        
        # Check if reached goal
        if self.current_node == self.goal_node:
            self.has_reached_goal = True
        
        return True

    
    def should_wait(self, current_density: float, current_time: float = 0.0) -> bool:
        """
        Decide whether to wait based on crowd density, patience, and intervention blocking.
        Higher patience = more willing to wait in crowds.
        
        PHASE 2: Now respects intervention blocking state (causal effect).
        """
        # PHASE 2: Check intervention-accumulated blocking (causal effect)
        if self.blocked_until_time > current_time:
            return True  # Force wait while blocked by intervention
        
        if current_density < self.preferred_personal_space:
            return False  # Not crowded, keep moving
            
        # Probability of waiting increases with density and patience
        wait_probability = (current_density / self.panic_threshold) * (1 - self.patience)
        return random.random() < wait_probability
    
    def is_blocked(self, current_time: float) -> bool:
        """Check if agent is currently blocked by an intervention"""
        return self.blocked_until_time > current_time
    
    def block_until(self, timestamp: float):
        """Block agent movement until specified timestamp (used by interventions)"""
        if timestamp > self.blocked_until_time:
            self.blocked_until_time = timestamp
    
    def needs_rerouting(self, current_density: float) -> bool:
        """Check if agent should seek alternative route due to crowding"""
        return current_density > self.panic_threshold
    
    # ============================================================
    # PHASE 2.2: Panic Propagation Methods
    # ============================================================
    
    def update_panic(self, new_level: float, source_id: str, current_time: float):
        """
        Update agent's panic level from propagation.
        
        Args:
            new_level: New panic level (0.0 - 1.0)
            source_id: Trigger ID causing the panic
            current_time: Current simulation time
        """
        # Only increase if new level is higher (panic accumulates, doesn't decrease instantly)
        if new_level > self.panic_level:
            self.panic_level = min(1.0, new_level)
            self.panic_source_id = source_id
            # Panic persists for at least 10 seconds before starting to decay
            self.panic_influenced_until = current_time + 10.0
            # Apply panic effects on behavior
            self._apply_panic_effects()
    
    def decay_panic(self, current_time: float, dt: float):
        """
        Decay panic level over time when not influenced by nearby triggers.
        
        Args:
            current_time: Current simulation time
            dt: Time step
        """
        if current_time > self.panic_influenced_until and self.panic_level > 0:
            # Gradual decay
            self.panic_level = max(0.0, self.panic_level - self.panic_decay_rate * dt)
            
            # If panic is very low, reset to calm state
            if self.panic_level < 0.05:
                self.panic_level = 0.0
                self.panic_source_id = None
                self._restore_normal_behavior()
    
    def _apply_panic_effects(self):
        """
        Apply panic effects to agent behavior.
        Higher panic = faster movement but reduced patience and lower panic threshold.
        """
        # Speed increases with panic (fleeing behavior)
        speed_multiplier = 1.0 + (self.panic_level * 0.5)  # Up to 50% faster
        self.speed = min(0.8, self.base_speed * speed_multiplier)  # Cap at 0.8
        
        # Patience decreases with panic (less willing to wait)
        patience_multiplier = 1.0 - (self.panic_level * 0.5)  # Up to 50% less patient
        self.patience = max(0.1, self.AGENT_TYPES[self.agent_type]["patience"] * patience_multiplier)
        
        # Panic threshold decreases (more sensitive to density)
        threshold_multiplier = 1.0 - (self.panic_level * 0.3)  # Up to 30% lower threshold
        self.panic_threshold = max(2.0, self.base_panic_threshold * threshold_multiplier)
    
    def _restore_normal_behavior(self):
        """Restore agent to normal behavior after panic subsides"""
        self.speed = self.base_speed
        self.patience = self.AGENT_TYPES[self.agent_type]["patience"]
        self.panic_threshold = self.base_panic_threshold
    
    def is_panicked(self) -> bool:
        """Check if agent is currently in a panicked state"""
        return self.panic_level > 0.2  # Threshold for "panicked"
    
    def get_panic_state(self) -> dict:
        """Get panic state for logging/visualization"""
        return {
            "panic_level": self.panic_level,
            "panic_source_id": self.panic_source_id,
            "is_panicked": self.is_panicked(),
            "speed_modifier": self.speed / self.base_speed,
            "patience_modifier": self.patience / self.AGENT_TYPES[self.agent_type]["patience"]
        }
    
    def update(self, dt: float, current_time: float = 0.0):
        """Update agent state (called each simulation tick)"""
        self.total_travel_time += dt
        # Decay panic over time
        self.decay_panic(current_time, dt)

