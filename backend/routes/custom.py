import random
import time

from fastapi import APIRouter, HTTPException

try:
    from backend import state
except ImportError:
    import state


router = APIRouter()


def apply_triggers(sim, current_step):
    """Apply active triggers to simulation"""
    active_triggers = []

    for trigger in sim.get("triggers", []):
        trigger_step = trigger.get("step", 0)

        # Check if trigger is active (within range)
        if trigger_step <= current_step <= trigger_step + 50:
            active_triggers.append(trigger)

            # Apply trigger effects based on type
            trigger_type = trigger.get("type")
            affected_zone = trigger.get("affectedZone")
            params = trigger.get("parameters", {})

            if affected_zone in sim["digital_twin"]["zones"]:
                # Get current zone data
                zone = sim["digital_twin"]["zones"][affected_zone]

                # Apply different effects based on trigger type
                if trigger_type == "fire":
                    # Fire: People rush to exits
                    severity = params.get("severity", 5.0)
                    zone["panic_multiplier"] = 1 + (severity / 10)

                elif trigger_type == "vip_delay":
                    # VIP Delay: Entry blocked temporarily
                    delay_minutes = params.get("delay", 30)
                    if current_step < trigger_step + delay_minutes:
                        zone["entry_blocked"] = True
                    else:
                        zone["entry_blocked"] = False

                elif trigger_type == "explosion":
                    # Explosion: Mass panic, everyone rushes
                    radius = params.get("radius", 100)
                    severity = params.get("severity", 9.0)
                    zone["panic_multiplier"] = 2.0 + (severity / 5)

                elif trigger_type == "crowd_surge":
                    # Crowd Surge: Sudden density increase
                    surge_intensity = params.get("intensity", 500)
                    zone["surge_agents"] = surge_intensity

                elif trigger_type == "infrastructure_failure":
                    # Infrastructure: Exit blocked
                    affected_exits = params.get("affectedExits", [])
                    zone["blocked_exits"] = affected_exits

                elif trigger_type == "weather":
                    # Weather: Slows movement
                    severity = params.get("severity", 5.0)
                    zone["weather_slowdown"] = severity / 10

                elif trigger_type == "security_threat":
                    # Security: Area evacuation
                    severity = params.get("severity", 7.0)
                    zone["evacuation_mode"] = True
                    zone["panic_multiplier"] = 1.5

                elif trigger_type == "medical_emergency":
                    # Medical: Area partially blocked
                    zone["partial_blockage"] = 0.3  # 30% capacity reduction

                elif trigger_type == "power_outage":
                    # Power outage: Confusion, slower movement
                    zone["visibility_reduced"] = True
                    zone["panic_multiplier"] = 1.3

    return active_triggers


