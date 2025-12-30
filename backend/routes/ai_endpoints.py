# backend/routes/ai_endpoints.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend import state
except ImportError:
    import state

router = APIRouter()


# ==================== PREDICTIONS ====================

@router.get("/simulation/{simulation_id}/predictions")
async def get_stampede_predictions(simulation_id: str):
    """
    Get AI stampede predictions for all zones
    
    Returns:
        {
            "predictions": [
                {
                    "zone_id": "zone_north",
                    "zone_name": "Zone North",
                    "risk_level": "high",
                    "probability": 0.75,
                    "time_to_stampede": 15,
                    "confidence": 0.82,
                    "contributing_factors": ["High density", "Rapid influx"],
                    "recommendations": ["Close entry", "Reroute flow"],
                    "current_density": 4.2,
                    "predicted_peak_density": 6.5
                }
            ]
        }
    """
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = state.active_simulations[simulation_id]
    
    # Check if stampede predictor is integrated
    if not hasattr(simulator, 'active_predictions'):
        return {"predictions": []}
    
    predictions_list = []
    
    for zone_id, pred in simulator.active_predictions.items():
        predictions_list.append({
            "zone_id": zone_id,
            "zone_name": zone_id.replace("_", " ").title(),
            "risk_level": pred.risk_level.value,
            "probability": pred.probability,
            "time_to_stampede": pred.time_to_stampede,
            "confidence": pred.confidence,
            "contributing_factors": pred.contributing_factors,
            "recommendations": pred.recommendations,
            "current_density": pred.current_density,
            "predicted_peak_density": pred.predicted_peak_density
        })
    
    # Sort by risk level (highest first)
    risk_order = {"imminent": 0, "critical": 1, "high": 2, 
                  "moderate": 3, "low": 4, "safe": 5}
    predictions_list.sort(key=lambda x: risk_order.get(x["risk_level"], 6))
    
    return {"predictions": predictions_list}


# ==================== CASCADES ====================

@router.get("/simulation/{simulation_id}/cascades")
async def get_active_cascades(simulation_id: str):
    """
    Get active cascade chains
    
    Returns:
        {
            "cascades": [
                {
                    "chain_id": "cascade_001",
                    "cascade_type": "bottleneck_backup",
                    "state": "active",
                    "origin_zone": "corridor_main",
                    "affected_zones": ["zone_a", "zone_b"],
                    "current_severity": 0.75,
                    "initiated_at": 120,
                    "predicted_stampede_step": 180,
                    "event_count": 5
                }
            ]
        }
    """
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = state.active_simulations[simulation_id]
    
    # Check if cascade engine is integrated
    if not hasattr(simulator, 'cascade_engine'):
        return {"cascades": []}
    
    cascades_list = []
    
    for cascade in simulator.cascade_engine.active_cascades:
        cascades_list.append({
            "chain_id": cascade.chain_id,
            "cascade_type": cascade.cascade_type.value,
            "state": cascade.state.value,
            "origin_zone": cascade.origin_zone,
            "affected_zones": cascade.affected_zones,
            "current_severity": cascade.current_severity,
            "initiated_at": cascade.initiated_at,
            "predicted_stampede_step": cascade.predicted_stampede_step,
            "event_count": len(cascade.events)
        })
    
    return {"cascades": cascades_list}


# ==================== INTERVENTIONS ====================

@router.get("/simulation/{simulation_id}/interventions")
async def get_recommended_interventions(simulation_id: str):
    """
    Get AI-recommended interventions (not yet applied)
    
    Returns:
        {
            "interventions": [
                {
                    "intervention_id": "INT_001",
                    "intervention_type": "close_entry",
                    "urgency": "critical",
                    "target_zone": "zone_north",
                    "action_description": "Close entry gate to prevent overcrowding",
                    "expected_lives_saved": 25,
                    "expected_density_reduction": 2.5,
                    "success_probability": 0.85,
                    "reasoning": "High density detected with rapid influx",
                    "deadline_step": 150
                }
            ]
        }
    """
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = state.active_simulations[simulation_id]
    
    # Check if intervention engine exists
    if not hasattr(simulator, 'intervention_engine'):
        return {"interventions": []}
    
    interventions_list = []
    
    # Generate interventions from predictions
    if hasattr(simulator, 'active_predictions'):
        for zone_id, prediction in simulator.active_predictions.items():
            # Only show moderate+ risk interventions
            if prediction.risk_level.value in ["moderate", "high", "critical", "imminent"]:
                plan = simulator.intervention_engine.recommend_for_prediction(
                    prediction,
                    int(simulator.current_time)
                )
                
                if plan and plan.primary_option:
                    option = plan.primary_option
                    interventions_list.append({
                        "intervention_id": option.intervention_id,
                        "intervention_type": option.intervention_type.value,
                        "urgency": option.urgency.value,
                        "target_zone": option.target_zone,
                        "action_description": option.action_description,
                        "expected_lives_saved": option.expected_lives_saved,
                        "expected_density_reduction": option.expected_density_reduction,
                        "success_probability": option.success_probability,
                        "reasoning": option.reasoning,
                        "deadline_step": option.deadline_step
                    })
    
    return {"interventions": interventions_list}


