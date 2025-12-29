import random
from typing import Dict, List, Optional

from simulation.digital_twin import DigitalTwin
from simulation.agent import Agent

class Simulator:
    """Main simulation engine for crowd dynamics with continuous agent spawning"""
    
    def __init__(self, digital_twin: DigitalTwin, time_step: float = 1.0):
        self.twin = digital_twin
        self.time_step = time_step
        self.current_time = 0.0
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        
        # ✅ NEW: Spawn queue for continuous arrival
        self.spawn_queue = []  # List of (spawn_time, start_node, goal_node, agent_type)
        self.spawn_rate = {}   # Dict of {start_node: agents_per_second}
        
        # Simulation statistics
        self.stats = {
            "total_agents_spawned": 0,
            "agents_reached_goal": 0,
            "total_wait_time": 0,
            "max_density_reached": 0.0,
            "danger_violations": 0
        }
    
    def spawn_agent(self, start_node: str, goal_node: str, 
                   agent_type: str = "normal") -> Agent:
        """Create a new agent in the simulation"""
        agent = Agent(self.next_agent_id, start_node, goal_node, agent_type)
        
        # Calculate initial path
        path = self.twin.get_shortest_path(start_node, goal_node)
        if path:
            agent.set_path(path)
        
        self.agents[self.next_agent_id] = agent
        self.next_agent_id += 1
        self.stats["total_agents_spawned"] += 1
        
        return agent
    
    def setup_continuous_spawn(self, spawn_config: List[Dict], spawn_duration: float = 60.0):
        """
        ✅ NEW: Setup continuous agent spawning over time
        
        Args:
            spawn_config: List of spawn configurations
            spawn_duration: Time period over which to spawn agents (seconds)
        
        Example:
            [
                {"start": "zone_north", "goal": "exit_main", "count": 2000, "type": "normal"},
                {"start": "zone_south", "goal": "exit_main", "count": 1500, "type": "family"}
            ]
            
        This will spawn 2000 agents from zone_north gradually over spawn_duration seconds
        """
        self.spawn_queue = []
        
        for config in spawn_config:
            count = config["count"]
            start_node = config["start"]
            goal_node = config["goal"]
            agent_type = config.get("type", "normal")
            
            # Calculate spawn rate (agents per second)
            spawn_rate = count / spawn_duration
            
            # Generate spawn times with some randomness for realism
            spawn_times = []
            for i in range(count):
                # Base time: evenly distributed over duration
                base_time = (i / count) * spawn_duration
                
                # Add random jitter (±20% of interval)
                jitter = random.uniform(-0.2, 0.2) * (spawn_duration / count)
                spawn_time = max(0, base_time + jitter)
                
                spawn_times.append(spawn_time)
            
            # Sort spawn times
            spawn_times.sort()
            
            # Add to spawn queue
            for spawn_time in spawn_times:
                self.spawn_queue.append({
                    "time": spawn_time,
                    "start": start_node,
                    "goal": goal_node,
                    "type": agent_type
                })
        
        # Sort entire queue by time
        self.spawn_queue.sort(key=lambda x: x["time"])
        
        print(f"✅ Continuous spawn setup: {len(self.spawn_queue)} agents over {spawn_duration}s")
        print(f"   Spawn rate: ~{len(self.spawn_queue)/spawn_duration:.1f} agents/second")
    
    def spawn_agents_batch(self, spawn_config: List[Dict]):
        """
        Spawn multiple agents from configuration (OLD METHOD - still supported)
        Use setup_continuous_spawn() for gradual spawning
        """
        for config in spawn_config:
            for _ in range(config["count"]):
                agent_type = config.get("type", "normal")
                self.spawn_agent(config["start"], config["goal"], agent_type)
    
    def process_spawn_queue(self):
        """✅ NEW: Spawn agents from queue based on current time"""
        agents_spawned_this_step = 0
        
        while self.spawn_queue and self.spawn_queue[0]["time"] <= self.current_time:
            spawn_event = self.spawn_queue.pop(0)
            self.spawn_agent(
                spawn_event["start"],
                spawn_event["goal"],
                spawn_event["type"]
            )
            agents_spawned_this_step += 1
        
        if agents_spawned_this_step > 0:
            print(f"  t={self.current_time:.1f}s: Spawned {agents_spawned_this_step} agents (queue: {len(self.spawn_queue)} remaining)")
    
    def update_node_occupancy(self):
        """Count agents in each node and update digital twin"""
        node_counts = {node: 0 for node in self.twin.node_data.keys()}
        
        for agent in self.agents.values():
            if agent.current_node in node_counts:
                node_counts[agent.current_node] += 1
        
        # Update digital twin with new counts
        for node_id, count in node_counts.items():
            self.twin.update_node_count(node_id, count)
    
    def step(self) -> Dict:
        """
        Execute one simulation time step
        Returns current state snapshot
        """
        # ✅ NEW: Process spawn queue first
        self.process_spawn_queue()
        
        # Update occupancy counts
        self.update_node_occupancy()
        
        # Move agents
        agents_to_remove = []
        
        for agent_id, agent in self.agents.items():
            if agent.has_reached_goal:
                agents_to_remove.append(agent_id)
                self.stats["agents_reached_goal"] += 1
                continue
            
            # Get current node density
            current_density = self.twin.node_data[agent.current_node]["density"]
            
            # Check if agent should wait due to crowding
            if agent.should_wait(current_density):
                agent.wait_time += self.time_step
                self.stats["total_wait_time"] += self.time_step
                continue
            
            # Check if agent needs rerouting
            if agent.needs_rerouting(current_density):
                # Try to find alternative path
                new_path = self.twin.get_shortest_path(
                    agent.current_node,
                    agent.goal_node
                )
                if new_path and new_path != agent.path:
                    agent.set_path(new_path)
            
            # Attempt to move (with realistic delays)
            next_node = agent.get_next_node()
            if next_node:
                next_density = self.twin.node_data[next_node]["density"]
                
                # If next node is crowded, slow down movement
                if next_density > 3.0:
                    # High density: 50% chance to move
                    if random.random() < 0.5:
                        agent.move_to_next_node()
                elif next_density > 2.0:
                    # Moderate density: 75% chance to move
                    if random.random() < 0.75:
                        agent.move_to_next_node()
                else:
                    # Low density: always move
                    agent.move_to_next_node()
            else:
                agent.move_to_next_node()
            
            agent.update(self.time_step)
        
        # Remove agents that reached goal
        for agent_id in agents_to_remove:
            del self.agents[agent_id]
        
        # Update statistics
        state = self.twin.get_state_snapshot()
        if state["max_density"] > self.stats["max_density_reached"]:
            self.stats["max_density_reached"] = state["max_density"]
        
        if state["danger_count"] > 0:
            self.stats["danger_violations"] += 1
        
        self.current_time += self.time_step
        
        return self.get_simulation_state()
    
    def run_simulation(self, num_steps: int) -> List[Dict]:
        """Run simulation for specified number of steps"""
        history = []
        for _ in range(num_steps):
            state = self.step()
            history.append(state)
        return history
    
    def get_simulation_state(self) -> Dict:
        """Get complete current state for visualization/API"""
        twin_state = self.twin.get_state_snapshot()
        
        # Convert edge tuple keys to strings for JSON/Pydantic serialization
        edges_serialized = {
            f"{from_node}->{to_node}": data
            for (from_node, to_node), data in twin_state["edges"].items()
        }
        
        return {
            "time": self.current_time,
            "nodes": twin_state["nodes"],
            "edges": edges_serialized,
            "agents": {
                agent_id: {
                    "current_node": agent.current_node,
                    "goal_node": agent.goal_node,
                    "type": agent.agent_type,
                    "wait_time": agent.wait_time,
                    "reached_goal": agent.has_reached_goal
                }
                for agent_id, agent in self.agents.items()
            },
            "stats": self.stats.copy(),
            "danger_zones": self.twin.get_danger_zones(),
            # ✅ NEW: Include spawn queue info
            "pending_spawns": len(self.spawn_queue),
            "total_agents": len(self.agents),
            "reached_goal": self.stats["agents_reached_goal"]
        }
    
    def reset(self):
        """Reset simulation to initial state"""
        self.agents.clear()
        self.current_time = 0.0
        self.next_agent_id = 0
        self.spawn_queue = []  # ✅ NEW: Clear spawn queue
        
        self.stats = {
            "total_agents_spawned": 0,
            "agents_reached_goal": 0,
            "total_wait_time": 0,
            "max_density_reached": 0.0,
            "danger_violations": 0
        }
        
        # Reset all node counts
        for node_id in self.twin.node_data.keys():
            self.twin.update_node_count(node_id, 0)
