import numpy as np
import pickle
from typing import Dict, Any


class DensityControlQLearning:
    """A from-scratch Q-learning agent focused on minimizing density peaks.

    This does NOT depend on your existing rl/ code.

    Actions are intentionally generic and are applied by the trainer/runtime wrapper.
    """

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

        self.q: Dict[str, Dict[str, float]] = {}
        self.training_history = {
            'episodes': [],
            'reward': [],
            'final_current_max_density': [],
            'danger_zone_count': [],
        }

    def _ensure(self, s: str):
        if s not in self.q:
            self.q[s] = {a: 0.0 for a in self.actions}

    def state_from_node(self, node: Dict[str, Any]) -> str:
        d = float(node.get('density', 0.0))
        t = str(node.get('type', 'general'))

        if d < 1.5:
            b = 'S0'
        elif d < 2.5:
            b = 'S1'
        elif d < 3.5:
            b = 'S2'
        elif d < 4.0:
            b = 'S3'
        elif d < 4.5:
            b = 'S4'
        elif d < 5.5:
            b = 'S5'
        else:
            b = 'S6'

        return f'{t}:{b}'

    def act(self, state: str, training: bool = True) -> str:
        self._ensure(state)
        if training and np.random.random() < self.epsilon:
            return str(np.random.choice(self.actions))
        qv = self.q[state]
        m = max(qv.values())
        best = [a for a, v in qv.items() if v == m]
        return str(np.random.choice(best))

    def update(self, s: str, a: str, r: float, s2: str):
        self._ensure(s)
        self._ensure(s2)
        cur = self.q[s][a]
        nxt = max(self.q[s2].values())
        self.q[s][a] = float(cur + self.lr * (r + self.gamma * nxt - cur))

    def decay(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def reward(self, sim_state: Dict[str, Any]) -> float:
        nodes = sim_state.get('nodes', {}) or {}
        cur_max = 0.0
        sum_over = 0.0
        for _, nd in nodes.items():
            d = float(nd.get('density', 0.0))
            cur_max = max(cur_max, d)
            sum_over += max(0.0, d - self.target_max_density)

        danger_zones = sim_state.get('danger_zones', []) or []
        danger_count = len(danger_zones)

        # penalize exceeding target
        over = max(0.0, cur_max - self.target_max_density)
        r = 0.0
        r -= (over ** 2) * 250.0
        r -= (sum_over ** 2) * 15.0
        r -= danger_count * 120.0

        # mild bonus if comfortably below target
        if cur_max < (self.target_max_density - 0.5):
            r += 10.0

        return float(r)

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump({
                'q': self.q,
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
            }, f)

    def load(self, path: str):
        with open(path, 'rb') as f:
            d = pickle.load(f)
        self.q = d.get('q', {})
        self.training_history = d.get('training_history', self.training_history)
