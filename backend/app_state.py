from pathlib import Path
from typing import Dict
import json

from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator


# Store active simulations (in production, use Redis/database)
active_simulations: Dict[str, Simulator] = {}


def load_scenario(scenario_name: str):
    """Load scenario configuration from JSON file"""
    scenario_path = Path(__file__).parent / "scenarios" / f"{scenario_name}.json"

    if not scenario_path.exists():
        # Fallback to built-in scenarios
        if scenario_name in SCENARIOS:
            return None  # Will use SCENARIOS dict
        raise FileNotFoundError(f"Scenario {scenario_name} not found")

    with open(scenario_path, "r") as f:
        return json.load(f)
