from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator
from rl.q_learning_agent import CrowdSafetyQLearning
from typing import Dict, List
import json


class SimulationComparison:
    """Compare baseline vs RL-optimized simulations"""
    
    def __init__(self, scenario_name: str, rl_agent: CrowdSafetyQLearning = None):
        self.scenario_name = scenario_name
        self.rl_agent = rl_agent
    
    def run_baseline(self, num_agents: int, spawn_config: List[Dict], 
                 max_steps: int = 200) -> Dict:  # Increased to 200

        """Run simulation WITHOUT RL optimization"""
        sim = Simulator(SCENARIOS[self.scenario_name](), time_step=1.0)
        sim.spawn_agents_batch(spawn_config)
        
        history = []
        for step in range(max_steps):
            state = sim.step()
            history.append({
                "time": state["time"],
                "max_density": state["stats"]["max_density_reached"],
                "active_agents": len(state["agents"]),
                "danger_zones": len(state["danger_zones"])
            })
            
            if len(state["agents"]) == 0:
                break
        
        final_state = sim.get_simulation_state()
        
        return {
            "type": "baseline",
            "final_stats": final_state["stats"],
            "history": history,
            "total_time": final_state["time"],
            "evacuation_time": final_state["time"],
            "max_density_reached": final_state["stats"]["max_density_reached"],
            "danger_violations": final_state["stats"]["danger_violations"],
            "agents_reached_goal": final_state["stats"]["agents_reached_goal"]
        }
    
    def run_optimized(self, num_agents: int, spawn_config: List[Dict], 
                      max_steps: int = 200) -> Dict:
        """Run simulation WITH RL optimization"""
        if not self.rl_agent:
            raise ValueError("RL agent not provided")
        
        sim = Simulator(SCENARIOS[self.scenario_name](), time_step=1.0)
        sim.spawn_agents_batch(spawn_config)
        
        history = []
        actions_taken = []
        
        for step in range(max_steps):
            current_state = sim.get_simulation_state()
            
            # Apply RL actions
            for node_id, node_data in current_state["nodes"].items():
                if node_data["density"] > 1.5:
                    state_hash = self.rl_agent.discretize_state(node_data)
                    action = self.rl_agent.choose_action(state_hash, training=False)
                    
                    if action != "no_action":
                        # Apply action
                        self._apply_action(sim, node_id, action)
                        actions_taken.append({
                            "time": current_state["time"],
                            "node": node_id,
                            "density": node_data["density"],
                            "action": action,
                            "explanation": self.rl_agent.get_action_explanation(state_hash, action)
                        })
            
            state = sim.step()
            history.append({
                "time": state["time"],
                "max_density": state["stats"]["max_density_reached"],
                "active_agents": len(state["agents"]),
                "danger_zones": len(state["danger_zones"])
            })
            
            if len(state["agents"]) == 0:
                break
        
        final_state = sim.get_simulation_state()
        
        return {
            "type": "rl_optimized",
            "final_stats": final_state["stats"],
            "history": history,
            "actions_taken": actions_taken,
            "total_time": final_state["time"],
            "evacuation_time": final_state["time"],
            "max_density_reached": final_state["stats"]["max_density_reached"],
            "danger_violations": final_state["stats"]["danger_violations"],
            "agents_reached_goal": final_state["stats"]["agents_reached_goal"]
        }
    
    def _apply_action(self, sim: Simulator, node_id: str, action: str):
        """Apply RL action (same as trainer)"""
        if action == "no_action":
            pass
        elif action == "reduce_inflow_25":
            affected_count = 0
            target_count = max(1, len(sim.agents) * 0.25)
            for agent in sim.agents.values():
                if agent.get_next_node() == node_id:
                    agent.wait_time += 1.0
                    affected_count += 1
                    if affected_count >= target_count:
                        break
        elif action == "reduce_inflow_50":
            affected_count = 0
            target_count = max(1, len(sim.agents) * 0.5)
            for agent in sim.agents.values():
                if agent.get_next_node() == node_id:
                    agent.wait_time += 2.0
                    affected_count += 1
                    if affected_count >= target_count:
                        break
        elif action == "close_inflow":
            for agent in sim.agents.values():
                if agent.get_next_node() == node_id:
                    agent.wait_time += 5.0
        elif action == "reroute_to_alt_exit":
            for agent in sim.agents.values():
                if node_id in (agent.path or []):
                    exit_nodes = [n for n, data in sim.digital_twin.node_data.items() 
                                 if data["type"] == "exit" and n != agent.goal_node]
                    if exit_nodes:
                        alt_exit = min(exit_nodes, 
                                      key=lambda n: sim.digital_twin.node_data[n]["density"])
                        alt_path = sim.digital_twin.get_shortest_path(agent.current_node, alt_exit)
                        if alt_path:
                            agent.set_path(alt_path)
                            agent.goal_node = alt_exit
    
    def generate_comparison_report(self, baseline_result: Dict, 
                                   optimized_result: Dict) -> Dict:
        """Generate detailed comparison metrics"""
        
        # Calculate improvements
        density_improvement = (
            (baseline_result["max_density_reached"] - 
             optimized_result["max_density_reached"]) / 
            baseline_result["max_density_reached"] * 100
        )
        
        violation_reduction = (
            baseline_result["danger_violations"] - 
            optimized_result["danger_violations"]
        )
        
        return {
            "baseline": {
                "max_density": baseline_result["max_density_reached"],
                "danger_violations": baseline_result["danger_violations"],
                "evacuation_time": baseline_result["evacuation_time"],
                "agents_reached": baseline_result["agents_reached_goal"]
            },
            "optimized": {
                "max_density": optimized_result["max_density_reached"],
                "danger_violations": optimized_result["danger_violations"],
                "evacuation_time": optimized_result["evacuation_time"],
                "agents_reached": optimized_result["agents_reached_goal"]
            },
            "improvements": {
                "density_reduction_percent": density_improvement,
                "danger_violations_prevented": violation_reduction,
                "time_difference": optimized_result["evacuation_time"] - baseline_result["evacuation_time"]
            },
            "actions_taken": optimized_result.get("actions_taken", [])
        }
    
    def save_report(self, report: Dict, filename: str = "comparison_report.json"):
        """Save comparison report to file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Comparison report saved to {filename}")
