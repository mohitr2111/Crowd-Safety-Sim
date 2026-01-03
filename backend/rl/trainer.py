from typing import Dict, List, Tuple
from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator
from rl.q_learning_agent import CrowdSafetyQLearning
import numpy as np

class RLTrainer:
    """Train RL agent using simulation"""
    
    def __init__(self, scenario_name: str, agent: CrowdSafetyQLearning):
        self.scenario_name = scenario_name
        self.agent = agent
        self.digital_twin = SCENARIOS[scenario_name]()
    
    def train_episode(self, num_agents: int, max_steps: int = 50) -> Dict:
        """Run one training episode"""
        # Create fresh simulator
        sim = Simulator(SCENARIOS[self.scenario_name](), time_step=1.0)
        
        # Spawn agents
        spawn_config = self._generate_spawn_config(num_agents)
        sim.spawn_agents_batch(spawn_config)
        
        episode_reward = 0
        states_actions = []  # For learning after episode
        
        for step in range(max_steps):
            # Get current state
            current_state = sim.get_simulation_state()
            
            # For each high-risk node, choose action
            for node_id, node_data in current_state["nodes"].items():
                if node_data["density"] > 2.5:  # Only act on moderate+ density
                    state_hash = self.agent.discretize_state(node_data)
                    action = self.agent.choose_action(state_hash, training=True)
                    
                    # Apply action to simulation
                    self._apply_action(sim, node_id, action)
                    
                    states_actions.append((state_hash, action))
            
            # Step simulation forward
            sim.step()
            
            # Calculate reward for this step
            reward = self.agent.calculate_reward(sim.get_simulation_state())
            episode_reward += reward
            
            # Update Q-values (online learning)
            if len(states_actions) > 0:
                for state, action in states_actions[-5:]:  # Last 5 actions
                    next_state_data = sim.get_simulation_state()["nodes"]
                    # Use aggregate state for next_state
                    avg_density = np.mean([n["density"] for n in next_state_data.values()])
                    next_state_hash = f"aggregate_{int(avg_density)}"
                    
                    self.agent.update_q_value(state, action, reward, next_state_hash)
            
            # Stop if all agents reached goal
            if len(current_state["agents"]) == 0:
                break
        
        # Get final stats
        final_state = sim.get_simulation_state()
        
        return {
            "episode_reward": episode_reward,
            "max_density": final_state["stats"]["max_density_reached"],
            "danger_violations": final_state["stats"]["danger_violations"],
            "agents_reached": final_state["stats"]["agents_reached_goal"]
        }
    
    def _apply_action(self, sim: Simulator, node_id: str, action: str):
        """Apply RL action to simulation (BALANCED)"""
        if action == "no_action":
            pass
        
        elif action == "reduce_inflow_25":
            # Slow down 30% of agents (balanced)
            affected_count = 0
            target_count = max(1, len(sim.agents) * 0.3)
            for agent in sim.agents.values():
                if agent.get_next_node() == node_id:
                    agent.wait_time += 2.0  # Moderate delay
                    affected_count += 1
                    if affected_count >= target_count:
                        break
        
        elif action == "reduce_inflow_50":
            # Slow down 50% of agents
            affected_count = 0
            target_count = max(1, len(sim.agents) * 0.5)
            for agent in sim.agents.values():
                if agent.get_next_node() == node_id:
                    agent.wait_time += 3.0  # Moderate-high delay
                    affected_count += 1
                    if affected_count >= target_count:
                        break
        
        elif action == "close_inflow":
            # Stop 80% of agents (not 100% - too harsh)
            affected_count = 0
            target_count = max(1, len(sim.agents) * 0.8)
            for agent in sim.agents.values():
                if agent.get_next_node() == node_id:
                    agent.wait_time += 6.0  # Strong delay
                    affected_count += 1
                    if affected_count >= target_count:
                        break
        
        elif action == "reroute_to_alt_exit":
            # Reroute agents intelligently
            rerouted_count = 0
            for agent in sim.agents.values():
                # Only reroute agents heading TO this node or currently in path
                if (agent.get_next_node() == node_id or node_id in (agent.path or [])):
                    # Find all exit nodes
                    exit_nodes = [n for n, data in sim.digital_twin.node_data.items() 
                                if data["type"] == "exit" and n != agent.goal_node]
                    
                    if exit_nodes:
                        # Pick least crowded exit
                        alt_exit = min(exit_nodes, 
                                    key=lambda n: sim.digital_twin.node_data[n]["density"])
                        
                        # Only reroute if alternative is less crowded
                        current_exit_density = sim.digital_twin.node_data.get(agent.goal_node, {}).get("density", 999)
                        alt_exit_density = sim.digital_twin.node_data[alt_exit]["density"]
                        
                        if alt_exit_density < current_exit_density - 0.5:
                            alt_path = sim.digital_twin.get_shortest_path(agent.current_node, alt_exit)
                            if alt_path:
                                agent.set_path(alt_path)
                                agent.goal_node = alt_exit
                                rerouted_count += 1
                                
                                # Limit rerouting (30% of agents max)
                                if rerouted_count >= len(sim.agents) * 0.3:
                                    break


    
    def _generate_spawn_config(self, num_agents: int) -> List[Dict]:
        """Generate varied spawn configurations"""
        # For stadium: FORCE most agents through main exit (creates pressure)
        if self.scenario_name == "stadium_exit":
            return [
                {"start": "zone_north", "goal": "exit_main", 
                "count": int(num_agents * 0.5), "type": "normal"},  # Was 0.4 - now MORE go to main
                {"start": "zone_south", "goal": "exit_main", 
                "count": int(num_agents * 0.3), "type": "family"},  # Same
                {"start": "zone_east", "goal": "exit_main",  # Changed from exit_side_1
                "count": int(num_agents * 0.1), "type": "rushing"},
                {"start": "zone_west", "goal": "exit_side_2", 
                "count": int(num_agents * 0.1), "type": "elderly"}
            ]
        elif self.scenario_name == "railway_station":
            return [
                {"start": "entry_main", "goal": "exit_east", 
                 "count": int(num_agents * 0.6), "type": "normal"},
                {"start": "entry_side", "goal": "exit_east", 
                 "count": int(num_agents * 0.4), "type": "rushing"}
            ]
        return []
    
    def train(self, num_episodes: int = 100, agent_range: Tuple[int, int] = (200, 500)):
        """Train agent over multiple episodes"""
        print(f"Starting training: {num_episodes} episodes")
        
        for episode in range(num_episodes):
            # Vary number of agents for robustness
            num_agents = np.random.randint(agent_range[0], agent_range[1])
            
            result = self.train_episode(num_agents)
            
            # Log progress
            self.agent.training_history["episodes"].append(episode)
            self.agent.training_history["total_rewards"].append(result["episode_reward"])
            self.agent.training_history["danger_violations"].append(result["danger_violations"])
            self.agent.training_history["max_densities"].append(result["max_density"])
            
            if episode % 10 == 0:
                print(f"Episode {episode}/{num_episodes}")
                print(f"  Reward: {result['episode_reward']:.2f}")
                print(f"  Max Density: {result['max_density']:.2f}")
                print(f"  Danger Violations: {result['danger_violations']}")
                print()
        
        print("Training complete!")
        return self.agent.training_history
