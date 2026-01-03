"""
Stadium Manager - Handles capacity, exits, and real-time recommendations
"""
from typing import Dict, List, Tuple, Optional
import random

class StadiumManager:
    """Manages stadium capacity, exits, and generates AI recommendations"""
    
    def __init__(self, stadium_config: Dict):
        self.capacity = stadium_config.get("capacity", 10000)
        self.sections = stadium_config.get("sections", ["North", "South", "East", "West"])
        self.exits = stadium_config.get("exits", {})
        self.arrival_patterns = stadium_config.get("arrival_patterns", {})
        
        # Track occupancy
        self.current_occupancy = 0
        self.section_occupancy = {section: 0 for section in self.sections}
        
        # Track exit status
        self.exit_status = {}
        for exit_id, exit_data in self.exits.items():
            self.exit_status[exit_id] = {
                "capacity": exit_data["capacity"],
                "current_flow": 0,
                "status": exit_data.get("status", "open"),
                "utilization": 0.0
            }
    
    def check_capacity(self) -> Tuple[bool, str]:
        """Check if stadium is at capacity"""
        utilization = (self.current_occupancy / self.capacity) * 100
        
        if utilization >= 100:
            return False, f"Stadium at full capacity ({self.capacity})"
        elif utilization >= 90:
            return True, f"WARNING: {utilization:.1f}% capacity - near full"
        else:
            return True, f"Capacity OK: {utilization:.1f}%"
    
    def update_occupancy(self, active_agents: int, agents_by_section: Dict[str, int]):
        """Update current occupancy metrics"""
        self.current_occupancy = active_agents
        self.section_occupancy = agents_by_section
    
    def update_exit_flow(self, exit_densities: Dict[str, float]):
        """Update exit utilization based on density"""
        for exit_id, density in exit_densities.items():
            if exit_id in self.exit_status:
                capacity = self.exit_status[exit_id]["capacity"]
                self.exit_status[exit_id]["current_flow"] = density
                self.exit_status[exit_id]["utilization"] = min(100, (density / capacity) * 100)
    
    def get_exit_recommendations(self, node_densities: Dict[str, float], 
                                 danger_threshold: float = 4.0) -> List[Dict]:
        """Generate real-time exit management recommendations"""
        recommendations = []
        
        for exit_id, status in self.exit_status.items():
            density = node_densities.get(exit_id, 0)
            
            # Critical: Exit overloaded
            if density > danger_threshold:
                recommendations.append({
                    "priority": "CRITICAL",
                    "exit": exit_id,
                    "action": "CLOSE_TEMPORARILY",
                    "reason": f"Density {density:.2f} exceeds danger threshold {danger_threshold}",
                    "recommendation": f"Close {exit_id} for 60 seconds, reroute to alternative exits",
                    "color": "red"
                })
            
            # Warning: Exit approaching capacity
            elif density > danger_threshold * 0.75:
                recommendations.append({
                    "priority": "WARNING",
                    "exit": exit_id,
                    "action": "REDUCE_FLOW",
                    "reason": f"Density {density:.2f} approaching danger level",
                    "recommendation": f"Reduce inflow to {exit_id} by 30%, open additional exits",
                    "color": "orange"
                })
            
            # Info: Exit underutilized
            elif status["utilization"] < 30:
                recommendations.append({
                    "priority": "INFO",
                    "exit": exit_id,
                    "action": "INCREASE_SIGNAGE",
                    "reason": f"Only {status['utilization']:.1f}% utilized",
                    "recommendation": f"Direct more crowd to {exit_id} - has spare capacity",
                    "color": "blue"
                })
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations
    
    def get_crowd_spawn_for_pattern(self, pattern_name: str, 
                                     elapsed_time: float) -> Optional[int]:
        """
        Get number of agents to spawn based on arrival pattern
        Returns None if pattern not active at this time
        """
        if pattern_name not in self.arrival_patterns:
            return None
        
        pattern = self.arrival_patterns[pattern_name]
        rate = pattern.get("rate", 50)  # people per second
        duration = pattern.get("duration", 600)  # seconds
        
        # Check if pattern is active (simple implementation)
        # In production, you'd track pattern start times
        if elapsed_time < duration:
            return rate
        return None
    
    def get_stadium_status(self) -> Dict:
        """Get comprehensive stadium status"""
        return {
            "capacity": self.capacity,
            "current_occupancy": self.current_occupancy,
            "occupancy_percent": (self.current_occupancy / self.capacity) * 100,
            "section_occupancy": self.section_occupancy,
            "exits": self.exit_status,
            "status": "FULL" if self.current_occupancy >= self.capacity else "AVAILABLE"
        }
