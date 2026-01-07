import uuid

from fastapi import APIRouter, HTTPException

from app_state import active_simulations, load_scenario
from models.schemas import SimulationRequest, SimulationStepRequest
from rl.comparison import SimulationComparison
from rl.q_learning_agent import CrowdSafetyQLearning
from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator



router = APIRouter(prefix="/simulation")


@router.post("/create")  # 🆕 Remove response_model
def create_simulation(request: SimulationRequest):
    """Create a new simulation instance"""
    try:
        scenario_config = load_scenario(request.scenario)
        if scenario_config and "spawn_presets" in scenario_config:
            pass
    except FileNotFoundError:
        pass

    if request.scenario not in SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario. Available: {list(SCENARIOS.keys())}",
        )

    digital_twin = SCENARIOS[request.scenario]()
    simulator = Simulator(digital_twin, time_step=request.time_step)

    spawn_config = [config.dict() for config in request.spawn_config]
    simulator.spawn_agents_batch(spawn_config)

    sim_id = str(uuid.uuid4())
    active_simulations[sim_id] = simulator

    initial_state = simulator.get_simulation_state()

    # 🆕 Return dict directly without validation
    return {
        "simulation_id": sim_id,
        "message": f"Simulation created with {len(simulator.agents)} agents",
        "initial_state": initial_state,
    }

@router.get("/{simulation_id}/ai-actions")
def get_ai_actions(simulation_id: str):
    """Get all AI actions taken during simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]
    return {
        "simulation_id": simulation_id,
        "ai_actions": simulator.ai_actions,
        "stampede_prediction": simulator.stampede_prediction,
        "total_actions": len(simulator.ai_actions),
        "critical_actions": len([a for a in simulator.ai_actions if a['severity'] == 'CRITICAL'])
    }

# ✨ NEW ENDPOINT FOR CASE STUDIES
@router.get("/case-studies")
def get_case_studies():
    """Get historical stampede case studies"""
    import json
    try:
        with open('data/real_case_studies.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {
            "error": "Case studies file not found",
            "message": "Make sure real_case_studies.json is in backend/data/"
        }

# ✨ NEW ENDPOINT FOR SCENARIO BUILDER
@router.post("/scenario/create")
def create_custom_scenario(scenario_data: dict):
    """Create and save a custom scenario"""
    from Components.scenario_builder import ScenarioBuilder
    
    try:
        builder = ScenarioBuilder(
            name=scenario_data.get('name', 'Custom Scenario'),
            template=scenario_data.get('template', 'temple')
        )
        
        # Return scenario JSON
        return {
            "status": "success",
            "scenario": builder.to_dict(),
            "message": f"Scenario '{builder.name}' created"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/step")
def step_simulation(request: SimulationStepRequest):
    """
    Advance simulation by specified number of steps

    Example request:
    {
        "simulation_id": "uuid-here",
        "steps": 1
    }
    """
    sim_id = request.simulation_id

    if sim_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = active_simulations[sim_id]

    # Run simulation steps
    states = []
    for _ in range(request.steps):
        state = simulator.step()
        states.append(state)

    return {
        "simulation_id": sim_id,
        "steps_executed": request.steps,
        "current_state": states[-1] if states else None,
        "history": states if request.steps > 1 else None,
    }


@router.get("/{simulation_id}/state")
def get_simulation_state(simulation_id: str):
    """Get current state of a simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = active_simulations[simulation_id]
    return simulator.get_simulation_state()


@router.post("/{simulation_id}/reset")
def reset_simulation(simulation_id: str):
    """Reset simulation to initial state"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = active_simulations[simulation_id]
    simulator.reset()

    return {
        "simulation_id": simulation_id,
        "message": "Simulation reset successfully",
        "state": simulator.get_simulation_state(),
    }


@router.delete("/{simulation_id}")
def delete_simulation(simulation_id: str):
    """Delete a simulation instance"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    del active_simulations[simulation_id]

    return {"simulation_id": simulation_id, "message": "Simulation deleted successfully"}


