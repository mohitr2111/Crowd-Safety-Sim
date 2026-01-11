from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def root():
    return {
        "message": "Crowd Safety Simulation API",
        "version": "1.0.0",
        "endpoints": {
            "scenarios": "/scenarios",
            "create_simulation": "/simulation/create",
            "step_simulation": "/simulation/step",
            "get_state": "/simulation/{simulation_id}/state",
            "compare": "/simulation/compare",
        },
    }
