import uuid

from fastapi import APIRouter, HTTPException

from app_state import active_simulations, load_scenario
from models.schemas import SimulationRequest, SimulationStepRequest, InterventionRequest, AutoExecutionSettings
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
                    "node_id": node_id,  # PHASE 2: Include node_id for intervention execution
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
                    "node_id": node_id,  # PHASE 2: Include node_id for intervention execution
                    "location": node_id.replace("_", " ").title(),
                    "action": "REDUCE_FLOW",
                    "reason": f"Density {density:.1f} p/m² approaching danger level",
                    "recommendation": f"Reduce inflow to {node_id} by 30% and monitor closely",
                    "color": "orange",
                }
            )

    # Sort by density (highest first)
    recommendations.sort(key=lambda x: 0 if x["priority"] == "CRITICAL" else 1)

    # PHASE 3: Process recommendations through auto-execution engine
    from Components.auto_execution import auto_execution_engine
    
    # Initialize if needed
    if simulation_id not in auto_execution_engine.execution_settings:
        auto_execution_engine.initialize_simulation(simulation_id)
    
    # Check for active triggers
    active_triggers = simulator.trigger_system.get_active_triggers(simulator.current_time)
    has_active_trigger = len(active_triggers) > 0
    
    # Process each recommendation
    processed_recommendations = []
    auto_executed_count = 0
    
    for rec in recommendations[:5]:  # Top 5
        # Build context for risk assessment
        node_id = rec.get("node_id")
        density = node_densities.get(node_id, 0.0)
        
        context = {
            "density": density,
            "has_active_trigger": has_active_trigger,
            "simulation_time": simulator.current_time,
        }
        
        # Process through auto-execution engine
        result = auto_execution_engine.process_recommendation(simulation_id, rec, context)
        
        # Add processing result to recommendation
        rec["processing_result"] = result
        
        if result.get("status") == "AUTO_EXECUTED":
            auto_executed_count += 1
            # Execute the intervention immediately
            from density_rl.trainer import DensityRLTrainer
            trainer = DensityRLTrainer()
            
            # Map recommendation action to intervention action
            action_mapping = {
                "CLOSE_TEMPORARILY": "CLOSE_INFLOW",
                "REDUCE_FLOW": "THROTTLE_25" if rec.get("priority") == "WARNING" else "THROTTLE_50",
                "REROUTE": "REROUTE",
            }
            intervention_action = action_mapping.get(rec.get("action"), "NOOP")
            
            if intervention_action != "NOOP" and node_id:
                trainer.apply_action(simulator, node_id, intervention_action)
                
                # Log auto-execution
                simulator.ai_actions.append({
                    'time_seconds': simulator.current_time,
                    'action': f"Auto-executed: {intervention_action}",
                    'action_type': intervention_action,
                    'node': node_id,
                    'priority': rec.get("priority", "WARNING"),
                    'human_approved': False,
                    'auto_executed': True,
                    'risk_level': result.get("intervention", {}).get("risk_level", "LOW"),
                })
        
        processed_recommendations.append(rec)

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
        "recommendations": processed_recommendations,
        "phase3_stats": {
            "auto_executed": auto_executed_count,
            "pending_count": len(auto_execution_engine.get_pending_actions(simulation_id)),
        },
        "timestamp": state.get("time", 0),
        "debug": {
            "total_agents": total_agents,
            "reached_goal": reached_goal,
            "active_agents": active_agents,
            "max_density": max(node_densities.values()) if node_densities else 0,
        },
    }


