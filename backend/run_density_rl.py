from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator

from density_rl.policy import DensityControlQLearning
from density_rl.trainer import DensityRLTrainer


def main():
    # 1) Load trained model
    model_path = "density_rl/models/stadium_exit_density_rl.pkl"
    agent = DensityControlQLearning(target_max_density=4.0)
    agent.load(model_path)
    agent.epsilon = 0.0  # important: no exploration during usage

    # 2) Create simulator + spawn crowd (same pattern used during training)
    sim = Simulator(SCENARIOS["stadium_exit"](), time_step=1.0)
    trainer = DensityRLTrainer(scenario_name="stadium_exit", target_max_density=4.0)
    spawn_config = trainer.default_spawn_config(total_agents=1100)
    sim.spawn_agents_batch(spawn_config)

    # 3) Use the model each step
    max_steps = 200
    for _ in range(max_steps):
        state = sim.get_simulation_state()

        # Pick top congested nodes and apply actions
        nodes = state.get("nodes", {})
        densest = sorted(
            [(nid, nd.get("density", 0.0)) for nid, nd in nodes.items()],
            key=lambda x: x[1],
            reverse=True,
        )

        actions_used = 0
        for node_id, d in densest[:3]:
            if d < 2.8:
                continue
            s = agent.state_from_node(nodes[node_id])
            a = agent.act(s, training=False)
            if a != "NOOP":
                trainer.apply_action(sim, node_id, a)
                actions_used += 1

        # Step simulation
        sim.step()

        # Stop if evacuated
        if len(sim.get_simulation_state().get("agents", {})) == 0:
            break

    final_state = sim.get_simulation_state()
    print("Done. Stats:", final_state.get("stats"))


if __name__ == "__main__":
    main()
