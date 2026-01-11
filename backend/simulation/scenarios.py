from simulation.digital_twin import DigitalTwin

def create_stadium_scenario() -> DigitalTwin:
    """Stadium exit scenario - REALISTIC BOTTLENECKS"""
    twin = DigitalTwin()
    
    # Main seating zones (large crowds)
    twin.add_area("zone_north", area_m2=600, capacity=1000, position=(50, 80), area_type="general")
    twin.add_area("zone_south", area_m2=600, capacity=1000, position=(50, 20), area_type="general")
    twin.add_area("zone_east", area_m2=500, capacity=800, position=(80, 50), area_type="general")
    twin.add_area("zone_west", area_m2=500, capacity=800, position=(20, 50), area_type="general")
    
    # Central concourse (MAJOR BOTTLENECK)
    twin.add_area("concourse", area_m2=150, capacity=200, position=(50, 50), area_type="waiting")  # Was 400/500
    
    # Exit gates (TINY - realistic doorways)
    twin.add_area("exit_main", area_m2=30, capacity=50, position=(50, 5), area_type="exit")  # Was 100/150
    twin.add_area("exit_side_1", area_m2=25, capacity=40, position=(10, 30), area_type="exit")  # Was 80/100
    twin.add_area("exit_side_2", area_m2=25, capacity=40, position=(90, 30), area_type="exit")  # Was 80/100
    
    # Narrow corridors to concourse
    twin.add_area("corridor_north", area_m2=40, capacity=60, position=(50, 65), area_type="general")
    twin.add_area("corridor_south", area_m2=40, capacity=60, position=(50, 35), area_type="general")
    
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
    """Railway station platform during peak hours - Multiple platforms with narrow foot-over-bridge"""
    twin = DigitalTwin()
    
    # Entry point
    twin.add_area("entry_main", area_m2=100, capacity=150, position=(50, 90), area_type="entry")
    
    # Main hall / ticketing area
    twin.add_area("main_hall", area_m2=300, capacity=400, position=(50, 75), area_type="waiting")
    
    # Foot-over-bridge (CRITICAL BOTTLENECK)
    twin.add_area("fob_west", area_m2=30, capacity=50, position=(20, 55), area_type="general")
    twin.add_area("fob_center", area_m2=40, capacity=60, position=(50, 55), area_type="general")
    twin.add_area("fob_east", area_m2=30, capacity=50, position=(80, 55), area_type="general")
    
    # Platforms (long, narrow)
    twin.add_area("platform_1", area_m2=200, capacity=300, position=(20, 30), area_type="waiting")
    twin.add_area("platform_2", area_m2=200, capacity=300, position=(50, 30), area_type="waiting")
    twin.add_area("platform_3", area_m2=200, capacity=300, position=(80, 30), area_type="waiting")
    
    # Exit points
    twin.add_area("exit_west", area_m2=40, capacity=60, position=(5, 50), area_type="exit")
    twin.add_area("exit_east", area_m2=40, capacity=60, position=(95, 50), area_type="exit")
    twin.add_area("exit_main", area_m2=50, capacity=80, position=(50, 10), area_type="exit")
    
    # Connect entry to main hall
    twin.add_path("entry_main", "main_hall", width_m=4, length_m=15, flow_capacity=80)
    
    # Connect main hall to foot-over-bridge
    twin.add_path("main_hall", "fob_west", width_m=2, length_m=20, flow_capacity=40)
    twin.add_path("main_hall", "fob_center", width_m=3, length_m=15, flow_capacity=60)
    twin.add_path("main_hall", "fob_east", width_m=2, length_m=20, flow_capacity=40)
    
    # Connect FOB sections
    twin.add_path("fob_west", "fob_center", width_m=2.5, length_m=30, flow_capacity=50)
    twin.add_path("fob_center", "fob_east", width_m=2.5, length_m=30, flow_capacity=50)
    
    # Connect FOB to platforms (staircases - narrow)
    twin.add_path("fob_west", "platform_1", width_m=1.5, length_m=25, flow_capacity=30)
    twin.add_path("fob_center", "platform_2", width_m=1.5, length_m=25, flow_capacity=30)
    twin.add_path("fob_east", "platform_3", width_m=1.5, length_m=25, flow_capacity=30)
    
    # Connect to exits
    twin.add_path("fob_west", "exit_west", width_m=2, length_m=15, flow_capacity=40)
    twin.add_path("fob_east", "exit_east", width_m=2, length_m=15, flow_capacity=40)
    twin.add_path("platform_2", "exit_main", width_m=2, length_m=20, flow_capacity=40)
    
    return twin