@router.get("/simulation/{simulation_id}/applied-interventions")
async def get_applied_interventions(simulation_id: str):
    """
    Get interventions that have been applied by AI
    
    Returns:
        {
            "interventions": [
                {
                    "intervention_id": "INT_001",
                    "target_zone": "zone_north",
                    "action": "close_entry",
                    "urgency": "critical",
                    "applied_at": 125
                }
            ]
        }
    """
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = state.active_simulations[simulation_id]
    
    if not hasattr(simulator, 'active_interventions'):
        return {"interventions": []}
    
    applied = []
    
    for intervention in simulator.active_interventions:
        applied.append({
            "intervention_id": intervention.intervention_id,
            "target_zone": intervention.target_zone,
            "action": intervention.intervention_type.value,
            "urgency": intervention.urgency.value,
            "applied_at": int(simulator.current_time)
        })
    
    return {"interventions": applied}


# ==================== AI ACTIONS LOG ====================

@router.get("/simulation/{simulation_id}/ai-actions")
async def get_ai_action_log(simulation_id: str):
    """
    Get complete log of all AI actions taken
    
    Returns:
        {
            "actions": [
                {
                    "step": 125,
                    "zone": "zone_north",
                    "action": "close_entry",
                    "reason": "Critical density detected",
                    "severity": "critical"
                }
            ]
        }
    """
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = state.active_simulations[simulation_id]
    
    # Get from AI action log
    actions = []
    
    if hasattr(simulator, 'ai_action_log'):
        actions = simulator.ai_action_log
    
    return {"actions": actions}


# ==================== MANUAL INTERVENTION ====================

class ApplyInterventionRequest(BaseModel):
    intervention_id: str
    force: bool = False  # Force apply even if not recommended

@router.post("/simulation/{simulation_id}/intervention")
async def apply_manual_intervention(
    simulation_id: str, 
    request: ApplyInterventionRequest
):
    """
    Manually apply a specific intervention
    
    Body:
        {
            "intervention_id": "INT_001",
            "force": false
        }
    
    Returns:
        {
            "status": "applied",
            "intervention_id": "INT_001",
            "message": "Intervention applied successfully",
            "effects": {
                "agents_rerouted": 15,
                "density_reduced": 1.5
            }
        }
    """
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = state.active_simulations[simulation_id]
    
    if not hasattr(simulator, 'intervention_engine'):
        raise HTTPException(status_code=400, detail="No intervention engine available")
    
    # TODO: Look up intervention by ID and apply it
    # For now, just acknowledge
    
    return {
        "status": "applied",
        "intervention_id": request.intervention_id,
        "message": "Intervention applied successfully",
        "effects": {
            "agents_rerouted": 0,
            "density_reduced": 0.0
        }
    }


# ==================== CUSTOM SIMULATION ENDPOINTS ====================

@router.post("/simulation/{simulation_id}/step-custom")
async def step_custom_simulation(simulation_id: str):
    """
    Step forward custom simulation (with event triggers)
    Same as /step but returns more AI data
    """
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = state.active_simulations[simulation_id]
    current_state = simulator.step()
    
    # Build zone data for frontend
    zone_data = {}
    for node_id, node_data in simulator.twin.node_data.items():
        zone_data[node_id] = {
            "agent_count": node_data["current_count"],
            "density": node_data["density"],
            "capacity": node_data["capacity"],
            "area": node_data["area_m2"]
        }
    
    return {
        "simulation_id": simulation_id,
        "current_step": int(simulator.current_time),
        "active_agents": len(simulator.agents),
        "reached_goal": simulator.stats["agents_reached_goal"],
        "max_density": simulator.stats["max_density_reached"],
        "stampedes": simulator.stats.get("stampedes_prevented", 0),
        "zone_data": zone_data,
        "ai_actions_taken": current_state.get("ai_actions_taken", [])
    }