@router.get("/{simulation_id}/graph")
def get_graph_structure(simulation_id: str):
    """Get digital twin graph structure for visualization"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = active_simulations[simulation_id]
    twin = simulator.digital_twin

    # Format graph for frontend visualization
    nodes = []
    for node_id, data in twin.node_data.items():
        nodes.append(
            {
                "id": node_id,
                "x": data["position"][0],
                "y": data["position"][1],
                "type": data["type"],
                "capacity": data["capacity"],
                "area_m2": data["area_m2"],
            }
        )

    edges = []
    for (from_node, to_node), data in twin.edge_data.items():
        edges.append(
            {
                "from": from_node,
                "to": to_node,
                "width": data["width_m"],
                "capacity": data["flow_capacity"],
            }
        )

    return {"nodes": nodes, "edges": edges}


@router.post("/compare")
def compare_simulations(request: SimulationRequest):
    """
    Run both baseline and RL-optimized simulations for comparison

    Returns side-by-side results with improvement metrics

    Example request:
    {
        "scenario": "stadium_exit",
        "spawn_config": [
            {"start": "zone_north", "goal": "exit_main", "count": 500, "type": "normal"}
        ],
        "time_step": 1.0
    }
    """
    # Load trained RL model
    agent = CrowdSafetyQLearning()
    try:
        agent.load_model("models/stadium_rl_model.pkl")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="RL model not found. Please train the model first by running: python train_model.py",
        )

    # Validate scenario
    if request.scenario not in SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario. Available: {list(SCENARIOS.keys())}",
        )

    # Create comparison
    comparison = SimulationComparison(request.scenario, agent)

    # Convert spawn config
    spawn_config = [config.dict() for config in request.spawn_config]
    num_agents = sum(c["count"] for c in spawn_config)

    print(f"Running comparison with {num_agents} agents...")

    # Run both simulations
    baseline = comparison.run_baseline(num_agents, spawn_config, max_steps=200)
    optimized = comparison.run_optimized(num_agents, spawn_config, max_steps=200)

    # Generate report
    report = comparison.generate_comparison_report(baseline, optimized)

    return {
        "scenario": request.scenario,
        "total_agents": num_agents,
        "baseline": report["baseline"],
        "optimized": report["optimized"],
        "improvements": report["improvements"],
        "sample_actions": report["actions_taken"][:10],  # First 10 actions
        "baseline_history": baseline.get("history", []),
        "optimized_history": optimized.get("history", []),
    }


# 🆕 ADD THIS NEW ENDPOINT - Stadium Status
@router.get("/{simulation_id}/stadium-status")
def get_stadium_status(simulation_id: str):
    """Get real-time stadium capacity and recommendations"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = active_simulations[simulation_id]
    state = simulator.get_simulation_state()

    # Debug: Print state structure
    print(f"📊 State keys: {state.keys()}")

    # Calculate node densities from state
    node_densities = {}

    # Access nodes data (might be under different key)
    nodes_data = state.get("nodes", {})

    for node_id, node_state in nodes_data.items():
        # Get node area from digital twin
        twin_node = simulator.digital_twin.node_data.get(node_id, {})
        area_m2 = twin_node.get("area_m2", 1)
        current_count = node_state.get("current_count", 0)

        # Correct density formula
        density = current_count / area_m2 if area_m2 > 0 else 0
        node_densities[node_id] = density

        # Debug high densities
        if density > 10:
            print(
                f"🚨 HIGH DENSITY: {node_id} = {density:.1f} p/m² ({current_count} people in {area_m2} m²)"
            )

    # Get active agents count
    total_agents = state.get("total_agents", 0)
    reached_goal = state.get("reached_goal", 0)
    active_agents = total_agents - reached_goal

    # Generate recommendations
    recommendations = []
    danger_threshold = 4.0
    warning_threshold = 3.0

    for node_id, density in node_densities.items():
        if density > danger_threshold:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "location": node_id.replace("_", " ").title(),
                    "action": "CLOSE_TEMPORARILY",
                    "reason": f"Density {density:.1f} p/m² exceeds danger threshold ({danger_threshold} p/m²)",
                    "recommendation": f"Close {node_id} for 60 seconds and reroute crowd to alternative paths",
                    "color": "red",
                }
            )
        elif density > warning_threshold:
            recommendations.append(
                {
                    "priority": "WARNING",
                    "location": node_id.replace("_", " ").title(),
                    "action": "REDUCE_FLOW",
                    "reason": f"Density {density:.1f} p/m² approaching danger level",
                    "recommendation": f"Reduce inflow to {node_id} by 30% and monitor closely",
                    "color": "orange",
                }
            )

    # Sort by density (highest first)
    recommendations.sort(key=lambda x: 0 if x["priority"] == "CRITICAL" else 1)

    # Stadium capacity status
    capacity = 10000
    occupancy_percent = (active_agents / capacity * 100) if capacity > 0 else 0

    return {
        "stadium_status": {
            "capacity": capacity,
            "current_occupancy": active_agents,
            "occupancy_percent": occupancy_percent,
            "status": "FULL" if active_agents >= capacity else "AVAILABLE",
        },
        "recommendations": recommendations[:5],  # Top 5
        "timestamp": state.get("time", 0),
        "debug": {
            "total_agents": total_agents,
            "reached_goal": reached_goal,
            "active_agents": active_agents,
            "max_density": max(node_densities.values()) if node_densities else 0,
        },
    }
