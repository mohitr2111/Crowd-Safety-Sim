from density_rl.policy import DensityControlQLearning
from density_rl.trainer import DensityRLTrainer


def main():
    agent = DensityControlQLearning(
        learning_rate=0.15,
        discount_factor=0.95,
        epsilon=0.8,
        epsilon_decay=0.985,
        min_epsilon=0.05,
        target_max_density=4.0,
    )

    trainer = DensityRLTrainer(
        scenario_name='stadium_exit',
        target_max_density=4.0,
    )

    trainer.train(
        agent=agent,
        episodes=400,
        agent_range=(900, 1300),
        max_steps=80,
        max_actions_per_step=3,
    )

    out = 'density_rl/models/stadium_exit_density_rl.pkl'
    agent.save(out)
    print(f'Saved model: {out}')


if __name__ == '__main__':
    main()
