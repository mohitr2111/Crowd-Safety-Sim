from typing import Dict, Any, List, Tuple
import numpy as np

from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator
from density_rl.policy import DensityControlQLearning


def _get_state(sim: Simulator) -> Dict[str, Any]:
    # your simulator uses get_simulation_state in some places and getsimulationstate in others
    if hasattr(sim, 'get_simulation_state'):
        return sim.get_simulation_state()
    return sim.getsimulationstate()


def _spawn_batch(sim: Simulator, spawn_config: List[Dict[str, Any]]):
    if hasattr(sim, 'spawn_agents_batch'):
        return sim.spawn_agents_batch(spawn_config)
    return sim.spawnagentsbatch(spawn_config)


def _agent_next_node(agent):
    if hasattr(agent, 'get_next_node'):
        return agent.get_next_node()
    if hasattr(agent, 'getnextnode'):
        return agent.getnextnode()
    return None


def _inc_wait(agent, dt: float):
    if hasattr(agent, 'wait_time'):
        agent.wait_time += dt
    else:
        agent.waittime += dt


def _agent_path(agent):
    return getattr(agent, 'path', None) or []


def _agent_current(agent):
    return getattr(agent, 'current_node', getattr(agent, 'currentnode', None))


def _agent_goal(agent):
    return getattr(agent, 'goal_node', getattr(agent, 'goalnode', None))


def _agent_set_goal(agent, goal: str):
    if hasattr(agent, 'goal_node'):
        agent.goal_node = goal
    else:
        agent.goalnode = goal


def _agent_set_path(agent, path):
    if hasattr(agent, 'set_path'):
        agent.set_path(path)
    else:
        agent.setpath(path)


def _twin_node_data(sim: Simulator):
    twin = sim.twin
    if hasattr(twin, 'node_data'):
        return twin.node_data
    return twin.nodedata


def _twin_shortest_path(sim: Simulator, start: str, end: str):
    twin = sim.twin
    if hasattr(twin, 'get_shortest_path'):
        return twin.get_shortest_path(start, end)
    return twin.getshortestpath(start, end)


class DensityRLTrainer:
    """Train DensityControlQLearning from scratch using your existing Simulator."""

    def __init__(
        self,
        scenario_name: str = 'stadium_exit',
        target_max_density: float = 4.0,
    ):
        self.scenario_name = scenario_name
        self.target_max_density = target_max_density

    def default_spawn_config(self, total_agents: int) -> List[Dict[str, Any]]:
        # uses your stadium_exit node IDs from scenarios.py
        if self.scenario_name == 'stadium_exit':
            return [
                {'start': 'zone_north', 'goal': 'exit_main', 'count': int(total_agents * 0.5), 'type': 'normal'},
                {'start': 'zone_south', 'goal': 'exit_main', 'count': int(total_agents * 0.3), 'type': 'family'},
                {'start': 'zone_east', 'goal': 'exit_main', 'count': int(total_agents * 0.1), 'type': 'rushing'},
                {'start': 'zone_west', 'goal': 'exit_side_2', 'count': int(total_agents * 0.1), 'type': 'elderly'},
            ]
        return []

    def train(
        self,
        agent: DensityControlQLearning,
        episodes: int = 400,
        agent_range: Tuple[int, int] = (900, 1300),
        max_steps: int = 80,
        max_actions_per_step: int = 3,
    ):
        for ep in range(episodes):
            total_agents = int(np.random.randint(agent_range[0], agent_range[1]))
            sim = Simulator(SCENARIOS[self.scenario_name](), time_step=1.0)
            _spawn_batch(sim, self.default_spawn_config(total_agents))

            ep_reward = 0.0
            for _ in range(max_steps):
                s = _get_state(sim)
                nodes = s.get('nodes', {}) or {}

                # act on the top-k densest nodes
                densest = sorted(
                    [(nid, float(nd.get('density', 0.0)), nd) for nid, nd in nodes.items()],
                    key=lambda x: x[1],
                    reverse=True,
                )

                transitions = []
                used = 0
                for nid, d, nd in densest:
                    if used >= max_actions_per_step:
                        break
                    if d < 2.8:
                        break

                    st = agent.state_from_node(nd)
                    a = agent.act(st, training=True)

                    # simple safety gating
                    if d < 3.3 and a in ('THROTTLE_50', 'CLOSE_INFLOW'):
                        a = 'THROTTLE_25'

                    if a != 'NOOP':
                        self.apply_action(sim, nid, a)
                        used += 1

                    transitions.append((nid, st, a))

                sim.step()
                s2 = _get_state(sim)
                r = agent.reward(s2) - used * 0.5
                ep_reward += r

                nodes2 = s2.get('nodes', {}) or {}
                for nid, st, a in transitions:
                    nd2 = nodes2.get(nid, {})
                    st2 = agent.state_from_node(nd2) if nd2 else 'terminal'
                    agent.update(st, a, r, st2)

                if len(s2.get('agents', {}) or {}) == 0:
                    break

            final = _get_state(sim)
            cur_max = 0.0
            for _, nd in (final.get('nodes', {}) or {}).items():
                cur_max = max(cur_max, float(nd.get('density', 0.0)))

            agent.training_history['episodes'].append(ep)
            agent.training_history['reward'].append(float(ep_reward))
            agent.training_history['final_current_max_density'].append(float(cur_max))
            agent.training_history['danger_zone_count'].append(len(final.get('danger_zones', []) or []))

            agent.decay()

            if ep % 25 == 0:
                print(f"ep={ep}/{episodes} eps={agent.epsilon:.3f} reward={ep_reward:.1f} curMax={cur_max:.2f}")

    def apply_action(self, sim: Simulator, node_id: str, action: str):
        agents_dict = getattr(sim, 'agents', {})
        agents = list(agents_dict.values()) if hasattr(agents_dict, 'values') else list(agents_dict)

        if action in ('THROTTLE_25', 'THROTTLE_50', 'CLOSE_INFLOW'):
            if action == 'THROTTLE_25':
                frac, dt = 0.25, 1.5
            elif action == 'THROTTLE_50':
                frac, dt = 0.50, 2.5
            else:
                frac, dt = 0.80, 5.0

            target = max(1, int(len(agents) * frac))
            affected = 0
            for ag in agents:
                if _agent_next_node(ag) == node_id:
                    _inc_wait(ag, dt)
                    affected += 1
                    if affected >= target:
                        break
            return

        if action == 'REROUTE':
            node_data = _twin_node_data(sim)
            exit_nodes = [n for n, d in node_data.items() if d.get('type') == 'exit']
            if not exit_nodes:
                return

            for ag in agents:
                path = _agent_path(ag)
                if node_id not in path and _agent_next_node(ag) != node_id:
                    continue

                current_goal = _agent_goal(ag)
                candidates = [e for e in exit_nodes if e != current_goal]
                if not candidates:
                    continue

                alt = min(candidates, key=lambda e: float(node_data.get(e, {}).get('density', 999)))
                start = _agent_current(ag)
                if not start:
                    continue

                alt_path = _twin_shortest_path(sim, start, alt)
                if alt_path:
                    _agent_set_path(ag, alt_path)
                    _agent_set_goal(ag, alt)
