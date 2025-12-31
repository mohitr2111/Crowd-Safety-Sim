from typing import Dict, Any
from density_rl.policy import DensityControlQLearning


class DensityControllerRuntime:
    """Runtime wrapper to use a trained DensityControlQLearning inside a live Simulator loop."""

    def __init__(self, model_path: str, target_max_density: float = 4.0):
        self.agent = DensityControlQLearning(target_max_density=target_max_density)
        self.agent.load(model_path)
        # disable exploration in runtime
        self.agent.epsilon = 0.0

    def pick_actions(self, sim_state: Dict[str, Any], top_k: int = 3, min_density: float = 2.8):
        nodes = sim_state.get('nodes', {}) or {}
        densest = sorted(
            [(nid, float(nd.get('density', 0.0)), nd) for nid, nd in nodes.items()],
            key=lambda x: x[1], reverse=True
        )

        actions = []
        for nid, d, nd in densest[:top_k]:
            if d < min_density:
                continue
            s = self.agent.state_from_node(nd)
            a = self.agent.act(s, training=False)
            if a != 'NOOP':
                actions.append({'node': nid, 'density': d, 'action': a, 'state': s})
        return actions
