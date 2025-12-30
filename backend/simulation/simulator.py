# backend/simulation/simulator.py

import random
from typing import Dict, List, Optional

from simulation.digital_twin import DigitalTwin
from simulation.agent import Agent
from ai.stampede_predictor import StampedePredictor, DensitySnapshot
from ai.intervention_engine import InterventionEngine
from events.cascade_effects import CascadeEngine

class Simulator:
    """Main simulation engine with integrated AI prediction and intervention"""
    
    def __init__(self, digital_twin: DigitalTwin, time_step: float = 1.0, ai_enabled: bool = True):
        self.twin = digital_twin
        self.time_step = time_step
        self.current_time = 0.0
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.ai_enabled = ai_enabled
        
        # ✅ NEW: Spawn queue for continuous arrival
        self.spawn_queue = []
        self.spawn_rate = {}
        
        # ✅ NEW: AI Systems Integration
        self.stampede_predictor = StampedePredictor(history_window=10)
        self.intervention_engine = InterventionEngine()
        self.active_predictions = {}  # {zone_id: StampedePrediction}
        self.active_interventions = []  # List of applied interventions
        
        # ✅ NEW: Cascade Detection
        # Build zone connections from graph
        connections = {}
        for (from_node, to_node) in self.twin.graph.edges():
            if from_node not in connections:
                connections[from_node] = []
            connections[from_node].append(to_node)
        self.cascade_engine = CascadeEngine(connections)
        
        # Simulation statistics
        self.stats = {
            "total_agents_spawned": 0,
            "agents_reached_goal": 0,
            "total_wait_time": 0,
            "max_density_reached": 0.0,
            "danger_violations": 0,
            "ai_interventions_count": 0,
            "stampedes_prevented": 0
        }
        
        # ✅ NEW: AI Action Log
        self.ai_action_log = []
    
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
        ✅ Setup continuous agent spawning over time
        
        Args:
            spawn_config: List of spawn configurations
                [{"start": "zone_north", "goal": "exit_main", "count": 2000, "type": "normal"}]
            spawn_duration: Time period over which to spawn agents (seconds)
        """
        self.spawn_queue = []
        
        for config in spawn_config:
            count = config["count"]
            start_node = config["start"]
            goal_node = config["goal"]
            agent_type = config.get("type", "normal")
            
            # Generate spawn times with randomness
            spawn_times = []
            for i in range(count):
                base_time = (i / count) * spawn_duration
                jitter = random.uniform(-0.2, 0.2) * (spawn_duration / count)
                spawn_time = max(0, base_time + jitter)
                spawn_times.append(spawn_time)
            
            spawn_times.sort()
            
            for spawn_time in spawn_times:
                self.spawn_queue.append({
                    "time": spawn_time,
                    "start": start_node,
                    "goal": goal_node,
                    "type": agent_type
                })
        
        self.spawn_queue.sort(key=lambda x: x["time"])
        
        print(f"✅ Continuous spawn setup: {len(self.spawn_queue)} agents over {spawn_duration}s")
        print(f"   Spawn rate: ~{len(self.spawn_queue)/spawn_duration:.1f} agents/second")
    
    def spawn_agents_batch(self, spawn_config: List[Dict]):
        """Spawn multiple agents immediately (batch mode)"""
        for config in spawn_config:
            for _ in range(config["count"]):
                agent_type = config.get("type", "normal")
                self.spawn_agent(config["start"], config["goal"], agent_type)
    
    def process_spawn_queue(self):
        """✅ Spawn agents from queue based on current time"""
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
            print(f"  t={self.current_time:.1f}s: Spawned {agents_spawned_this_step} agents")
    
    def update_node_occupancy(self):
        """Count agents in each node and update digital twin"""
        node_counts = {node: 0 for node in self.twin.node_data.keys()}
        
        for agent in self.agents.values():
            if agent.current_node in node_counts:
                node_counts[agent.current_node] += 1
        
        # Update digital twin with new counts
        for node_id, count in node_counts.items():
            self.twin.update_node_count(node_id, count)
    
    # ✅ NEW: Helper methods for AI systems
    def _calculate_flow_rate(self, node_id: str) -> float:
        """Calculate agents entering/leaving per time step"""
        # Count agents moving TO this node
        incoming = sum(1 for a in self.agents.values() 
                      if a.get_next_node() == node_id)
        
        # Count agents moving FROM this node
        outgoing = sum(1 for a in self.agents.values() 
                      if a.current_node == node_id and a.get_next_node() is not None)
        
        return incoming - outgoing
    
    def _calculate_avg_speed(self, node_id: str) -> float:
        """Calculate average agent speed in this node"""
        agents_in_node = [a for a in self.agents.values() 
                         if a.current_node == node_id]
        
        if not agents_in_node:
            return 1.0
        
        return sum(a.speed for a in agents_in_node) / len(agents_in_node)
    
    # ✅ NEW: Stampede Prediction System
    def _update_stampede_predictions(self):
        """Feed live data to stampede predictor and get predictions"""
        for node_id, node_data in self.twin.node_data.items():
            # Create density snapshot
            snapshot = DensitySnapshot(
                zone_id=node_id,
                timestamp=int(self.current_time),
                density=node_data["density"],
                agent_count=node_data["current_count"],
                area=node_data["area_m2"],
                flow_rate=self._calculate_flow_rate(node_id),
                avg_speed=self._calculate_avg_speed(node_id)
            )
            
            # Update predictor with new data
            self.stampede_predictor.update_data(snapshot)
            
            # Get prediction
            prediction = self.stampede_predictor.predict(node_id)
            
            if prediction:
                self.active_predictions[node_id] = prediction
                
                # Log high-risk predictions
                if prediction.risk_level.value in ["critical", "imminent"]:
                    print(f"⚠️  STAMPEDE RISK: {node_id} - {prediction.risk_level.value.upper()}")
                    print(f"    Probability: {prediction.probability*100:.0f}%")
                    print(f"    Current density: {prediction.current_density:.1f} p/m²")
    
    # ✅ NEW: Intervention System
    def _generate_and_apply_interventions(self):
        """Generate interventions from predictions and cascades, then apply critical ones"""
        new_interventions = []
        
        # Generate interventions from predictions
        for zone_id, prediction in self.active_predictions.items():
            if prediction.risk_level.value in ["critical", "imminent", "high"]:
                plan = self.intervention_engine.recommend_for_prediction(
                    prediction,
                    int(self.current_time)
                )
                
                if plan and plan.primary_option:
                    new_interventions.append(plan.primary_option)
        
        # Generate interventions from cascades
        active_cascades = self.cascade_engine.active_cascades
        for cascade in active_cascades:
            if cascade.current_severity > 0.6:  # High severity cascades
                plan = self.intervention_engine.recommend_for_cascade(
                    cascade,
                    int(self.current_time)
                )
                
                if plan and plan.primary_option:
                    new_interventions.append(plan.primary_option)
        
        # Auto-apply CRITICAL and IMMEDIATE interventions
        for intervention in new_interventions:
            if intervention.urgency.value in ["critical", "immediate"]:
                self._apply_intervention(intervention)
                self.active_interventions.append(intervention)
                self.stats["ai_interventions_count"] += 1
                
                # Log action
                self.ai_action_log.append({
                    "step": int(self.current_time),
                    "zone": intervention.target_zone,
                    "action": intervention.intervention_type.value,
                    "reason": intervention.action_description,
                    "severity": intervention.urgency.value
                })
                
                print(f"🤖 AI INTERVENTION: {intervention.intervention_type.value} on {intervention.target_zone}")
                print(f"   Reason: {intervention.action_description}")
    
    def _apply_intervention(self, intervention):
        """Execute an intervention action"""
        target = intervention.target_zone
        action = intervention.intervention_type.value
        
        if action == "close_entry":
            # Block the zone temporarily
            if target in self.twin.node_data:
                self.twin.node_data[target]["is_blocked"] = True
                self.twin.node_data[target]["block_expires"] = (
                    self.current_time + 60  # Block for 60 seconds
                )
                print(f"   ✅ Closed entry to {target}")
        
        elif action == "reroute_flow":
            # Reroute agents heading to this zone
            rerouted = 0
            for agent in self.agents.values():
                if agent.get_next_node() == target:
                    # Find alternative path
                    alt_path = self.twin.get_shortest_path(
                        agent.current_node,
                        agent.goal_node
                    )
                    if alt_path and alt_path != agent.path:
                        agent.set_path(alt_path)
                        rerouted += 1
            
            print(f"   ✅ Rerouted {rerouted} agents away from {target}")
        
        elif action == "open_exit":
            # Unblock an exit if it was blocked
            if target in self.twin.node_data:
                self.twin.node_data[target]["is_blocked"] = False
                print(f"   ✅ Opened emergency exit {target}")
        
        elif action == "reduce_inflow":
            # Slow down agent spawning to this zone
            # (Implementation depends on spawn queue logic)
            print(f"   ✅ Reduced inflow to {target}")
    
    # ✅ NEW: Cascade Detection
    def _update_cascade_detection(self):
        """Update cascade engine with current zone data"""
        zone_data = {}
        
        for node_id, node in self.twin.node_data.items():
            agents_in_node = [a for a in self.agents.values() 
                             if a.current_node == node_id]
            
            avg_speed = (sum(a.speed for a in agents_in_node) / len(agents_in_node)
                        if agents_in_node else 1.0)
            
            zone_data[node_id] = {
                "density": node["density"],
                "flow_rate": self._calculate_flow_rate(node_id),
                "speed": avg_speed,
                "agent_count": len(agents_in_node)
            }
        
        # Update cascades
        active_cascades = self.cascade_engine.update(
            int(self.current_time),
            zone_data
        )
        
        # Log new cascades
        for cascade in active_cascades:
            if cascade.initiated_at == int(self.current_time):
                print(f"🌊 CASCADE DETECTED: {cascade.cascade_type.value}")
                print(f"   Origin: {cascade.origin_zone}")
                print(f"   Affected zones: {len(cascade.affected_zones)}")
    
    # ✅ NEW: Auto-unblock expired nodes
    def _unblock_expired_nodes(self):
        """Unblock nodes whose block duration has expired"""
        for node_id, node_data in self.twin.node_data.items():
            if node_data.get("is_blocked") and node_data.get("block_expires"):
                if self.current_time >= node_data["block_expires"]:
                    node_data["is_blocked"] = False
                    node_data.pop("block_expires", None)
                    print(f"   ✅ Auto-unblocked {node_id}")
    
    def step(self) -> Dict:
        """
        ✅ UPDATED: Execute one simulation time step with full AI integration
        
        Returns:
            Current state snapshot with AI predictions
        """
        # 1. Process spawn queue
        self.process_spawn_queue()
        
        # 2. Update occupancy counts
        self.update_node_occupancy()
        
        # 3. ✅ NEW: Update stampede predictions
        self._update_stampede_predictions()
        
        # 4. ✅ NEW: Update cascade detection
        self._update_cascade_detection()
        
        # 5. ✅ NEW: Generate and apply AI interventions
        self._generate_and_apply_interventions()
        
        # 6. ✅ NEW: Unblock expired nodes
        self._unblock_expired_nodes()
        
        # 7. Move agents
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

            if self.ai_enabled:
                self._update_stampede_predictions()
    
            # 4. ✅ NEW: Update cascade detection (only if AI enabled)
            if self.ai_enabled:
                self._update_cascade_detection()
    
            # 5. ✅ NEW: Generate and apply AI interventions (only if AI enabled)
            if self.ai_enabled:
                self._generate_and_apply_interventions()
            
            # Check if agent needs rerouting
            if agent.needs_rerouting(current_density):
                new_path = self.twin.get_shortest_path(
                    agent.current_node,
                    agent.goal_node
                )
                if new_path and new_path != agent.path:
                    agent.set_path(new_path)
            
            # Attempt to move
            next_node = agent.get_next_node()
            if next_node:
                next_density = self.twin.node_data[next_node]["density"]
                
                # Slow down in high density
                if next_density > 3.0:
                    if random.random() < 0.5:
                        agent.move_to_next_node()
                elif next_density > 5.0:
                    if random.random() < 0.3:
                        agent.move_to_next_node()
                    else:
                        self.stats["danger_violations"] += 1
                else:
                    agent.move_to_next_node()
        
        # Remove completed agents
        for agent_id in agents_to_remove:
            del self.agents[agent_id]
        
        # Update max density stat
        current_max = max(
            (node["density"] for node in self.twin.node_data.values()),
            default=0.0
        )
        self.stats["max_density_reached"] = max(
            self.stats["max_density_reached"],
            current_max
        )
        
        # Advance time
        self.current_time += self.time_step
        
        # Return state snapshot
        return self.get_state()
    
    def get_state(self) -> Dict:
        """Get current simulation state with AI data"""
        return {
            "time": self.current_time,
            "agents": {
                agent_id: {
                    "current_node": agent.current_node,
                    "goal_node": agent.goal_node,
                    "type": agent.agent_type,
                    "wait_time": agent.wait_time
                }
                for agent_id, agent in self.agents.items()
            },
            "nodes": {
                node_id: {
                    "current_count": node_data["current_count"],
                    "density": node_data["density"]
                }
                for node_id, node_data in self.twin.node_data.items()
            },
            "stats": self.stats,
            "active_predictions": len(self.active_predictions),
            "active_cascades": len(self.cascade_engine.active_cascades),
            "ai_actions_taken": self.ai_action_log[-5:]  # Last 5 actions
        }
    
    def reset(self):
        """Reset simulation to initial state"""
        self.current_time = 0.0
        self.agents.clear()
        self.next_agent_id = 0
        self.spawn_queue.clear()
        self.active_predictions.clear()
        self.active_interventions.clear()
        self.ai_action_log.clear()
        
        # Reset cascade engine
        self.cascade_engine.active_cascades.clear()
        self.cascade_engine.cascade_history.clear()
        
        # Reset stats
        self.stats = {
            "total_agents_spawned": 0,
            "agents_reached_goal": 0,
            "total_wait_time": 0,
            "max_density_reached": 0.0,
            "danger_violations": 0,
            "ai_interventions_count": 0,
            "stampedes_prevented": 0
        }
        
        # Reset digital twin
        for node_data in self.twin.node_data.values():
            node_data["current_count"] = 0
            node_data["density"] = 0.0
            node_data["is_blocked"] = False

    def get_simulation_state(self):
        """Compatibility alias for routes that expect get_simulation_state()"""
        return self.get_state()

