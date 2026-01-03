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
        self.patience = self.AGENT_TYPES[agent_type]["patience"]  # 0-1 scale
        
        # Navigation state
        self.path: Optional[List[str]] = None
        self.path_index = 0
        self.wait_time = 0  # Seconds spent waiting
        self.has_reached_goal = False
        self.total_travel_time = 0
        
        # Decision making
        self.preferred_personal_space = 2.0  # Preferred density (people/m²)
        self.panic_threshold = 4.0  # Density that triggers alternative routing
        
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

    
    def should_wait(self, current_density: float) -> bool:
        """
        Decide whether to wait based on crowd density and patience
        Higher patience = more willing to wait in crowds
        """
        if current_density < self.preferred_personal_space:
            return False  # Not crowded, keep moving
            
        # Probability of waiting increases with density and patience
        wait_probability = (current_density / self.panic_threshold) * (1 - self.patience)
        return random.random() < wait_probability
    
    def needs_rerouting(self, current_density: float) -> bool:
        """Check if agent should seek alternative route due to crowding"""
        return current_density > self.panic_threshold
    
    def update(self, dt: float):
        """Update agent state (called each simulation tick)"""
        self.total_travel_time += dt
