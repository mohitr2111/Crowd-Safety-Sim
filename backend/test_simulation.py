from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator

# Create stadium scenario
stadium = SCENARIOS["stadium_exit"]()
sim = Simulator(stadium, time_step=1.0)

# Spawn crowd leaving stadium
spawn_config = [
    {"start": "zone_north", "goal": "exit_main", "count": 100, "type": "normal"},
    {"start": "zone_south", "goal": "exit_main", "count": 80, "type": "family"},
    {"start": "zone_east", "goal": "exit_side_1", "count": 50, "type": "rushing"},
    {"start": "zone_west", "goal": "exit_side_2", "count": 50, "type": "elderly"}
]

sim.spawn_agents_batch(spawn_config)

print(f"Spawned {len(sim.agents)} agents")
print("\n--- Running 30-second simulation ---\n")

# Run simulation for 30 steps (30 seconds)
for i in range(30):
    state = sim.step()
    if i % 5 == 0:  # Print every 5 seconds
        print(f"Time: {state['time']}s")
        print(f"  Active agents: {len(state['agents'])}")
        print(f"  Max density: {state['stats']['max_density_reached']:.2f} people/m²")
        print(f"  Danger violations: {state['stats']['danger_violations']}")
        print(f"  Agents reached goal: {state['stats']['agents_reached_goal']}")
        print()

print("Final Statistics:")
print(f"  Total spawned: {state['stats']['total_agents_spawned']}")
print(f"  Reached goal: {state['stats']['agents_reached_goal']}")
print(f"  Still active: {len(state['agents'])}")
print(f"  Max density: {state['stats']['max_density_reached']:.2f} people/m²")
