from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from simulation.simulator import Simulator


active_simulations: Dict[str, "Simulator"] = {}

simulations: Dict[str, Any] = {}