def create_festival_corridor_scenario() -> DigitalTwin:
    """Festival corridor with linear flow - Limited exits, high density at stages"""
    twin = DigitalTwin()
    
    # Entry gate
    twin.add_area("entry_gate", area_m2=80, capacity=120, position=(5, 50), area_type="entry")
    
    # Stage areas (high crowd density)
    twin.add_area("stage_1_area", area_m2=400, capacity=600, position=(25, 50), area_type="general")
    twin.add_area("stage_2_area", area_m2=400, capacity=600, position=(55, 50), area_type="general")
    twin.add_area("stage_3_area", area_m2=300, capacity=450, position=(80, 50), area_type="general")
    
    # Narrow corridors between stages (BOTTLENECKS)
    twin.add_area("corridor_1_2", area_m2=50, capacity=80, position=(40, 50), area_type="general")
    twin.add_area("corridor_2_3", area_m2=50, capacity=80, position=(67, 50), area_type="general")
    
    # Side paths for food/facilities
    twin.add_area("food_court", area_m2=150, capacity=200, position=(40, 75), area_type="waiting")
    twin.add_area("facilities", area_m2=100, capacity=150, position=(60, 25), area_type="waiting")
    
    # Emergency exits
    twin.add_area("exit_main", area_m2=60, capacity=100, position=(95, 50), area_type="exit")
    twin.add_area("exit_side_north", area_m2=30, capacity=50, position=(50, 90), area_type="exit")
    twin.add_area("exit_side_south", area_m2=30, capacity=50, position=(50, 10), area_type="exit")
    
    # Main flow: entry -> stages -> exit
    twin.add_path("entry_gate", "stage_1_area", width_m=4, length_m=20, flow_capacity=80)
    twin.add_path("stage_1_area", "corridor_1_2", width_m=2, length_m=15, flow_capacity=40)
    twin.add_path("corridor_1_2", "stage_2_area", width_m=2, length_m=15, flow_capacity=40)
    twin.add_path("stage_2_area", "corridor_2_3", width_m=2, length_m=12, flow_capacity=40)
    twin.add_path("corridor_2_3", "stage_3_area", width_m=2, length_m=12, flow_capacity=40)
    twin.add_path("stage_3_area", "exit_main", width_m=3, length_m=15, flow_capacity=60)
    
    # Side paths
    twin.add_path("corridor_1_2", "food_court", width_m=2, length_m=25, flow_capacity=40)
    twin.add_path("stage_2_area", "facilities", width_m=2, length_m=25, flow_capacity=40)
    
    # Emergency exit connections
    twin.add_path("food_court", "exit_side_north", width_m=2, length_m=15, flow_capacity=40)
    twin.add_path("facilities", "exit_side_south", width_m=2, length_m=15, flow_capacity=40)
    
    return twin


