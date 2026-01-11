"""
Trigger-Aware Policy (Sub-Phase 2.5)

Extends DensityControlQLearning with trigger-type conditioning.
Same density pattern can produce different recommendations based on emergency type.

Features:
- Separate Q-tables per trigger type
- Trigger-conditioned action selection
- Transfer learning from base policy
- Explainable trigger-specific reasoning
"""

import numpy as np
import pickle
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from Components.trigger_system import TriggerType


@dataclass
class TriggerContext:
    """Context about active triggers for policy conditioning"""
    active_trigger_type: Optional[TriggerType] = None
    trigger_severity: float = 0.0
    affected_zones: List[str] = None
    time_since_trigger: float = 0.0
    
    def __post_init__(self):
        if self.affected_zones is None:
            self.affected_zones = []


class TriggerAwareQLearning:
    """
    Q-learning agent with trigger-type conditioning.
    
    Q(s, a) becomes Q(s, trigger_type, a)
    Same density pattern → different action based on emergency type.
    
    IMPORTANT: This is still ADVISORY ONLY. Recommendations require
    human approval for execution.
    """
    
    # Trigger-specific action preferences (prior knowledge)
    TRIGGER_ACTION_PREFERENCES = {
        TriggerType.EXTERNAL_EXPLOSION: {
            "preferred": ["REROUTE", "CLOSE_INFLOW"],
            "avoid": ["NOOP"],
            "reason": "Evacuate away from danger zone"
        },
        TriggerType.GATE_MALFUNCTION: {
            "preferred": ["REROUTE", "THROTTLE_50"],
            "avoid": ["CLOSE_INFLOW"],
            "reason": "Redirect to alternate exits"
        },
        TriggerType.FALSE_ALARM: {
            "preferred": ["THROTTLE_25", "THROTTLE_50"],
            "avoid": [],
            "reason": "Controlled slowdown to prevent surge"
        },
        TriggerType.WEATHER_CHANGE: {
            "preferred": ["REROUTE"],
            "avoid": ["CLOSE_INFLOW"],
            "reason": "Redirect to covered areas"
        },
        TriggerType.INFRASTRUCTURE_FAILURE: {
            "preferred": ["CLOSE_INFLOW", "REROUTE"],
            "avoid": ["NOOP"],
            "reason": "Clear affected zone immediately"
        },
        TriggerType.PANIC_CHAIN_REACTION: {
            "preferred": ["THROTTLE_25", "REROUTE"],
            "avoid": ["CLOSE_INFLOW"],  # May worsen panic
            "reason": "Calm gradual intervention"
        }
    }
    
    def __init__(
        self,
        learning_rate: float = 0.15,
        discount_factor: float = 0.95,
        epsilon: float = 0.8,
        epsilon_decay: float = 0.985,
        min_epsilon: float = 0.05,
        target_max_density: float = 4.0,
    ):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.target_max_density = target_max_density
        
        self.actions = [
            'NOOP',
            'REROUTE',
            'THROTTLE_25',
            'THROTTLE_50',
            'CLOSE_INFLOW',
        ]
        
        # Base Q-table (no trigger / normal operation)
        self.q_base: Dict[str, Dict[str, float]] = {}
        
        # Trigger-specific Q-tables
        self.q_trigger: Dict[TriggerType, Dict[str, Dict[str, float]]] = {
            trigger_type: {} for trigger_type in TriggerType
        }
        
        # Training statistics
        self.training_history = {
            'episodes': [],
            'reward': [],
            'trigger_episodes': {t.value: 0 for t in TriggerType}
        }
        
        # Minimum samples before using trigger-specific Q
        self.min_trigger_samples = 50
        self.trigger_sample_counts: Dict[TriggerType, int] = {
            t: 0 for t in TriggerType
        }
    
    def _ensure_base(self, s: str):
        """Ensure base Q-table has state"""
        if s not in self.q_base:
            self.q_base[s] = {a: 0.0 for a in self.actions}
    
    def _ensure_trigger(self, s: str, trigger_type: TriggerType):
        """Ensure trigger Q-table has state"""
        if s not in self.q_trigger[trigger_type]:
            # Initialize from base Q-table (transfer learning)
            if s in self.q_base:
                self.q_trigger[trigger_type][s] = self.q_base[s].copy()
            else:
                self.q_trigger[trigger_type][s] = {a: 0.0 for a in self.actions}
    
    def state_from_observation(
        self,
        max_density: float,
        danger_count: int,
        avg_density: float,
        trigger_context: Optional[TriggerContext] = None
    ) -> str:
        """
        Convert observation to state string.
        
        State encoding includes density bucket and optional trigger info.
        """
        # Density bucket
        if max_density < 1.5:
            d_bucket = 'D0'
        elif max_density < 2.5:
            d_bucket = 'D1'
        elif max_density < 3.5:
            d_bucket = 'D2'
        elif max_density < 4.0:
            d_bucket = 'D3'
        elif max_density < 4.5:
            d_bucket = 'D4'
        elif max_density < 5.5:
            d_bucket = 'D5'
        else:
            d_bucket = 'D6'
        
        # Danger level
        if danger_count == 0:
            g_level = 'G0'
        elif danger_count <= 2:
            g_level = 'G1'
        else:
            g_level = 'G2'
        
        return f'{d_bucket}:{g_level}'
    
    def get_action(
        self,
        state: Tuple,
        trigger_context: Optional[TriggerContext] = None,
        explore: bool = True
    ) -> str:
        """
        Get action for state, conditioned on trigger type if active.
        
        Args:
            state: (max_density, danger_count, avg_density_bucket)
            trigger_context: Optional trigger information
            explore: Whether to use epsilon-greedy exploration
            
        Returns:
            Selected action string
        """
        max_density, danger_count, avg_bucket = state
        s = self.state_from_observation(max_density, danger_count, avg_bucket)
        
        # Determine which Q-table to use
        if trigger_context and trigger_context.active_trigger_type:
            trigger_type = trigger_context.active_trigger_type
            
            # Check if we have enough samples for trigger-specific
            if self.trigger_sample_counts[trigger_type] >= self.min_trigger_samples:
                self._ensure_trigger(s, trigger_type)
                q_table = self.q_trigger[trigger_type]
            else:
                # Fall back to base with trigger preference bias
                self._ensure_base(s)
                q_table = self._apply_trigger_bias(
                    self.q_base[s].copy(), trigger_type
                )
                return self._select_action(q_table, explore)
        else:
            self._ensure_base(s)
            q_table = self.q_base
        
        if s not in q_table:
            q_table[s] = {a: 0.0 for a in self.actions}
        
        return self._select_action(q_table[s], explore)
    
    def _apply_trigger_bias(
        self,
        q_values: Dict[str, float],
        trigger_type: TriggerType
    ) -> Dict[str, float]:
        """Apply trigger-specific bias to Q-values"""
        prefs = self.TRIGGER_ACTION_PREFERENCES.get(trigger_type, {})
        
        # Boost preferred actions
        for action in prefs.get("preferred", []):
            if action in q_values:
                q_values[action] += 2.0
        
        # Penalize avoided actions
        for action in prefs.get("avoid", []):
            if action in q_values:
                q_values[action] -= 3.0
        
        return q_values
    
    def _select_action(
        self,
        q_values: Dict[str, float],
        explore: bool
    ) -> str:
        """Select action using epsilon-greedy"""
        if explore and np.random.random() < self.epsilon:
            return str(np.random.choice(self.actions))
        
        max_q = max(q_values.values())
        best_actions = [a for a, v in q_values.items() if v == max_q]
        return str(np.random.choice(best_actions))
    
    def update(
        self,
        state: Tuple,
        action: str,
        reward: float,
        next_state: Tuple,
        trigger_context: Optional[TriggerContext] = None
    ):
        """
        Update Q-table with new experience.
        
        Updates both base table and trigger-specific table if applicable.
        """
        max_d, danger_c, avg_b = state
        next_max_d, next_danger_c, next_avg_b = next_state
        
        s = self.state_from_observation(max_d, danger_c, avg_b)
        s2 = self.state_from_observation(next_max_d, next_danger_c, next_avg_b)
        
        # Always update base Q-table
        self._ensure_base(s)
        self._ensure_base(s2)
        
        cur = self.q_base[s][action]
        nxt = max(self.q_base[s2].values())
        self.q_base[s][action] = float(cur + self.lr * (reward + self.gamma * nxt - cur))
        
        # Also update trigger-specific Q-table if trigger is active
        if trigger_context and trigger_context.active_trigger_type:
            trigger_type = trigger_context.active_trigger_type
            self.trigger_sample_counts[trigger_type] += 1
            
            self._ensure_trigger(s, trigger_type)
            self._ensure_trigger(s2, trigger_type)
            
            cur_t = self.q_trigger[trigger_type][s][action]
            nxt_t = max(self.q_trigger[trigger_type][s2].values())
            self.q_trigger[trigger_type][s][action] = float(
                cur_t + self.lr * (reward + self.gamma * nxt_t - cur_t)
            )
    
    def get_action_explanation(
        self,
        state: Tuple,
        action: str,
        trigger_context: Optional[TriggerContext] = None
    ) -> Dict:
        """
        Get explainable reasoning for an action.
        
        Returns human-readable explanation of why action was selected.
        """
        max_density, danger_count, _ = state
        
        explanation = {
            "action": action,
            "state": {
                "max_density": max_density,
                "danger_zones": danger_count
            },
            "trigger_aware": False,
            "reasoning": []
        }
        
        # Base reasoning
        if max_density < 2.5:
            explanation["reasoning"].append("Density is within safe limits")
        elif max_density < 4.0:
            explanation["reasoning"].append("Density is elevated - preventive action recommended")
        else:
            explanation["reasoning"].append("CRITICAL: Density exceeds danger threshold")
        
        if danger_count > 0:
            explanation["reasoning"].append(f"{danger_count} zone(s) in DANGER state")
        
        # Trigger-specific reasoning
        if trigger_context and trigger_context.active_trigger_type:
            explanation["trigger_aware"] = True
            trigger_type = trigger_context.active_trigger_type
            prefs = self.TRIGGER_ACTION_PREFERENCES.get(trigger_type, {})
            
            explanation["trigger_type"] = trigger_type.value
            explanation["trigger_severity"] = trigger_context.trigger_severity
            
            if prefs:
                explanation["reasoning"].append(
                    f"Emergency type '{trigger_type.value}': {prefs.get('reason', 'Trigger-specific response')}"
                )
                
                if action in prefs.get("preferred", []):
                    explanation["reasoning"].append(
                        f"Action '{action}' is preferred for this emergency type"
                    )
        
        # Action-specific explanation
        action_explanations = {
            "NOOP": "No intervention needed at this time",
            "THROTTLE_25": "Slow inflow by 25% to reduce buildup",
            "THROTTLE_50": "Slow inflow by 50% for moderate congestion",
            "CLOSE_INFLOW": "Stop inflow to critical zone",
            "REROUTE": "Redirect agents to alternative paths"
        }
        explanation["action_description"] = action_explanations.get(action, "Unknown action")
        
        return explanation
    
    def decay(self):
        """Decay exploration rate"""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
    
    def get_trigger_readiness(self) -> Dict[str, Dict]:
        """
        Get readiness status for each trigger type.
        
        Returns whether each trigger type has sufficient training data.
        """
        readiness = {}
        for trigger_type in TriggerType:
            count = self.trigger_sample_counts[trigger_type]
            ready = count >= self.min_trigger_samples
            
            readiness[trigger_type.value] = {
                "samples": count,
                "min_required": self.min_trigger_samples,
                "ready": ready,
                "states_learned": len(self.q_trigger[trigger_type])
            }
        
        return readiness
    
    def save(self, path: str):
        """Save policy to file"""
        data = {
            'q_base': self.q_base,
            'q_trigger': {
                t.value: q for t, q in self.q_trigger.items()
            },
            'trigger_sample_counts': {
                t.value: c for t, c in self.trigger_sample_counts.items()
            },
            'meta': {
                'lr': self.lr,
                'gamma': self.gamma,
                'epsilon': self.epsilon,
                'epsilon_decay': self.epsilon_decay,
                'min_epsilon': self.min_epsilon,
                'target_max_density': self.target_max_density,
                'actions': self.actions,
            },
            'training_history': self.training_history,
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, path: str):
        """Load policy from file"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.q_base = data.get('q_base', {})
        
        # Restore trigger Q-tables
        q_trigger_data = data.get('q_trigger', {})
        for trigger_type in TriggerType:
            if trigger_type.value in q_trigger_data:
                self.q_trigger[trigger_type] = q_trigger_data[trigger_type.value]
        
        # Restore sample counts
        counts_data = data.get('trigger_sample_counts', {})
        for trigger_type in TriggerType:
            if trigger_type.value in counts_data:
                self.trigger_sample_counts[trigger_type] = counts_data[trigger_type.value]
        
        self.training_history = data.get('training_history', self.training_history)


def upgrade_to_trigger_aware(base_agent) -> TriggerAwareQLearning:
    """
    Upgrade an existing DensityControlQLearning agent to trigger-aware.
    
    Transfers learned Q-values to the new agent's base table.
    """
    trigger_aware = TriggerAwareQLearning(
        learning_rate=base_agent.lr,
        discount_factor=base_agent.gamma,
        epsilon=base_agent.epsilon,
        epsilon_decay=base_agent.epsilon_decay,
        min_epsilon=base_agent.min_epsilon,
        target_max_density=base_agent.target_max_density,
    )
    
    # Transfer Q-table
    trigger_aware.q_base = base_agent.q.copy()
    
    return trigger_aware
