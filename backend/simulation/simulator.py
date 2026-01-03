import random
from typing import Dict, List, Optional
from simulation.digital_twin import DigitalTwin
from simulation.agent import Agent
from Components.trigger_system import TriggerSystem, TriggerType
from Components.crowd_generator import CrowdGenerator
import json



class Simulator:
    def __init__(self, digital_twin, time_step=1.0):
        self.digital_twin = digital_twin
        self.agents = {}
        self.time = 0
        self.time_step = time_step
        self.next_agent_id = 0
        self.current_time = 0.0
        
        # Your new trigger system code...
        self.trigger_system = TriggerSystem()
        self.crowd_generator = CrowdGenerator()
        self.ai_actions = []
        self.stampede_prediction = None
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
        path = self.digital_twin.get_shortest_path(start_node, goal_node)

        if path:
            agent.set_path(path)
        
        self.agents[self.next_agent_id] = agent
        self.next_agent_id += 1
        self.stats["total_agents_spawned"] += 1
        
        return agent
    
    def spawn_agents_batch(self, spawn_config: List[Dict]):
        """
        Spawn multiple agents from configuration
        
        Example config:
        [
            {"start": "zone_north", "goal": "exit_main", "count": 50, "type": "normal"},
            {"start": "zone_south", "goal": "exit_side_1", "count": 30, "type": "family"}
        ]
        """
        for config in spawn_config:
            for _ in range(config["count"]):
                agent_type = config.get("type", "normal")
                self.spawn_agent(config["start"], config["goal"], agent_type)
    
    def update_node_occupancy(self):
        """Count agents in each node and update digital twin"""
        node_counts = {node: 0 for node in self.digital_twin.node_data.keys()}
        
        for agent in self.agents.values():
            if agent.current_node in node_counts:
                node_counts[agent.current_node] += 1
        
        # Update digital twin with new counts
        for node_id, count in node_counts.items():
            self.digital_twin.update_node_count(node_id, count)
    
    def step(self) -> Dict:
        """
        Execute one simulation time step
        Returns current state snapshot
        """
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
            current_density = self.digital_twin.node_data[agent.current_node]["density"]
            
            # Check if agent should wait due to crowding
            if agent.should_wait(current_density):
                agent.wait_time += self.time_step
                self.stats["total_wait_time"] += self.time_step
                continue
            
            # Check if agent needs rerouting
            if agent.needs_rerouting(current_density):
                # Try to find alternative path
                new_path = self.digital_twin.get_shortest_path(
                    agent.current_node, 
                    agent.goal_node
                )
                if new_path and new_path != agent.path:
                    agent.set_path(new_path)
            
            # Attempt to move (with realistic delays)
            next_node = agent.get_next_node()
            if next_node:
                next_density = self.digital_twin.node_data[next_node]["density"]
                
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
        state = self.digital_twin.get_state_snapshot()
        if state["max_density"] > self.stats["max_density_reached"]:
            self.stats["max_density_reached"] = state["max_density"]
        
        if state["danger_count"] > 0:
            self.stats["danger_violations"] += 1
        
        self.current_time += self.time_step
        self.time += self.time_step
    
        # Check for active triggers
        active_triggers = self.trigger_system.get_active_triggers(self.time)
        for trigger in active_triggers:
            effects = self.trigger_system.apply_trigger_effects(self, trigger)
            
            # Log AI action
            self.ai_actions.append({
                'time_seconds': self.time,
                'action': f"Detected {trigger.trigger_type.value}",
                'action_type': trigger.trigger_type.value,
                'zone': trigger.affected_zones[0] if trigger.affected_zones else 'global',
                'density': 0,
                'severity': 'CRITICAL' if trigger.severity > 0.7 else 'WARNING',
                'confidence': 0.85,
                'expected_effect': effects.get('actions_taken', []),
                'recommendation': self.trigger_system._get_recommendation(trigger.severity, trigger)
            })
        
        # Get stampede prediction
        self.stampede_prediction = self.trigger_system.get_stampede_prediction(self)
        
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
        twin_state = self.digital_twin.get_state_snapshot()
        
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
            "danger_zones": self.digital_twin.get_danger_zones()
        }

    
    def reset(self):
        """Reset simulation to initial state"""
        self.agents.clear()
        self.current_time = 0.0
        self.time = 0.0
        self.next_agent_id = 0
        self.stats = {
            "total_agents_spawned": 0,
            "agents_reached_goal": 0,
            "total_wait_time": 0,
            "max_density_reached": 0.0,
            "danger_violations": 0
        }
        # Reset all node counts
        for node_id in self.digital_twin.node_data.keys():
            self.digital_twin.update_node_count(node_id, 0)