@router.post("/{simulation_id}/execute-intervention")
def execute_intervention(simulation_id: str, intervention: InterventionRequest):
    """
    PHASE 2: Execute an approved intervention on a simulation
    
    Maps recommendation actions to intervention actions:
    - CLOSE_TEMPORARILY -> CLOSE_INFLOW
    - REDUCE_FLOW -> THROTTLE_50 (can be adjusted based on priority)
    - REROUTE -> REROUTE
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]
    
    # Map recommendation actions to intervention actions
    action_mapping = {
        "CLOSE_TEMPORARILY": "CLOSE_INFLOW",
        "REDUCE_FLOW": "THROTTLE_50",  # Default to moderate throttling
        "REROUTE": "REROUTE",
    }
    
    # Adjust action based on priority if REDUCE_FLOW
    intervention_action = action_mapping.get(intervention.action)
    if not intervention_action:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown action: {intervention.action}. Supported: {list(action_mapping.keys())}"
        )
    
    # Adjust throttling based on priority for REDUCE_FLOW
    if intervention.action == "REDUCE_FLOW":
        if intervention.priority == "CRITICAL":
            intervention_action = "THROTTLE_50"
        elif intervention.priority == "WARNING":
            intervention_action = "THROTTLE_25"
        else:
            intervention_action = "THROTTLE_25"
    
    # Verify node exists
    if intervention.node_id not in simulator.digital_twin.node_data:
        raise HTTPException(
            status_code=400,
            detail=f"Node {intervention.node_id} not found in simulation"
        )
    
    # Apply intervention using DensityRLTrainer
    from density_rl.trainer import DensityRLTrainer
    
    trainer = DensityRLTrainer()
    trainer.apply_action(simulator, intervention.node_id, intervention_action)
    
    # Log the intervention
    simulator.ai_actions.append({
        'time_seconds': simulator.current_time,
        'action': f"Human-approved: {intervention_action}",
        'action_type': intervention_action,
        'node': intervention.node_id,
        'priority': intervention.priority or 'WARNING',
        'human_approved': True,
        'original_recommendation': intervention.action,
    })
    
    # Get updated state
    state = simulator.get_simulation_state()
    
    return {
        "simulation_id": simulation_id,
        "status": "success",
        "intervention_applied": {
            "node_id": intervention.node_id,
            "action": intervention_action,
            "original_recommendation": intervention.action,
            "priority": intervention.priority,
        },
        "message": f"Intervention {intervention_action} applied to {intervention.node_id}",
        "current_state": state,
    }


# ============================================================================
# PHASE 3: CONTROLLED AUTONOMY ENDPOINTS
# ============================================================================

@router.get("/{simulation_id}/pending-actions")
def get_pending_actions(simulation_id: str):
    """
    PHASE 3: Get all pending actions awaiting approval
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.auto_execution import auto_execution_engine
    
    pending = auto_execution_engine.get_pending_actions(simulation_id)
    
    return {
        "simulation_id": simulation_id,
        "pending_actions": pending,
        "count": len(pending),
    }


@router.post("/{simulation_id}/pending-actions/{action_id}/approve")
def approve_pending_action(simulation_id: str, action_id: str):
    """
    PHASE 3: Approve a pending intervention action
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.auto_execution import auto_execution_engine
    from density_rl.trainer import DensityRLTrainer
    
    simulator = active_simulations[simulation_id]
    
    # Get and approve the action
    pending = auto_execution_engine.approve_action(simulation_id, action_id)
    if not pending:
        raise HTTPException(status_code=404, detail="Pending action not found")
    
    # Execute the intervention
    trainer = DensityRLTrainer()
    trainer.apply_action(simulator, pending.node_id, pending.action)
    
    # Mark as executed
    pending.status = "EXECUTED"
    
    # Log the intervention
    simulator.ai_actions.append({
        'time_seconds': simulator.current_time,
        'action': f"Supervisor-approved: {pending.action}",
        'action_type': pending.action,
        'node': pending.node_id,
        'priority': pending.priority,
        'human_approved': True,
        'action_id': action_id,
        'risk_level': pending.risk_level,
    })
    
    # Log to audit
    auto_execution_engine._log_action(simulation_id, {
        "type": "ACTION_EXECUTED",
        "action_id": action_id,
        "node_id": pending.node_id,
        "action": pending.action,
        "time": simulator.current_time,
    })
    
    state = simulator.get_simulation_state()
    
    return {
        "simulation_id": simulation_id,
        "status": "success",
        "action_id": action_id,
        "message": f"Intervention {pending.action} approved and executed on {pending.node_id}",
        "intervention": pending.to_dict(),
        "current_state": state,
    }


@router.post("/{simulation_id}/pending-actions/{action_id}/reject")
def reject_pending_action(simulation_id: str, action_id: str):
    """
    PHASE 3: Reject a pending intervention action
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.auto_execution import auto_execution_engine
    
    pending = auto_execution_engine.reject_action(simulation_id, action_id)
    if not pending:
        raise HTTPException(status_code=404, detail="Pending action not found")
    
    return {
        "simulation_id": simulation_id,
        "status": "success",
        "action_id": action_id,
        "message": f"Intervention {pending.action} rejected",
        "intervention": pending.to_dict(),
    }


