from pathlib import Path
import json

from fastapi import APIRouter

from simulation.scenarios import SCENARIOS


router = APIRouter()


@router.get("/scenarios")
async def get_scenarios():
    """Get available scenarios from both built-in and JSON files"""
    scenarios_dir = Path(__file__).parent.parent / "scenarios"
    scenarios = []

    # Load from JSON files if scenarios folder exists
    if scenarios_dir.exists():
        scenario_files = scenarios_dir.glob("*.json")

        for file in scenario_files:
            try:
                with open(file, "r") as f:
                    config = json.load(f)
                    scenarios.append(
                        {
                            "id": file.stem,
                            "name": config.get("name", file.stem),
                            "description": config.get("description", ""),
                            "source": "file",
                        }
                    )
            except Exception as e:
                print(f"Error loading {file}: {e}")

    # Add built-in scenarios
    for scenario_id in SCENARIOS.keys():
        # Check if not already added from file
        if not any(s["id"] == scenario_id for s in scenarios):
            descriptions = {
                "stadium_exit": "Stadium evacuation after event (600-1200 agents)",
                "railway_station": "Railway station during peak hours (150-400 agents)",
            }
            scenarios.append(
                {
                    "id": scenario_id,
                    "name": scenario_id.replace("_", " ").title(),
                    "description": descriptions.get(scenario_id, "Built-in scenario"),
                    "source": "built-in",
                }
            )

    return {"scenarios": scenarios}