@router.post("/simulation/create-custom")
async def create_custom_simulation(request: dict):
    """Create simulation from Scenario Builder"""
    try:
        venue_data = request.get("venue")
        event_config = request.get("event")
        triggers = request.get("triggers", [])
        num_agents = request.get("num_agents", 30000)

        # Create digital twin from venue data
        zones = {}
        for zone in venue_data["zones"]:
            zones[zone["id"]] = {
                "capacity": zone["capacity"],
                "area": zone["area"],
                "type": zone.get("type", "regular"),
                "panic_multiplier": 1.0,
                "surge_agents": 0,
                "entry_blocked": False,
                "blocked_exits": [],
            }

        # Create graph structure
        graph = {}
        for conn in venue_data["connections"]:
            if conn["from"] not in graph:
                graph[conn["from"]] = []
            graph[conn["from"]].append(conn["to"])

            if conn["to"] not in graph:
                graph[conn["to"]] = []
            graph[conn["to"]].append(conn["from"])

        # Initialize simulation
        sim_id = f"custom_{int(time.time())}"

        # ✅ NEW: Calculate spawn duration (realistic arrival pattern)
        if num_agents < 10000:
            spawn_duration = 60  # 60 steps = 30 minutes
        elif num_agents < 30000:
            spawn_duration = 120  # 120 steps = 60 minutes
        else:
            spawn_duration = 180  # 180 steps = 90 minutes

        # Store simulation data
        state.simulations[sim_id] = {
            "digital_twin": {
                "zones": zones,
                "graph": graph,
                "entries": venue_data["entries"],
                "exits": venue_data["exits"],
            },
            "event_config": event_config,
            "triggers": triggers,
            "current_step": 0,
            "agents": [],
            "stats": {
                "active_agents": 0,
                "reached_goal": 0,
                "max_density": 0,
                "stampedes": 0,
            },
            "applied_interventions": [],
            "ai_actions_log": [],
            # ✅ NEW: Spawn configuration
            "spawn_config": {
                "total_agents": num_agents,
                "spawn_duration": spawn_duration,
                "spawned_count": 0,
                "spawn_rate": num_agents / spawn_duration,  # Agents per step
            },
        }

        return {
            "simulation_id": sim_id,
            "status": "created",
            "message": f"Simulation created: {num_agents} agents will arrive over {spawn_duration} steps (~{spawn_duration/2} minutes)",
            "spawn_info": {
                "total": num_agents,
                "duration_steps": spawn_duration,
                "duration_minutes": spawn_duration / 2,
                "rate_per_step": int(num_agents / spawn_duration),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation/{simulation_id}/step-custom")
async def step_custom_simulation(simulation_id: str):
    """Step custom simulation forward with trigger support"""
    if simulation_id not in state.simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = state.simulations[simulation_id]
    sim["current_step"] += 1

    # ✅ NEW: SPAWN AGENTS GRADUALLY
    spawn_config = sim.get("spawn_config", {})
    if spawn_config:
        total_agents = spawn_config["total_agents"]
        spawn_duration = spawn_config["spawn_duration"]
        spawned_count = spawn_config["spawned_count"]
        spawn_rate = spawn_config["spawn_rate"]

        # Calculate how many agents to spawn this step
        if sim["current_step"] <= spawn_duration and spawned_count < total_agents:
            # Use Poisson-like distribution for realistic arrival
            agents_this_step = int(spawn_rate)

            # Add random variance (±20%)
            variance = random.randint(-int(spawn_rate * 0.2), int(spawn_rate * 0.2))
            agents_this_step = max(1, agents_this_step + variance)

            # Don't exceed total
            agents_this_step = min(agents_this_step, total_agents - spawned_count)

            # Spawn agents at random entry points
            for i in range(agents_this_step):
                agent_id = spawned_count + i
                entry = random.choice(sim["digital_twin"]["entries"])
                exit_zone = random.choice(sim["digital_twin"]["exits"])

                agent = {
                    "id": agent_id,
                    "position": entry,
                    "goal": exit_zone,
                    "reached": False,
                    "spawn_step": sim["current_step"],
                }
                sim["agents"].append(agent)

            # Update spawn count
            spawn_config["spawned_count"] += agents_this_step

    # Apply triggers
    active_triggers = apply_triggers(sim, sim["current_step"])

    # Calculate zone densities with trigger effects
    zone_data = {}
    ai_actions_taken = []

    for zone_id in sim["digital_twin"]["zones"].keys():
        agents_in_zone = [
            a for a in sim["agents"] if a["position"] == zone_id and not a["reached"]
        ]

        zone = sim["digital_twin"]["zones"][zone_id]
        zone_area = zone["area"]

        # Base agent count
        agent_count = len(agents_in_zone)

        # ADD: Surge agents from triggers
        surge_agents = zone.get("surge_agents", 0)
        if surge_agents > 0:
            agent_count += surge_agents
            zone["surge_agents"] = max(0, surge_agents - 10)

        # Calculate density
        density = agent_count / zone_area if zone_area > 0 else 0

        # APPLY: Panic multiplier from triggers
        panic_mult = zone.get("panic_multiplier", 1.0)
        density = density * panic_mult

        # Decay panic over time
        if panic_mult > 1.0:
            zone["panic_multiplier"] = max(1.0, panic_mult - 0.05)

        # ✅ AI INTERVENTION: More aggressive response
        if density > 5.0 and not zone.get("ai_intervention_applied", False):
            intervention_action = None

            if density > 8.0:
                # Critical: EMERGENCY CLOSE
                zone["entry_blocked"] = True
                zone["ai_intervention_applied"] = True
                intervention_action = {
                    "step": sim["current_step"],
                    "zone": zone_id,
                    "action": "EMERGENCY_CLOSE",
                    "reason": f"Critical density {density:.1f} p/m²",
                    "severity": "CRITICAL",
                }
            elif density > 6.5:
                # High: REDUCE FLOW
                zone["flow_reduction"] = 0.5
                zone["ai_intervention_applied"] = True
                intervention_action = {
                    "step": sim["current_step"],
                    "zone": zone_id,
                    "action": "REDUCE_FLOW",
                    "reason": f"High density {density:.1f} p/m²",
                    "severity": "HIGH",
                }
            elif density > 5.0:
                # Moderate: WARNING
                intervention_action = {
                    "step": sim["current_step"],
                    "zone": zone_id,
                    "action": "WARNING_ISSUED",
                    "reason": f"Elevated density {density:.1f} p/m²",
                    "severity": "MODERATE",
                }

            if intervention_action:
                ai_actions_taken.append(intervention_action)

                if "ai_actions_log" not in sim:
                    sim["ai_actions_log"] = []
                sim["ai_actions_log"].append(intervention_action)

        # Reset AI intervention flag if density drops
        if density < 3.0 and zone.get("ai_intervention_applied", False):
            zone["ai_intervention_applied"] = False
            zone["entry_blocked"] = False
            zone["flow_reduction"] = 1.0

        zone_data[zone_id] = {
            "density": density,
            "agent_count": agent_count,
            "speed": 1.0 / panic_mult,
            "flow_rate": 0.5 / panic_mult,
            "panic_level": panic_mult - 1.0,
            "is_blocked": zone.get("entry_blocked", False),
            "ai_protected": zone.get("ai_intervention_applied", False),
        }

    # Move agents (with AI intervention effects)
    for agent in sim["agents"]:
        if not agent["reached"] and agent["position"] != agent["goal"]:
            current_zone = sim["digital_twin"]["zones"].get(agent["position"], {})

            # AI intervention: Block entry
            if current_zone.get("entry_blocked", False):
                continue

            # AI intervention: Slow down flow
            flow_reduction = current_zone.get("flow_reduction", 1.0)
            if random.random() > flow_reduction:
                continue

            # Check if exit is blocked
            blocked_exits = current_zone.get("blocked_exits", [])

            if agent["position"] in sim["digital_twin"]["graph"]:
                next_positions = sim["digital_twin"]["graph"][agent["position"]]

                available_positions = [p for p in next_positions if p not in blocked_exits]

                if not available_positions:
                    continue

                if agent["goal"] in available_positions:
                    agent["position"] = agent["goal"]
                    agent["reached"] = True
                else:
                    agent["position"] = random.choice(available_positions)

    # Update stats
    active = len([a for a in sim["agents"] if not a["reached"]])
    reached = len([a for a in sim["agents"] if a["reached"]])
    max_density = max([z["density"] for z in zone_data.values()]) if zone_data else 0

    # Count stampedes (density > 8.5)
    stampedes = len([z for z in zone_data.values() if z["density"] > 8.5])

    sim["stats"] = {
        "active_agents": active,
        "reached_goal": reached,
        "max_density": max_density,
        "stampedes": stampedes,
    }

    full_log = sim.get("ai_actions_log", [])
    last_actions = full_log[-5:]

    return {
        "current_step": sim["current_step"],
        "zone_data": zone_data,
        "active_agents": active,
        "reached_goal": reached,
        "max_density": max_density,
        "stampedes": stampedes,
        "active_triggers": [{"name": t.get("name"), "type": t.get("type")} for t in active_triggers],
        "ai_actions_taken": last_actions,
        "total_ai_actions": len(sim.get("ai_actions_log", [])),
        "spawn_progress": {
            "spawned": spawn_config.get("spawned_count", 0),
            "total": spawn_config.get("total_agents", 0),
            "remaining": spawn_config.get("total_agents", 0)
            - spawn_config.get("spawned_count", 0),
        },
    }


@router.get("/simulation/{simulation_id}/ai-actions")
async def get_ai_actions(simulation_id: str):
    """Get all AI actions taken during simulation"""
    if simulation_id not in state.simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = state.simulations[simulation_id]
    actions_log = sim.get("ai_actions_log", [])

    return {"actions": actions_log, "total_actions": len(actions_log)}


@router.get("/simulation/{simulation_id}/predictions")
async def get_predictions(simulation_id: str):
    """Get stampede predictions for simulation"""
    if simulation_id not in state.simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Use stampede predictor from Phase 1
    from ai.stampede_predictor import DensitySnapshot, StampedePredictor

    predictor = StampedePredictor()
    sim = state.simulations[simulation_id]

    predictions = []

    # Get zone data from last step
    for zone_id in sim["digital_twin"]["zones"].keys():
        agents_in_zone = [
            a for a in sim["agents"] if a["position"] == zone_id and not a["reached"]
        ]
        zone_area = sim["digital_twin"]["zones"][zone_id]["area"]
        density = len(agents_in_zone) / zone_area if zone_area > 0 else 0

        # Create snapshot
        snapshot = DensitySnapshot(
            zone_id=zone_id,
            timestamp=sim["current_step"],
            density=density,
            agent_count=len(agents_in_zone),
            area=zone_area,
            flow_rate=0.5,
            avg_speed=1.0,
        )

        predictor.update_data(snapshot)

        # Get prediction
        pred = predictor.predict(zone_id)
        if pred and pred.risk_level.value not in ["safe", "low"]:
            predictions.append(
                {
                    "zone_id": pred.zone_id,
                    "risk_level": pred.risk_level.value,
                    "probability": pred.probability,
                    "time_to_stampede": pred.time_to_stampede,
                    "current_density": pred.current_density,
                    "predicted_peak_density": pred.predicted_peak_density,
                    "confidence": pred.confidence,
                }
            )

    return {"predictions": predictions}


@router.get("/simulation/{simulation_id}/cascades")
async def get_cascades(simulation_id: str):
    """Get active cascades"""
    if simulation_id not in state.simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Simplified for now
    return {"cascades": []}


@router.get("/simulation/{simulation_id}/interventions")
async def get_interventions(simulation_id: str):
    """Get AI intervention recommendations"""
    if simulation_id not in state.simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Use intervention engine from Phase 2
    from ai.intervention_engine import InterventionEngine
    from ai.stampede_predictor import RiskLevel, StampedePrediction

    engine = InterventionEngine()
    sim = state.simulations[simulation_id]

    interventions = []

    # Check each zone for high density
    for zone_id in sim["digital_twin"]["zones"].keys():
        agents_in_zone = [
            a for a in sim["agents"] if a["position"] == zone_id and not a["reached"]
        ]
        zone_area = sim["digital_twin"]["zones"][zone_id]["area"]
        density = len(agents_in_zone) / zone_area if zone_area > 0 else 0

        if density > 5.0:  # High risk threshold
            # Create prediction
            prediction = StampedePrediction(
                zone_id=zone_id,
                risk_level=RiskLevel.HIGH if density > 7.0 else RiskLevel.MODERATE,
                probability=min(density / 10.0, 1.0),
                time_to_stampede=int((8.5 - density) / 0.5) if density < 8.5 else 0,
                confidence=0.85,
                contributing_factors=[f"High density: {density:.1f} p/m²"],
                recommendations=[f"Close entries to {zone_id}"],
                current_density=density,
                predicted_peak_density=density + 1.5,
            )

            # Get intervention plan
            plan = engine.recommend_for_prediction(prediction, sim["current_step"])

            if plan:
                interventions.append(
                    {
                        "intervention_id": plan.primary_option.intervention_id,
                        "urgency": plan.primary_option.urgency.value,
                        "action_description": plan.primary_option.action_description,
                        "expected_lives_saved": plan.primary_option.expected_lives_saved,
                        "success_probability": plan.primary_option.success_probability,
                        "deadline_step": plan.primary_option.deadline_step,
                        "resource_cost": plan.primary_option.resource_cost,
                        "reasoning": plan.primary_option.reasoning,
                    }
                )

    return {"interventions": interventions}


@router.post("/simulation/{simulation_id}/intervention")
async def apply_intervention(simulation_id: str, request: dict):
    """Apply an intervention and track it"""
    if simulation_id not in state.simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    intervention_id = request.get("intervention_id")
    sim = state.simulations[simulation_id]

    # ✅ Track applied interventions
    sim["applied_interventions"].append(
        {
            "intervention_id": intervention_id,
            "applied_at_step": sim["current_step"],
            "timestamp": time.time(),
        }
    )

    # ✅ APPLY INTERVENTION EFFECTS
    # Example: Close entry to zone
    if "close_entry" in intervention_id:
        zone_id = intervention_id.split("_")[-1]  # Extract zone ID
        if zone_id in sim["digital_twin"]["zones"]:
            sim["digital_twin"]["zones"][zone_id]["entry_blocked"] = True

    # Example: Open alternate exit
    elif "open_exit" in intervention_id:
        zone_id = intervention_id.split("_")[-1]
        if zone_id in sim["digital_twin"]["zones"]:
            sim["digital_twin"]["zones"][zone_id]["blocked_exits"] = []

    # Example: Deploy security
    elif "deploy_security" in intervention_id:
        zone_id = intervention_id.split("_")[-1]
        if zone_id in sim["digital_twin"]["zones"]:
            # Reduce panic
            sim["digital_twin"]["zones"][zone_id]["panic_multiplier"] = 1.0

    print(f"✅ Applied intervention {intervention_id} to simulation {simulation_id}")

    return {
        "status": "applied",
        "message": f"Intervention {intervention_id} applied successfully",
        "applied_count": len(sim["applied_interventions"]),
    }


@router.get("/simulation/{simulation_id}/applied-interventions")
async def get_applied_interventions(simulation_id: str):
    """Get list of applied interventions"""
    if simulation_id not in state.simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = state.simulations[simulation_id]
    applied = sim.get("applied_interventions", [])

    return {"interventions": applied, "total_applied": len(applied)}
