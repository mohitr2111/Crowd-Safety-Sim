import uuid

from fastapi import APIRouter, HTTPException

try:
    from backend.models.schemas import SimulationRequest, SimulationStepRequest
    from backend.simulation.scenarios import SCENARIOS
    from backend.simulation.simulator import Simulator
    from backend import state
except ImportError:
    from models.schemas import SimulationRequest, SimulationStepRequest
    from simulation.scenarios import SCENARIOS
    from simulation.simulator import Simulator
    import state


router = APIRouter()


@router.post("/simulation/create")
def create_simulation(request: SimulationRequest):
    """Create a new simulation instance with continuous spawning"""
    try:
        if request.scenario not in SCENARIOS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown scenario. Available: {list(SCENARIOS.keys())}",
            )

        digital_twin = SCENARIOS[request.scenario]()
        simulator = Simulator(digital_twin, time_step=request.time_step)

        # Setup continuous spawning
        spawn_config = [config.dict() for config in request.spawn_config]

        # Calculate spawn duration based on total agents
        total_agents = sum(cfg["count"] for cfg in spawn_config)

        if total_agents < 1000:
            spawn_duration = 30.0
        elif total_agents < 5000:
            spawn_duration = 45.0
        else:
            spawn_duration = 60.0

        simulator.setup_continuous_spawn(spawn_config, spawn_duration)

        sim_id = str(uuid.uuid4())
        state.active_simulations[sim_id] = simulator

        initial_state = simulator.get_simulation_state()

        return {
            "simulation_id": sim_id,
            "message": f"Simulation created with {total_agents} agents spawning over {spawn_duration}s",
            "initial_state": initial_state,
        }

    except Exception as e:
        print(f"Error creating simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation/step")
def step_simulation(request: SimulationStepRequest):
    """Advance simulation by specified number of steps"""
    sim_id = request.simulation_id

    if sim_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = state.active_simulations[sim_id]

    try:
        states = []
        for _ in range(request.steps):
            state_step = simulator.step()
            states.append(state_step)

        return {
            "simulation_id": sim_id,
            "steps_executed": request.steps,
            "current_state": states[-1] if states else None,
            "history": states if request.steps > 1 else None,
        }

    except Exception as e:
        print(f"❌ Error in /simulation/step: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Simulation step failed: {str(e)}")


@router.get("/simulation/{simulation_id}/state")
def get_simulation_state(simulation_id: str):
    """Get current state of a simulation"""
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = state.active_simulations[simulation_id]
    return simulator.get_simulation_state()


@router.post("/simulation/{simulation_id}/reset")
def reset_simulation(simulation_id: str):
    """Reset simulation to initial state"""
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = state.active_simulations[simulation_id]
    simulator.reset()

    return {
        "simulation_id": simulation_id,
        "message": "Simulation reset successfully",
        "state": simulator.get_simulation_state(),
    }


@router.delete("/simulation/{simulation_id}")
def delete_simulation(simulation_id: str):
    """Delete a simulation instance"""
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    del state.active_simulations[simulation_id]

    return {"simulation_id": simulation_id, "message": "Simulation deleted successfully"}