def create_temple_scenario() -> DigitalTwin:
    """Temple/pilgrimage scenario - Based on real stampede patterns (Mahakumbh, etc.)"""
    twin = DigitalTwin()
    
    # Multiple entry gates
    twin.add_area("entry_north", area_m2=60, capacity=100, position=(50, 95), area_type="entry")
    twin.add_area("entry_south", area_m2=60, capacity=100, position=(50, 5), area_type="entry")
    twin.add_area("entry_east", area_m2=40, capacity=60, position=(95, 50), area_type="entry")
    
    # Main pathway to sanctum
    twin.add_area("outer_corridor", area_m2=200, capacity=300, position=(50, 75), area_type="general")
    twin.add_area("inner_corridor", area_m2=100, capacity=150, position=(50, 55), area_type="general")
    
    # Sanctum area (very small, high desirability)
    twin.add_area("sanctum_queue", area_m2=40, capacity=60, position=(50, 40), area_type="waiting")
    twin.add_area("sanctum", area_m2=30, capacity=40, position=(50, 30), area_type="general")
    
    # Side areas
    twin.add_area("prasad_area", area_m2=80, capacity=120, position=(25, 50), area_type="waiting")
    twin.add_area("donation_hall", area_m2=80, capacity=120, position=(75, 50), area_type="waiting")
    
    # Exit path
    twin.add_area("exit_path", area_m2=100, capacity=150, position=(50, 15), area_type="general")
    twin.add_area("exit_main", area_m2=50, capacity=80, position=(30, 5), area_type="exit")
    twin.add_area("exit_side", area_m2=40, capacity=60, position=(70, 5), area_type="exit")
    
    # Paths from entries to outer corridor
    twin.add_path("entry_north", "outer_corridor", width_m=3, length_m=20, flow_capacity=60)
    twin.add_path("entry_south", "exit_path", width_m=2, length_m=10, flow_capacity=40)
    twin.add_path("entry_east", "donation_hall", width_m=2, length_m=45, flow_capacity=40)
    
    # Main devotee flow
    twin.add_path("outer_corridor", "inner_corridor", width_m=2, length_m=20, flow_capacity=40)
    twin.add_path("inner_corridor", "sanctum_queue", width_m=1.5, length_m=15, flow_capacity=30)
    twin.add_path("sanctum_queue", "sanctum", width_m=1, length_m=10, flow_capacity=20)
    twin.add_path("sanctum", "exit_path", width_m=1.5, length_m=15, flow_capacity=30)
    
    # Side area connections
    twin.add_path("outer_corridor", "prasad_area", width_m=2, length_m=25, flow_capacity=40)
    twin.add_path("outer_corridor", "donation_hall", width_m=2, length_m=25, flow_capacity=40)
    twin.add_path("prasad_area", "inner_corridor", width_m=1.5, length_m=20, flow_capacity=30)
    twin.add_path("donation_hall", "inner_corridor", width_m=1.5, length_m=20, flow_capacity=30)
    
    # Exit paths
    twin.add_path("exit_path", "exit_main", width_m=2.5, length_m=20, flow_capacity=50)
    twin.add_path("exit_path", "exit_side", width_m=2, length_m=20, flow_capacity=40)
    
    return twin


# Scenario metadata for multi-scenario training
SCENARIO_METADATA = {
    "stadium_exit": {
        "name": "Stadium Exit",
        "description": "Stadium evacuation after event (600-1200 agents)",
        "agent_range": (600, 1200),
        "danger_threshold": 4.0,
        "typical_bottlenecks": ["concourse", "exit_main"]
    },
    "railway_station": {
        "name": "Railway Platform",
        "description": "Railway station during peak hours (300-600 agents)",
        "agent_range": (300, 600),
        "danger_threshold": 3.5,
        "typical_bottlenecks": ["fob_center", "platform_2"]
    },
    "festival_corridor": {
        "name": "Festival Corridor",
        "description": "Festival with linear stages (400-800 agents)",
        "agent_range": (400, 800),
        "danger_threshold": 4.0,
        "typical_bottlenecks": ["corridor_1_2", "corridor_2_3"]
    },
    "temple": {
        "name": "Temple/Pilgrimage",
        "description": "Religious venue with sanctum (200-500 agents)",
        "agent_range": (200, 500),
        "danger_threshold": 3.0,
        "typical_bottlenecks": ["sanctum_queue", "inner_corridor"]
    }
}

# Add more scenarios as needed
SCENARIOS = {
    "stadium_exit": create_stadium_scenario,
    "railway_station": create_railway_station_scenario,
    "festival_corridor": create_festival_corridor_scenario,
    "temple": create_temple_scenario
}

