import numpy as np
import pickle
from typing import Dict, List, Tuple

class CrowdSafetyQLearning:
    """
    Q-Learning agent for optimal crowd control
    
    State: (node_id, density_bucket, inflow_bucket, exit_pressure_bucket)
    Actions: ["no_action", "reduce_inflow_25", "reduce_inflow_50", 
              "close_inflow", "reroute_to_alt_exit"]
    """
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, 
             epsilon=0.2):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        
        # Define action space (REORDERED by preference)
        self.actions = [
            "no_action",
            "reroute_to_alt_exit",  # FIRST CHOICE - redistribute load
            "reduce_inflow_25",     # Gentle slowdown
            "reduce_inflow_50",     # Moderate slowdown
            "close_inflow",         # LAST RESORT - creates upstream jams
        ]

        
        # Q-table: {state_hash: {action: q_value}}
        self.q_table = {}
        
        # Training history
        self.training_history = {
            "episodes": [],
            "total_rewards": [],
            "danger_violations": [],
            "max_densities": []
        }
    
    def discretize_state(self, node_data: Dict) -> str:
        """
        Convert continuous node data into discrete state
        IMPROVED: More granular states for better learning
        """
        density = node_data["density"]
        node_type = node_data["type"]
        
        # Calculate occupancy ratio from density and area
        area_m2 = node_data.get("area_m2", 100)
        capacity = node_data.get("capacity", 100)
        
        # Estimate current occupancy from density
        # density = people / area, so people = density * area
        estimated_occupancy = density * area_m2
        occupancy_ratio = estimated_occupancy / max(capacity, 1)
        
        # More granular density levels (6 levels instead of 3)
        if density < 1.5:
            density_level = "safe"
        elif density < 2.5:
            density_level = "low"
        elif density < 3.5:
            density_level = "moderate"
        elif density < 4.5:
            density_level = "warning"
        elif density < 5.5:
            density_level = "danger"
        else:
            density_level = "critical"
        
        # Occupancy level
        if occupancy_ratio < 0.4:
            occupancy_level = "low"
        elif occupancy_ratio < 0.7:
            occupancy_level = "medium"
        else:
            occupancy_level = "high"
        
        # Create state hash with more detail
        state = f"{node_type}_{density_level}_{occupancy_level}"
        return state

    def get_q_value(self, state: str, action: str) -> float:
        """Get Q-value for state-action pair"""
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        return self.q_table[state][action]
    
    def choose_action(self, state: str, training: bool = True) -> str:
        """
        Choose action using epsilon-greedy policy
        
        Args:
            state: Current state hash
            training: If True, explore; if False, exploit only
        """
        if training and np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(self.actions)
        else:
            # Exploit: best known action
            if state not in self.q_table:
                self.q_table[state] = {a: 0.0 for a in self.actions}
            
            q_values = self.q_table[state]
            max_q = max(q_values.values())
            
            # Choose randomly among actions with max Q-value
            best_actions = [a for a, q in q_values.items() if q == max_q]
            return np.random.choice(best_actions)
    
    def update_q_value(self, state: str, action: str, reward: float, 
                       next_state: str):
        """
        Update Q-value using Q-learning update rule:
        Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        """
        current_q = self.get_q_value(state, action)
        
        # Get max Q-value for next state
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in self.actions}
        max_next_q = max(self.q_table[next_state].values())
        
        # Q-learning update
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def calculate_reward(self, sim_state: Dict) -> float:
        """
        Improved reward function - COMPATIBLE with trainer.py
        
        Trainer calls: reward = self.agent.calculate_reward(sim.get_simulation_state())
        So we only get sim_state, not prev_state/action/new_state
        """
        # Extract metrics from simulation state
        max_density = sim_state["stats"]["max_density_reached"]
        danger_count = len(sim_state["danger_zones"])
        agents_reached = sim_state["stats"]["agents_reached_goal"]
        total_agents = sim_state["stats"]["total_agents_spawned"]
        
        reward = 0.0
        
        # 1. SHARPER density penalties (quadratic!)
        if max_density > 6.0:
            reward -= 150  # Was -120, now even stronger
        elif max_density > 5.0:
            reward -= 80   # Was -60
        elif max_density > 4.5:
            reward -= 40   # Was -30
        elif max_density > 4.0:
            reward -= 20   # Was -15
        elif max_density > 3.5:
            reward += 10   # Still warning but acceptable
        elif max_density > 3.0:
            reward += 40   # Was +35, now higher reward
        elif max_density > 2.0:
            reward += 65   # Was +55
        else:
            reward += 90   # Was +75, reward perfect density more
        
        # 2. MUCH STRONGER violation penalty
        reward -= danger_count * 50  # Was 25, now DOUBLED
        
        # 3. Throughput reward (only if safe)
        if total_agents > 0:
            throughput_rate = agents_reached / total_agents
            if max_density < 3.5:  # Only reward throughput if safe
                reward += throughput_rate * 30  # Was 25
            else:
                reward += throughput_rate * 5  # Minimal reward if unsafe
        
        # 4. BIG BONUS for keeping density below danger threshold
        if max_density < 4.0:
            reward += 50  # Was 40, now bigger bonus
        
        # 5. BONUS for zero danger zones
        if danger_count == 0:
            reward += 45  # Was 35, now bigger bonus
        
        # 6. Penalize stagnation (agents not moving)
        active_agents = total_agents - agents_reached
        if active_agents > total_agents * 0.7 and sim_state["time"] > 30:
            reward -= 20  # Was -15, now stronger
        
        return reward

    def save_model(self, filepath: str):
        """Save Q-table to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'training_history': self.training_history
            }, f)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load Q-table from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.q_table = data['q_table']
            self.training_history = data['training_history']
        print(f"Model loaded from {filepath}")
    
    def get_action_explanation(self, state: str, action: str) -> str:
        """Generate human-readable explanation for action"""
        q_value = self.q_table.get(state, {}).get(action, 0.0)
        
        explanations = {
            "no_action": f"Situation under control. Monitoring density. (Confidence: {q_value:.2f})",
            "reduce_inflow_25": f"Moderate crowding detected. Slowing 25% of incoming traffic. (Confidence: {q_value:.2f})",
            "reduce_inflow_50": f"High density approaching. Cutting inflow by 50%. (Confidence: {q_value:.2f})",
            "close_inflow": f"DANGER: Critical density. Temporarily closing entry. (Confidence: {q_value:.2f})",
            "reroute_to_alt_exit": f"Optimizing flow. Redirecting crowd to less congested exits. (Confidence: {q_value:.2f})",
        }
        
        return explanations.get(action, f"Action: {action} (Confidence: {q_value:.2f})")
