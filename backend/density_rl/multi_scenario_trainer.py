"""
Multi-Scenario RL Trainer (Sub-Phase 2.3)

Trains RL policy across multiple venue types for robustness.
Includes improved reward shaping for stability and reduced oscillation.

Features:
- Multi-scenario training (stadium, railway, festival, temple)
- Multi-seed evaluation for statistical robustness
- Improved reward function with stability bonus
- Trigger-aware training (Sub-Phase 2.5 foundation)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np
import random
from datetime import datetime

from simulation.scenarios import SCENARIOS, SCENARIO_METADATA
from simulation.simulator import Simulator
from density_rl.policy import DensityControlQLearning


@dataclass
class TrainingConfig:
    """Configuration for multi-scenario training"""
    scenarios: List[str] = field(default_factory=lambda: ["stadium_exit", "railway_station", "festival_corridor", "temple"])
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456, 789])
    episodes_per_scenario: int = 100
    max_steps_per_episode: int = 80
    max_actions_per_step: int = 3
    early_stop_threshold: float = 0.02  # Stop if improvement < 2%
    target_max_density: float = 4.0


@dataclass
class TrainingMetrics:
    """Metrics collected during training"""
    scenario: str
    seed: int
    episode: int
    mean_max_density: float
    max_density_reached: float
    danger_violations: int
    evacuation_progress: float  # % agents reached goal
    action_stability: float  # 0-1 (less oscillation = higher)
    reward_total: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "scenario": self.scenario,
            "seed": self.seed,
            "episode": self.episode,
            "mean_max_density": self.mean_max_density,
            "max_density_reached": self.max_density_reached,
            "danger_violations": self.danger_violations,
            "evacuation_progress": self.evacuation_progress,
            "action_stability": self.action_stability,
            "reward_total": self.reward_total,
            "timestamp": self.timestamp.isoformat()
        }


class ImprovedRewardShaper:
    """
    Improved reward computation for RL training.
    
    Focuses on:
    - Stability (penalizes oscillation)
    - Danger decay rate (proactive intervention)
    - Evacuation progress
    - Trigger-awareness bonus
    """
    
    def __init__(self, target_max_density: float = 4.0):
        self.target_max_density = target_max_density
        self.prev_action: Optional[str] = None
        self.action_history: List[str] = []
    
    def compute_reward(
        self,
        prev_state: Dict,
        curr_state: Dict,
        action: str,
        has_active_trigger: bool = False
    ) -> float:
        """
        Compute reward with improved shaping.
        
        Args:
            prev_state: Previous simulation state
            curr_state: Current simulation state
            action: Action taken
            has_active_trigger: Whether an emergency trigger is active
            
        Returns:
            Computed reward value
        """
        reward = 0.0
        
        # 1. Density improvement (core objective)
        prev_max = prev_state.get("max_density", 0)
        curr_max = curr_state.get("max_density", 0)
        density_delta = prev_max - curr_max
        reward += density_delta * 10.0
        
        # 2. Stay below danger threshold bonus
        if curr_max < self.target_max_density:
            reward += 1.0
        elif curr_max > 5.0:
            reward -= 2.0  # Penalty for very high density
        
        # 3. Stability bonus (penalize oscillation)
        self.action_history.append(action)
        if len(self.action_history) > 5:
            self.action_history = self.action_history[-5:]
        
        if self.prev_action is not None:
            if action == self.prev_action:
                reward += 0.5  # Bonus for consistent action
            else:
                reward -= 0.2  # Small penalty for switching
        
        # Calculate action stability
        if len(self.action_history) >= 3:
            switches = sum(1 for i in range(1, len(self.action_history)) 
                          if self.action_history[i] != self.action_history[i-1])
            stability_score = 1.0 - (switches / len(self.action_history))
            reward += stability_score * 0.3
        
        self.prev_action = action
        
        # 4. Danger zone reduction (proactive intervention)
        prev_danger = prev_state.get("danger_count", 0)
        curr_danger = curr_state.get("danger_count", 0)
        if curr_danger < prev_danger:
            reward += 2.0  # Bonus for reducing danger zones
        elif curr_danger > prev_danger:
            reward -= 1.5  # Penalty for increasing danger
        
        # 5. Evacuation progress
        prev_exited = prev_state.get("agents_exited", 0)
        curr_exited = curr_state.get("agents_exited", 0)
        evacuated = curr_exited - prev_exited
        reward += evacuated * 0.1
        
        # 6. Trigger-aware bonus (Phase 2.5)
        if has_active_trigger:
            # Extra reward for appropriate response during emergency
            if action != "NOOP" and curr_max < self.target_max_density:
                reward *= 1.5
            elif action == "NOOP" and curr_max > self.target_max_density:
                reward -= 1.0  # Penalty for inaction during emergency
        
        return reward
    
    def reset(self):
        """Reset state between episodes"""
        self.prev_action = None
        self.action_history = []


class MultiScenarioTrainer:
    """
    Trains RL policy across multiple venue scenarios for robustness.
    
    Uses identical physics across venues but varied topologies
    to ensure the agent generalizes well.
    """
    
    def __init__(self, config: Optional[TrainingConfig] = None):
        self.config = config or TrainingConfig()
        self.reward_shaper = ImprovedRewardShaper(self.config.target_max_density)
        self.training_history: List[TrainingMetrics] = []
        self.episode_rewards: Dict[str, List[float]] = {}
        
    def train(
        self,
        agent: DensityControlQLearning,
        verbose: bool = True
    ) -> Dict:
        """
        Train agent across all configured scenarios.
        
        Args:
            agent: The RL agent to train
            verbose: Whether to print progress
            
        Returns:
            Training summary with metrics
        """
        total_episodes = (len(self.config.scenarios) * 
                         len(self.config.seeds) * 
                         self.config.episodes_per_scenario)
        completed = 0
        
        for scenario_name in self.config.scenarios:
            if scenario_name not in SCENARIOS:
                if verbose:
                    print(f"Warning: Scenario '{scenario_name}' not found, skipping")
                continue
            
            self.episode_rewards[scenario_name] = []
            
            for seed in self.config.seeds:
                random.seed(seed)
                np.random.seed(seed)
                
                for episode in range(self.config.episodes_per_scenario):
                    metrics = self._train_episode(
                        agent, scenario_name, seed, episode
                    )
                    self.training_history.append(metrics)
                    self.episode_rewards[scenario_name].append(metrics.reward_total)
                    
                    completed += 1
                    if verbose and completed % 50 == 0:
                        print(f"Progress: {completed}/{total_episodes} episodes "
                              f"({100*completed/total_episodes:.1f}%)")
        
        return self._generate_summary()
    
    def _train_episode(
        self,
        agent: DensityControlQLearning,
        scenario_name: str,
        seed: int,
        episode: int
    ) -> TrainingMetrics:
        """Run a single training episode"""
        # Create simulator
        twin = SCENARIOS[scenario_name]()
        sim = Simulator(twin)
        
        # Get scenario-appropriate agent count
        metadata = SCENARIO_METADATA.get(scenario_name, {})
        agent_range = metadata.get("agent_range", (500, 1000))
        num_agents = random.randint(*agent_range)
        
        # Generate spawn configuration
        spawn_config = self._generate_spawn_config(sim, num_agents)
        sim.spawn_agents_batch(spawn_config)
        
        # Initialize paths
        for ag in sim.agents.values():
            path = sim.digital_twin.get_shortest_path(ag.current_node, ag.goal_node)
            if path:
                ag.set_path(path)
        
        # Reset reward shaper
        self.reward_shaper.reset()
        
        # Training loop
        total_reward = 0.0
        max_densities = []
        danger_violations = 0
        action_history = []
        
        for step in range(self.config.max_steps_per_episode):
            # Get current state
            state = self._get_state(sim)
            prev_state = {
                "max_density": state["max_density"],
                "danger_count": state["danger_count"],
                "agents_exited": state["agents_exited"]
            }
            
            # Track max density
            max_densities.append(state["max_density"])
            
            # Get node with highest density
            node_data = sim.digital_twin.node_data
            hotspot = max(node_data.items(), 
                         key=lambda x: x[1].get("density", 0), 
                         default=(None, {}))[0]
            
            if hotspot:
                for _ in range(self.config.max_actions_per_step):
                    # Select action
                    action = agent.get_action((
                        round(state["max_density"], 1),
                        state["danger_count"],
                        state["avg_density_bucket"]
                    ))
                    
                    if action and action != "NOOP":
                        self._apply_action(sim, hotspot, action)
                        action_history.append(action)
            
            # Step simulation
            sim.step()
            
            # Get new state
            state = self._get_state(sim)
            curr_state = {
                "max_density": state["max_density"],
                "danger_count": state["danger_count"],
                "agents_exited": state["agents_exited"]
            }
            
            # Compute reward
            last_action = action_history[-1] if action_history else "NOOP"
            reward = self.reward_shaper.compute_reward(
                prev_state, curr_state, last_action
            )
            total_reward += reward
            
            # Count violations
            if state["max_density"] > self.config.target_max_density:
                danger_violations += 1
            
            # Update agent Q-table
            if hotspot:
                agent.update(
                    state=(
                        round(prev_state["max_density"], 1),
                        prev_state["danger_count"],
                        state.get("avg_density_bucket", 0)
                    ),
                    action=last_action,
                    reward=reward,
                    next_state=(
                        round(curr_state["max_density"], 1),
                        curr_state["danger_count"],
                        state.get("avg_density_bucket", 0)
                    )
                )
        
        # Calculate metrics
        agents_reached = sum(1 for a in sim.agents.values() if a.has_reached_goal)
        evac_progress = agents_reached / len(sim.agents) if sim.agents else 0
        
        # Calculate action stability
        if len(action_history) >= 2:
            switches = sum(1 for i in range(1, len(action_history)) 
                          if action_history[i] != action_history[i-1])
            stability = 1.0 - (switches / len(action_history))
        else:
            stability = 1.0
        
        return TrainingMetrics(
            scenario=scenario_name,
            seed=seed,
            episode=episode,
            mean_max_density=np.mean(max_densities),
            max_density_reached=max(max_densities) if max_densities else 0,
            danger_violations=danger_violations,
            evacuation_progress=evac_progress,
            action_stability=stability,
            reward_total=total_reward
        )
    
    def _get_state(self, sim: Simulator) -> Dict:
        """Extract state from simulator"""
        snapshot = sim.digital_twin.get_state_snapshot()
        nodes = snapshot.get("nodes", {})
        
        densities = [n.get("density", 0) for n in nodes.values()]
        max_density = max(densities) if densities else 0
        avg_density = np.mean(densities) if densities else 0
        danger_count = sum(1 for n in nodes.values() 
                          if n.get("risk_level") == "DANGER")
        
        agents_exited = sum(1 for a in sim.agents.values() if a.has_reached_goal)
        
        return {
            "max_density": max_density,
            "avg_density": avg_density,
            "avg_density_bucket": int(avg_density),
            "danger_count": danger_count,
            "agents_exited": agents_exited,
            "total_agents": len(sim.agents)
        }
    
    def _generate_spawn_config(self, sim: Simulator, num_agents: int) -> List[Dict]:
        """Generate spawn configuration based on venue topology"""
        node_data = sim.digital_twin.node_data
        
        # Find entry and exit nodes
        entries = [n for n, d in node_data.items() if d.get("type") == "entry"]
        exits = [n for n, d in node_data.items() if d.get("type") == "exit"]
        
        # Fall back to general nodes if no entries/exits defined
        if not entries:
            entries = [n for n, d in node_data.items() 
                      if d.get("type") in ("general", "waiting")][:3]
        if not exits:
            exits = [n for n, d in node_data.items() 
                    if d.get("type") == "exit"] or list(node_data.keys())[-2:]
        
        if not entries or not exits:
            # Last resort: use any nodes
            all_nodes = list(node_data.keys())
            entries = all_nodes[:len(all_nodes)//2]
            exits = all_nodes[len(all_nodes)//2:]
        
        spawn_config = []
        agents_per_entry = num_agents // len(entries)
        remainder = num_agents % len(entries)
        
        for i, entry in enumerate(entries):
            count = agents_per_entry + (1 if i < remainder else 0)
            if count > 0:
                spawn_config.append({
                    "start": entry,
                    "goal": random.choice(exits),
                    "count": count,
                    "type": random.choice(["normal", "normal", "family", "rushing"])
                })
        
        return spawn_config
    
    def _apply_action(self, sim: Simulator, node_id: str, action: str):
        """Apply RL action to simulation"""
        current_time = getattr(sim, 'time', 0.0)
        
        if action == "NOOP":
            return
        
        # Get agents heading to or at the node
        target_agents = []
        for ag in sim.agents.values():
            if ag.has_reached_goal:
                continue
            next_node = ag.get_next_node()
            if next_node == node_id or ag.current_node == node_id:
                target_agents.append(ag)
        
        if action == "THROTTLE_25":
            for ag in target_agents[:len(target_agents)//4]:
                ag.block_until(current_time + 1.5)
                
        elif action == "THROTTLE_50":
            for ag in target_agents[:len(target_agents)//2]:
                ag.block_until(current_time + 2.5)
                
        elif action == "CLOSE_INFLOW":
            for ag in target_agents:
                ag.block_until(current_time + 5.0)
                
        elif action == "REROUTE":
            # Try to find alternative exits
            exits = [n for n, d in sim.digital_twin.node_data.items() 
                    if d.get("type") == "exit"]
            
            for ag in target_agents[:len(target_agents)//3]:
                if not exits:
                    continue
                alt_exit = random.choice(exits)
                path = sim.digital_twin.get_shortest_path(ag.current_node, alt_exit)
                if path:
                    ag.set_path(path)
                    ag.goal_node = alt_exit
    
    def _generate_summary(self) -> Dict:
        """Generate training summary"""
        summary = {
            "total_episodes": len(self.training_history),
            "scenarios_trained": list(self.episode_rewards.keys()),
            "per_scenario": {}
        }
        
        for scenario, rewards in self.episode_rewards.items():
            scenario_metrics = [m for m in self.training_history 
                               if m.scenario == scenario]
            
            summary["per_scenario"][scenario] = {
                "episodes": len(scenario_metrics),
                "mean_reward": np.mean(rewards),
                "final_reward": np.mean(rewards[-20:]) if len(rewards) >= 20 else np.mean(rewards),
                "mean_max_density": np.mean([m.max_density_reached for m in scenario_metrics]),
                "mean_violations": np.mean([m.danger_violations for m in scenario_metrics]),
                "mean_stability": np.mean([m.action_stability for m in scenario_metrics]),
                "mean_evac_progress": np.mean([m.evacuation_progress for m in scenario_metrics])
            }
        
        return summary
    
    def evaluate_multi_seed(
        self,
        agent: DensityControlQLearning,
        scenario_name: str,
        seeds: Optional[List[int]] = None,
        episodes_per_seed: int = 10
    ) -> Dict:
        """
        Evaluate trained agent with multiple seeds for statistical robustness.
        
        Returns confidence intervals and variance metrics.
        """
        seeds = seeds or self.config.seeds
        results = []
        
        for seed in seeds:
            random.seed(seed)
            np.random.seed(seed)
            
            for _ in range(episodes_per_seed):
                # Run evaluation episode (no learning)
                twin = SCENARIOS[scenario_name]()
                sim = Simulator(twin)
                
                metadata = SCENARIO_METADATA.get(scenario_name, {})
                agent_range = metadata.get("agent_range", (500, 1000))
                num_agents = random.randint(*agent_range)
                
                spawn_config = self._generate_spawn_config(sim, num_agents)
                sim.spawn_agents_batch(spawn_config)
                
                for ag in sim.agents.values():
                    path = sim.digital_twin.get_shortest_path(ag.current_node, ag.goal_node)
                    if path:
                        ag.set_path(path)
                
                max_densities = []
                danger_violations = 0
                
                for step in range(self.config.max_steps_per_episode):
                    state = self._get_state(sim)
                    max_densities.append(state["max_density"])
                    
                    if state["max_density"] > self.config.target_max_density:
                        danger_violations += 1
                    
                    # Apply actions based on policy (no exploration)
                    node_data = sim.digital_twin.node_data
                    hotspot = max(node_data.items(), 
                                 key=lambda x: x[1].get("density", 0), 
                                 default=(None, {}))[0]
                    
                    if hotspot:
                        action = agent.get_action((
                            round(state["max_density"], 1),
                            state["danger_count"],
                            state.get("avg_density_bucket", 0)
                        ), explore=False)  # No exploration
                        
                        if action and action != "NOOP":
                            self._apply_action(sim, hotspot, action)
                    
                    sim.step()
                
                agents_reached = sum(1 for a in sim.agents.values() if a.has_reached_goal)
                evac_progress = agents_reached / len(sim.agents) if sim.agents else 0
                
                results.append({
                    "seed": seed,
                    "max_density": max(max_densities) if max_densities else 0,
                    "mean_density": np.mean(max_densities),
                    "violations": danger_violations,
                    "evac_progress": evac_progress
                })
        
        # Compute statistics
        max_densities = [r["max_density"] for r in results]
        violations = [r["violations"] for r in results]
        evac_progress = [r["evac_progress"] for r in results]
        
        return {
            "scenario": scenario_name,
            "num_evaluations": len(results),
            "max_density": {
                "mean": np.mean(max_densities),
                "std": np.std(max_densities),
                "min": min(max_densities),
                "max": max(max_densities),
                "ci_95": (np.percentile(max_densities, 2.5), np.percentile(max_densities, 97.5))
            },
            "violations": {
                "mean": np.mean(violations),
                "std": np.std(violations),
                "min": min(violations),
                "max": max(violations)
            },
            "evacuation_progress": {
                "mean": np.mean(evac_progress),
                "std": np.std(evac_progress)
            }
        }
