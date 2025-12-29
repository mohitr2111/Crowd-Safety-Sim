from simulation.digital_twin import DigitalTwin

def create_stadium_scenario() -> DigitalTwin:
    """Stadium exit scenario - REALISTIC BOTTLENECKS"""
    twin = DigitalTwin()
    
    # Main seating zones (large crowds)
    twin.add_area("zone_north", area_m2=600, capacity=1000, position=(50, 80), area_type="general")
    twin.add_area("zone_south", area_m2=600, capacity=1000, position=(50, 20), area_type="general")
    twin.add_area("zone_east", area_m2=500, capacity=800, position=(80, 50), area_type="general")
    twin.add_area("zone_west", area_m2=500, capacity=800, position=(20, 50), area_type="general")
    
    # Larger concourse to handle crowd flow
    twin.add_area("concourse", area_m2=300, capacity=400, position=(50, 50), area_type="waiting")

    
    # Exit gates (TINY - realistic doorways)
    twin.add_area("exit_main", area_m2=30, capacity=50, position=(50, 5), area_type="exit")  # Was 100/150
    twin.add_area("exit_side_1", area_m2=25, capacity=40, position=(10, 30), area_type="exit")  # Was 80/100
    twin.add_area("exit_side_2", area_m2=25, capacity=40, position=(90, 30), area_type="exit")  # Was 80/100
    
    twin.add_area("corridor_north", area_m2=120, capacity=180, position=(50, 65), area_type="general")
    twin.add_area("corridor_south", area_m2=120, capacity=180, position=(50, 35), area_type="general")
    
    # Connect zones to corridors (narrow paths)
    twin.add_path("zone_north", "corridor_north", width_m=2, length_m=10, flow_capacity=60)
    twin.add_path("corridor_north", "concourse", width_m=2, length_m=10, flow_capacity=60)
    

    twin.add_path("zone_south", "corridor_south", width_m=2, length_m=10, flow_capacity=60)
    twin.add_path("corridor_south", "concourse", width_m=2, length_m=10, flow_capacity=60)
    
    twin.add_path("zone_east", "concourse", width_m=2, length_m=15, flow_capacity=50)
    twin.add_path("zone_west", "concourse", width_m=2, length_m=15, flow_capacity=50)
    
    # Connect concourse to exits (VERY NARROW)
    twin.add_path("concourse", "exit_main", width_m=1.5, length_m=20, flow_capacity=30)  # Was 100
    twin.add_path("concourse", "exit_side_1", width_m=1, length_m=15, flow_capacity=20)  # Was 50
    twin.add_path("concourse", "exit_side_2", width_m=1, length_m=15, flow_capacity=20)  # Was 50
    
    return twin


def create_railway_station_scenario() -> DigitalTwin:
    """Railway station platform during peak hours"""
    twin = DigitalTwin()
    
    # ... rest of railway scenario
    
    return twin

# Add more scenarios as needed
SCENARIOS = {
    "stadium_exit": create_stadium_scenario,
    "railway_station": create_railway_station_scenario
}