@router.post("/{simulation_id}/settings/auto-execute")
def update_auto_execution_settings(simulation_id: str, settings: AutoExecutionSettings):
    """
    PHASE 3: Update auto-execution settings for a simulation
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.auto_execution import auto_execution_engine
    
    auto_execution_engine.update_settings(
        simulation_id,
        auto_execute_enabled=settings.auto_execute_enabled,
        disabled_nodes=settings.disabled_nodes
    )
    
    # Log to audit
    auto_execution_engine._log_action(simulation_id, {
        "type": "SETTINGS_UPDATED",
        "auto_execute_enabled": settings.auto_execute_enabled,
        "disabled_nodes": settings.disabled_nodes or [],
        "time": active_simulations[simulation_id].current_time,
    })
    
    return {
        "simulation_id": simulation_id,
        "status": "success",
        "message": "Auto-execution settings updated",
        "settings": {
            "auto_execute_enabled": settings.auto_execute_enabled,
            "disabled_nodes": settings.disabled_nodes or [],
        },
    }


@router.get("/{simulation_id}/settings/auto-execute")
def get_auto_execution_settings(simulation_id: str):
    """
    PHASE 3: Get current auto-execution settings
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.auto_execution import auto_execution_engine
    
    if simulation_id not in auto_execution_engine.execution_settings:
        auto_execution_engine.initialize_simulation(simulation_id)
    
    settings = auto_execution_engine.execution_settings[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "settings": settings,
    }


@router.get("/{simulation_id}/audit-log")
def get_audit_log(simulation_id: str, limit: int = 100):
    """
    PHASE 3: Get audit log for a simulation
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.auto_execution import auto_execution_engine
    
    audit_log = auto_execution_engine.get_audit_log(simulation_id, limit=limit)
    
    return {
        "simulation_id": simulation_id,
        "audit_log": audit_log,
        "count": len(audit_log),
    }


# ============================================================================
# PHASE 4: PARTIAL AUTONOMY ENDPOINTS
# ============================================================================

@router.post("/{simulation_id}/spawn-control")
def control_spawn_rate(simulation_id: str, request: dict):
    """
    PHASE 4: Control spawn rate at entry nodes
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.spawn_control import spawn_rate_controller
    
    node_id = request.get("node_id")
    rate_multiplier = request.get("rate_multiplier", 1.0)
    duration = request.get("duration")
    current_time = active_simulations[simulation_id].current_time
    
    spawn_rate_controller.set_spawn_rate(node_id, rate_multiplier, duration, current_time)
    
    state = spawn_rate_controller.get_state(node_id)
    
    return {
        "simulation_id": simulation_id,
        "message": f"Spawn rate control applied to {node_id}",
        "state": state,
    }


