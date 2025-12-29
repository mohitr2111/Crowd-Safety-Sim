from simulation.scenarios import SCENARIOS

# Test stadium scenario
stadium = SCENARIOS["stadium_exit"]()
print(f"Stadium graph has {stadium.graph.number_of_nodes()} nodes")
print(f"Stadium graph has {stadium.graph.number_of_edges()} edges")

# Simulate some occupancy
stadium.update_node_count("zone_north", 850)  # Overcrowded!
stadium.update_node_count("concourse", 600)   # Warning level

snapshot = stadium.get_state_snapshot()
print(f"\nDanger zones: {stadium.get_danger_zones()}")
print(f"Max density: {snapshot['max_density']:.2f} people/m²")

# Test pathfinding
path = stadium.get_shortest_path("zone_north", "exit_main")
print(f"Path from north to main exit: {path}")
