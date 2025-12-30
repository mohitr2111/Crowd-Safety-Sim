from fastapi import APIRouter, HTTPException

try:
    from backend import state
except ImportError:
    import state


router = APIRouter()


@router.get("/simulation/{simulation_id}/graph")
def get_graph_structure(simulation_id: str):
    """Get digital twin graph structure for visualization"""
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = state.active_simulations[simulation_id]
    twin = simulator.twin

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


@router.get("/simulation/{simulation_id}/venue-status")
def get_venue_status(simulation_id: str):
    """Get real-time venue capacity and recommendations"""
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = state.active_simulations[simulation_id]
    state_data = simulator.get_simulation_state()

    # Calculate capacity dynamically
    total_capacity = 0
    for node_id, node_data in simulator.twin.node_data.items():
        total_capacity += node_data.get("capacity", 0)

    if total_capacity == 0:
        total_area = sum(n.get("area_m2", 0) for n in simulator.twin.node_data.values())
        total_capacity = int(total_area * 2)

    # Calculate node densities
    node_densities = {}
    nodes_data = state_data.get("nodes", {})

    # Count active agents correctly
    active_agents = 0

    for node_id, node_state in nodes_data.items():
        twin_node = simulator.twin.node_data.get(node_id, {})
        area_m2 = twin_node.get("area_m2", 1)
        current_count = node_state.get("current_count", 0)
        density = current_count / area_m2 if area_m2 > 0 else 0
        node_densities[node_id] = density

        if not node_id.startswith("exit"):
            active_agents += current_count

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
                    "reason": f"Density {density:.1f} p/m² exceeds danger threshold",
                    "recommendation": f"Close {node_id} temporarily and reroute",
                    "color": "red",
                }
            )
        elif density > warning_threshold:
            recommendations.append(
                {
                    "priority": "WARNING",
                    "location": node_id.replace("_", " ").title(),
                    "action": "REDUCE_FLOW",
                    "reason": f"Density {density:.1f} p/m² approaching danger",
                    "recommendation": f"Reduce inflow to {node_id} by 30%",
                    "color": "orange",
                }
            )

    recommendations.sort(key=lambda x: 0 if x["priority"] == "CRITICAL" else 1)

    occupancy_percent = (active_agents / total_capacity * 100) if total_capacity > 0 else 0

    return {
        "venue_status": {
            "name": "Stadium",
            "capacity": total_capacity,
            "current_occupancy": max(0, active_agents),
            "occupancy_percent": max(0, occupancy_percent),
            "status": "FULL" if occupancy_percent >= 100 else "AVAILABLE",
        },
        "recommendations": recommendations[:5],
        "timestamp": state_data.get("time", 0),
    }


@router.post("/simulation/{simulation_id}/execute-action")
def execute_action(simulation_id: str, action: dict):
    """Execute a safety recommendation action"""
    if simulation_id not in state.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulator = state.active_simulations[simulation_id]
    action_type = action.get("action_type")
    target_node = action.get("target_node")
    duration = action.get("duration", 60)
    intensity = action.get("intensity", 0.5)

    expiration_time = simulator.current_time + duration

    if action_type == "CLOSE_NODE":
        if target_node in simulator.twin.node_data:
            simulator.twin.node_data[target_node]["is_blocked"] = True
            simulator.twin.node_data[target_node]["block_expires"] = expiration_time

            rerouted_count = 0
            for agent in simulator.agents.values():
                if agent.get_next_node() == target_node or target_node in (agent.path or []):
                    alt_path = simulator.twin.get_shortest_path(agent.current_node, agent.goal_node)
                    if alt_path:
                        agent.set_path(alt_path)
                        rerouted_count += 1

            return {
                "status": "executed",
                "action": "CLOSE_NODE",
                "target": target_node,
                "duration": duration,
                "agents_rerouted": rerouted_count,
                "expires_at": expiration_time,
            }

    elif action_type == "REDUCE_FLOW":
        affected_count = 0
        for agent in simulator.agents.values():
            if agent.get_next_node() == target_node:
                agent.wait_time += intensity * 2.0
                affected_count += 1

        return {
            "status": "executed",
            "action": "REDUCE_FLOW",
            "target": target_node,
            "intensity": intensity,
            "agents_affected": affected_count,
        }

    elif action_type == "REROUTE":
        exit_nodes = [
            n
            for n, data in simulator.twin.node_data.items()
            if data["type"] == "exit" and n != target_node
        ]

        if not exit_nodes:
            return {"status": "failed", "reason": "No alternative exits available"}

        alt_exit = min(exit_nodes, key=lambda n: simulator.twin.node_data[n]["density"])

        rerouted_count = 0
        for agent in simulator.agents.values():
            if agent.goal_node == target_node:
                alt_path = simulator.twin.get_shortest_path(agent.current_node, alt_exit)
                if alt_path:
                    agent.set_path(alt_path)
                    agent.goal_node = alt_exit
                    rerouted_count += 1

        return {
            "status": "executed",
            "action": "REROUTE",
            "from_exit": target_node,
            "to_exit": alt_exit,
            "agents_rerouted": rerouted_count,
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action type: {action_type}")