@router.get("/{simulation_id}/spawn-control/{node_id}")
def get_spawn_control_state(simulation_id: str, node_id: str):
    """
    PHASE 4: Get spawn control state for a node
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.spawn_control import spawn_rate_controller
    
    state = spawn_rate_controller.get_state(node_id)
    
    if state is None:
        raise HTTPException(status_code=404, detail=f"Spawn control not initialized for node {node_id}")
    
    return {
        "simulation_id": simulation_id,
        "node_id": node_id,
        "state": state,
    }


@router.post("/{simulation_id}/capacity-adjustment")
def adjust_capacity(simulation_id: str, request: dict):
    """
    PHASE 4: Adjust node or edge capacity
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.capacity_control import capacity_controller
    
    simulator = active_simulations[simulation_id]
    node_id = request.get("node_id")
    adjustment_type = request.get("adjustment_type")
    factor = request.get("factor")
    duration = request.get("duration")
    current_time = simulator.current_time
    
    # Register nodes/edges if not already registered
    for node_id_twin, node_data in simulator.digital_twin.node_data.items():
        capacity_controller.register_node(
            node_id_twin,
            node_data["area_m2"],
            node_data.get("capacity", 0)
        )
    
    success = False
    if adjustment_type == "expand_area":
        success = capacity_controller.expand_node_area(node_id, factor, duration, current_time)
    elif adjustment_type == "block_zone":
        success = capacity_controller.block_zone(node_id, duration, current_time)
    elif adjustment_type == "restore":
        success = capacity_controller.restore_node(node_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown adjustment type: {adjustment_type}")
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to apply capacity adjustment")
    
    state = capacity_controller.get_node_state(node_id)
    
    return {
        "simulation_id": simulation_id,
        "message": f"Capacity adjustment applied to {node_id}",
        "state": state,
    }


@router.get("/{simulation_id}/capacity/{node_id}")
def get_capacity_state(simulation_id: str, node_id: str):
    """
    PHASE 4: Get capacity state for a node
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.capacity_control import capacity_controller
    
    state = capacity_controller.get_node_state(node_id)
    
    if state is None:
        # Return original capacity from digital twin
        simulator = active_simulations[simulation_id]
        if node_id in simulator.digital_twin.node_data:
            node_data = simulator.digital_twin.node_data[node_id]
            return {
                "simulation_id": simulation_id,
                "node_id": node_id,
                "state": {
                    "current_area_m2": node_data["area_m2"],
                    "current_capacity": node_data.get("capacity", 0),
                    "is_blocked": False,
                },
            }
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    return {
        "simulation_id": simulation_id,
        "node_id": node_id,
        "state": state,
    }


@router.get("/{simulation_id}/monitoring/health")
def get_system_health(simulation_id: str):
    """
    PHASE 4: Get system health metrics
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.advanced_monitoring import advanced_monitoring
    from Components.auto_execution import auto_execution_engine
    
    simulator = active_simulations[simulation_id]
    state = simulator.get_simulation_state()
    
    # Calculate node densities
    node_densities = {}
    for node_id, node_state in state.get("nodes", {}).items():
        node_data = simulator.digital_twin.node_data.get(node_id, {})
        area_m2 = node_data.get("area_m2", 1)
        current_count = node_state.get("current_count", 0)
        density = current_count / area_m2 if area_m2 > 0 else 0
        node_densities[node_id] = density
    
    # Record density snapshot
    advanced_monitoring.record_density_snapshot(simulator.current_time, node_densities)
    
    # Get active interventions
    active_interventions = len(auto_execution_engine.get_pending_actions(simulation_id))
    danger_zone_count = len(simulator.digital_twin.get_danger_zones())
    
    # Calculate health metrics
    health = advanced_monitoring.calculate_system_health(
        simulator.current_time,
        node_densities,
        active_interventions,
        danger_zone_count
    )
    
    return {
        "simulation_id": simulation_id,
        "health": {
            "overall_status": health.overall_status.value,
            "intervention_frequency": health.intervention_frequency,
            "average_effectiveness": health.average_effectiveness,
            "danger_zone_count": health.danger_zone_count,
            "max_density": health.max_density,
            "active_interventions": health.active_interventions,
            "system_stability": health.system_stability,
            "last_updated": health.last_updated,
        },
    }


@router.get("/{simulation_id}/monitoring/stampede-prediction")
def get_stampede_prediction(simulation_id: str):
    """
    PHASE 4: Get predictive stampede probability
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.advanced_monitoring import advanced_monitoring
    from Components.failsafe_mechanisms import failsafe_mechanisms
    
    simulator = active_simulations[simulation_id]
    state = simulator.get_simulation_state()
    
    # Calculate node densities
    node_densities = {}
    for node_id, node_state in state.get("nodes", {}).items():
        node_data = simulator.digital_twin.node_data.get(node_id, {})
        area_m2 = node_data.get("area_m2", 1)
        current_count = node_state.get("current_count", 0)
        density = current_count / area_m2 if area_m2 > 0 else 0
        node_densities[node_id] = density
    
    # Get active triggers
    active_triggers = simulator.trigger_system.get_active_triggers(simulator.current_time)
    
    # Get intervention frequency
    safety_status = failsafe_mechanisms.get_safety_status(simulator.current_time)
    intervention_frequency = safety_status["current_status"]["current_frequency"]
    
    # Predict stampede probability
    prediction = advanced_monitoring.predict_stampede_probability(
        node_densities,
        simulator.current_time,
        active_triggers,
        intervention_frequency
    )
    
    return {
        "simulation_id": simulation_id,
        "prediction": {
            "probability": prediction.probability,
            "risk_level": prediction.risk_level,
            "predicted_time": prediction.predicted_time,
            "contributing_factors": prediction.contributing_factors,
            "confidence": prediction.confidence,
            "last_updated": prediction.last_updated,
        },
    }


@router.get("/{simulation_id}/safety/status")
def get_safety_status(simulation_id: str):
    """
    PHASE 4: Get safety constraints status
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.failsafe_mechanisms import failsafe_mechanisms
    
    simulator = active_simulations[simulation_id]
    status = failsafe_mechanisms.get_safety_status(simulator.current_time)
    
    return {
        "simulation_id": simulation_id,
        "safety_status": status,
    }


@router.post("/{simulation_id}/safety/constraints")
def update_safety_constraints(simulation_id: str, request: dict):
    """
    PHASE 4: Update safety constraints
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.failsafe_mechanisms import failsafe_mechanisms
    
    failsafe_mechanisms.configure_constraints(
        max_interventions_per_minute=request.get("max_interventions_per_minute"),
        min_interval_seconds=request.get("min_interval_seconds"),
        max_active_interventions=request.get("max_active_interventions"),
        enable_rollback=request.get("enable_rollback"),
        enable_manual_override=request.get("enable_manual_override"),
    )
    
    simulator = active_simulations[simulation_id]
    status = failsafe_mechanisms.get_safety_status(simulator.current_time)
    
    return {
        "simulation_id": simulation_id,
        "message": "Safety constraints updated",
        "safety_status": status,
    }


@router.post("/{simulation_id}/safety/rollback")
def rollback_intervention(simulation_id: str, request: dict):
    """
    PHASE 4: Rollback an intervention
    """
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    from Components.failsafe_mechanisms import failsafe_mechanisms
    
    simulator = active_simulations[simulation_id]
    intervention_id = request.get("intervention_id")
    
    record = failsafe_mechanisms.rollback_intervention(intervention_id, simulator.current_time)
    
    if record is None:
        raise HTTPException(status_code=400, detail="Failed to rollback intervention")
    
    return {
        "simulation_id": simulation_id,
        "message": f"Intervention {intervention_id or 'most recent'} rolled back",
        "intervention": {
            "intervention_id": record.intervention_id,
            "action_type": record.action_type,
            "node_id": record.node_id,
            "applied_at": record.applied_at,
            "rolled_back_at": record.rolled_back_at,
        },
    }
