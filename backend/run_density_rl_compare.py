import json
from typing import Dict, Any, List

from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator

from density_rl.policy import DensityControlQLearning
from density_rl.trainer import DensityRLTrainer


def _history_row(state: Dict[str, Any]) -> Dict[str, Any]:
    stats = state.get('stats', {}) or {}
    return {
        'time': state.get('time', 0),
        'max_density': stats.get('max_density_reached', stats.get('maxdensityreached', 0.0)),
        'active_agents': len(state.get('agents', {}) or {}),
        'danger_zones': len(state.get('danger_zones', []) or state.get('dangerzones', []) or []),
    }


def _final_metrics(state: Dict[str, Any]) -> Dict[str, Any]:
    stats = state.get('stats', {}) or {}
    return {
        'max_density': stats.get('max_density_reached', stats.get('maxdensityreached', 0.0)),
        'danger_violations': stats.get('danger_violations', stats.get('dangerviolations', 0)),
        'evacuation_time': state.get('time', 0),
        'agents_reached': stats.get('agents_reached_goal', stats.get('agentsreachedgoal', 0)),
    }


def _explain_action(action: str, q_val: float) -> str:
    mapping = {
        'NOOP': 'No intervention needed.',
        'REROUTE': 'Redistribute flow to a less crowded exit/path.',
        'THROTTLE_25': 'Slow a portion of inflow to prevent density spikes.',
        'THROTTLE_50': 'Strong inflow throttling to stop a rising peak.',
        'CLOSE_INFLOW': 'Emergency hold: temporarily stop most inflow to this node.',
    }
    base = mapping.get(action, f'Action: {action}')
    return f"{base} (Q={q_val:.2f})"


def run_baseline(total_agents: int = 1100, max_steps: int = 200) -> Dict[str, Any]:
    sim = Simulator(SCENARIOS['stadium_exit'](), time_step=1.0)
    trainer = DensityRLTrainer(scenario_name='stadium_exit', target_max_density=4.0)
    sim.spawn_agents_batch(trainer.default_spawn_config(total_agents))

    history: List[Dict[str, Any]] = []

    for _ in range(max_steps):
        state = sim.step()
        history.append(_history_row(state))
        if len(state.get('agents', {}) or {}) == 0:
            break

    final_state = sim.get_simulation_state()
    return {
        'final': _final_metrics(final_state),
        'history': history,
    }


def run_optimized(model_path: str, total_agents: int = 1100, max_steps: int = 200,
                  top_k: int = 3, min_density: float = 2.8) -> Dict[str, Any]:
    agent = DensityControlQLearning(target_max_density=4.0)
    agent.load(model_path)
    agent.epsilon = 0.0

    sim = Simulator(SCENARIOS['stadium_exit'](), time_step=1.0)
    trainer = DensityRLTrainer(scenario_name='stadium_exit', target_max_density=4.0)
    sim.spawn_agents_batch(trainer.default_spawn_config(total_agents))

    history: List[Dict[str, Any]] = []
    actions_taken: List[Dict[str, Any]] = []

    for _ in range(max_steps):
        pre = sim.get_simulation_state()
        nodes = pre.get('nodes', {}) or {}

        densest = sorted(
            [(nid, float(nd.get('density', 0.0)), nd) for nid, nd in nodes.items()],
            key=lambda x: x[1],
            reverse=True,
        )

        applied = 0
        for nid, d, nd in densest[:top_k]:
            if d < min_density:
                continue
            s = agent.state_from_node(nd)
            a = agent.act(s, training=False)
            if a == 'NOOP':
                continue
            # Q-value for explanation
            q_val = agent.q.get(s, {}).get(a, 0.0)
            trainer.apply_action(sim, nid, a)
            actions_taken.append({
                'time': pre.get('time', 0),
                'node': nid,
                'density': d,
                'action': a,
                'explanation': _explain_action(a, float(q_val)),
            })
            applied += 1
            if applied >= top_k:
                break

        state = sim.step()
        history.append(_history_row(state))
        if len(state.get('agents', {}) or {}) == 0:
            break

    final_state = sim.get_simulation_state()
    return {
        'final': _final_metrics(final_state),
        'history': history,
        'actions_taken': actions_taken,
    }


def make_report(model_path: str = 'density_rl/models/stadium_exit_density_rl.pkl', total_agents: int = 1100) -> Dict[str, Any]:
    baseline = run_baseline(total_agents=total_agents)
    optimized = run_optimized(model_path=model_path, total_agents=total_agents)

    b = baseline['final']
    o = optimized['final']

    density_reduction = 0.0
    if b['max_density']:
        density_reduction = (b['max_density'] - o['max_density']) / b['max_density'] * 100.0

    report = {
        'scenario': 'stadium_exit',
        'total_agents': total_agents,
        'baseline': b,
        'optimized': o,
        'improvements': {
            'density_reduction_percent': density_reduction,
            'danger_violations_prevented': b['danger_violations'] - o['danger_violations'],
            'time_difference': o['evacuation_time'] - b['evacuation_time'],
        },
        'sample_actions': optimized['actions_taken'][:12],
        'baseline_history': baseline['history'],
        'optimized_history': optimized['history'],
    }
    return report


def main():
    report = make_report(
        model_path='density_rl/models/stadium_exit_density_rl.pkl',
        total_agents=11000,
    )

    out_file = 'density_rl_comparison_report.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f'Saved: {out_file}')
    print('Baseline:', report['baseline'])
    print('Optimized:', report['optimized'])


if __name__ == '__main__':
    main()