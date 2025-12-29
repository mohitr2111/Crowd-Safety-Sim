# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uuid
import json
import os
from pathlib import Path
import random
import time


simulations = {}


from models.schemas import (
    SimulationRequest, 
    SimulationStepRequest,
    SimulationResponse,
    SimulationState
)
from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator
from rl.comparison import SimulationComparison
from rl.q_learning_agent import CrowdSafetyQLearning


# ============================================================================
# CREATE APP FIRST
# ============================================================================
app = FastAPI(
    title="Crowd Safety Simulation API",
    description="AI-Driven Public Infrastructure Simulation Platform",
    version="1.0.0"
)


# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Store active simulations (in production, use Redis/database)
active_simulations: Dict[str, Simulator] = {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def load_scenario(scenario_name: str):
    """Load scenario configuration from JSON file"""
    scenario_path = Path(__file__).parent / "scenarios" / f"{scenario_name}.json"
    
    if not scenario_path.exists():
        # Fallback to built-in scenarios
        if scenario_name in SCENARIOS:
            return None  # Will use SCENARIOS dict
        raise FileNotFoundError(f"Scenario {scenario_name} not found")
    
    with open(scenario_path, 'r') as f:
        return json.load(f)


# ✅ NEW: Apply triggers to simulation
def apply_triggers(sim, current_step):
    """Apply active triggers to simulation"""
    active_triggers = []
    
    for trigger in sim.get('triggers', []):
        trigger_step = trigger.get('step', 0)
        
        # Check if trigger is active (within range)
        if trigger_step <= current_step <= trigger_step + 50:
            active_triggers.append(trigger)
            
            # Apply trigger effects based on type
            trigger_type = trigger.get('type')
            affected_zone = trigger.get('affectedZone')
            params = trigger.get('parameters', {})
            
            if affected_zone in sim['digital_twin']['zones']:
                # Get current zone data
                zone = sim['digital_twin']['zones'][affected_zone]
                
                # Apply different effects based on trigger type
                if trigger_type == 'fire':
                    # Fire: People rush to exits
                    severity = params.get('severity', 5.0)
                    zone['panic_multiplier'] = 1 + (severity / 10)
                    
                elif trigger_type == 'vip_delay':
                    # VIP Delay: Entry blocked temporarily
                    delay_minutes = params.get('delay', 30)
                    if current_step < trigger_step + delay_minutes:
                        zone['entry_blocked'] = True
                    else:
                        zone['entry_blocked'] = False
                        
                elif trigger_type == 'explosion':
                    # Explosion: Mass panic, everyone rushes
                    radius = params.get('radius', 100)
                    severity = params.get('severity', 9.0)
                    zone['panic_multiplier'] = 2.0 + (severity / 5)
                    
                elif trigger_type == 'crowd_surge':
                    # Crowd Surge: Sudden density increase
                    surge_intensity = params.get('intensity', 500)
                    zone['surge_agents'] = surge_intensity
                    
                elif trigger_type == 'infrastructure_failure':
                    # Infrastructure: Exit blocked
                    affected_exits = params.get('affectedExits', [])
                    zone['blocked_exits'] = affected_exits
                    
                elif trigger_type == 'weather':
                    # Weather: Slows movement
                    severity = params.get('severity', 5.0)
                    zone['weather_slowdown'] = severity / 10
                    
                elif trigger_type == 'security_threat':
                    # Security: Area evacuation
                    severity = params.get('severity', 7.0)
                    zone['evacuation_mode'] = True
                    zone['panic_multiplier'] = 1.5
                    
                elif trigger_type == 'medical_emergency':
                    # Medical: Area partially blocked
                    zone['partial_blockage'] = 0.3  # 30% capacity reduction
                    
                elif trigger_type == 'power_outage':
                    # Power outage: Confusion, slower movement
                    zone['visibility_reduced'] = True
                    zone['panic_multiplier'] = 1.3
    
    return active_triggers


# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.get("/")
def root():
    return {
        "message": "Crowd Safety Simulation API",
        "version": "1.0.0",
        "endpoints": {
            "scenarios": "/scenarios",
            "create_simulation": "/simulation/create",
            "step_simulation": "/simulation/step",
            "get_state": "/simulation/{simulation_id}/state",
            "compare": "/simulation/compare"
        }
    }



@app.get("/scenarios")
async def get_scenarios():
    """Get available scenarios from both built-in and JSON files"""
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenarios = []
    
    # Load from JSON files if scenarios folder exists
    if scenarios_dir.exists():
        scenario_files = scenarios_dir.glob("*.json")
        
        for file in scenario_files:
            try:
                with open(file, 'r') as f:
                    config = json.load(f)
                    scenarios.append({
                        "id": file.stem,
                        "name": config.get("name", file.stem),
                        "description": config.get("description", ""),
                        "source": "file"
                    })
            except Exception as e:
                print(f"Error loading {file}: {e}")
    
    # Add built-in scenarios
    for scenario_id in SCENARIOS.keys():
        # Check if not already added from file
        if not any(s["id"] == scenario_id for s in scenarios):
            descriptions = {
                "stadium_exit": "Stadium evacuation after event (600-1200 agents)",
                "railway_station": "Railway station during peak hours (150-400 agents)"
            }
            scenarios.append({
                "id": scenario_id,
                "name": scenario_id.replace("_", " ").title(),
                "description": descriptions.get(scenario_id, "Built-in scenario"),
                "source": "built-in"
            })
    
    return {"scenarios": scenarios}



@app.post("/simulation/create")
def create_simulation(request: SimulationRequest):
    """Create a new simulation instance with continuous spawning"""
    try:
        if request.scenario not in SCENARIOS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown scenario. Available: {list(SCENARIOS.keys())}"
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
        active_simulations[sim_id] = simulator
        
        initial_state = simulator.get_simulation_state()
        
        return {
            "simulation_id": sim_id,
            "message": f"Simulation created with {total_agents} agents spawning over {spawn_duration}s",
            "initial_state": initial_state
        }
        
    except Exception as e:
        print(f"Error creating simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/simulation/step")
def step_simulation(request: SimulationStepRequest):
    """Advance simulation by specified number of steps"""
    sim_id = request.simulation_id
    
    if sim_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[sim_id]
    
    try:
        states = []
        for _ in range(request.steps):
            state = simulator.step()
            states.append(state)
        
        return {
            "simulation_id": sim_id,
            "steps_executed": request.steps,
            "current_state": states[-1] if states else None,
            "history": states if request.steps > 1 else None
        }
    
    except Exception as e:
        print(f"❌ Error in /simulation/step: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Simulation step failed: {str(e)}")




@app.get("/simulation/{simulation_id}/state")
def get_simulation_state(simulation_id: str):
    """Get current state of a simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]
    return simulator.get_simulation_state()



@app.post("/simulation/{simulation_id}/reset")
def reset_simulation(simulation_id: str):
    """Reset simulation to initial state"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]
    simulator.reset()
    
    return {
        "simulation_id": simulation_id,
        "message": "Simulation reset successfully",
        "state": simulator.get_simulation_state()
    }



@app.delete("/simulation/{simulation_id}")
def delete_simulation(simulation_id: str):
    """Delete a simulation instance"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    del active_simulations[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "message": "Simulation deleted successfully"
    }



@app.get("/simulation/{simulation_id}/graph")
def get_graph_structure(simulation_id: str):
    """Get digital twin graph structure for visualization"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]
    twin = simulator.twin
    
    # Format graph for frontend visualization
    nodes = []
    for node_id, data in twin.node_data.items():
        nodes.append({
            "id": node_id,
            "x": data["position"][0],
            "y": data["position"][1],
            "type": data["type"],
            "capacity": data["capacity"],
            "area_m2": data["area_m2"]
        })
    
    edges = []
    for (from_node, to_node), data in twin.edge_data.items():
        edges.append({
            "from": from_node,
            "to": to_node,
            "width": data["width_m"],
            "capacity": data["flow_capacity"]
        })
    
    return {
        "nodes": nodes,
        "edges": edges
    }



@app.post("/simulation/compare")
def compare_simulations(request: SimulationRequest):
    """Run both baseline and RL-optimized simulations for comparison"""
    # Load trained RL model
    agent = CrowdSafetyQLearning()
    try:
        agent.load_model("models/stadium_rl_model.pkl")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, 
            detail="RL model not found. Please train the model first by running: python train_model.py"
        )
    
    # Validate scenario
    if request.scenario not in SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario. Available: {list(SCENARIOS.keys())}"
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
        "sample_actions": report["actions_taken"][:10],
        "baseline_history": baseline.get("history", []),
        "optimized_history": optimized.get("history", [])
    }


@app.get("/simulation/{simulation_id}/venue-status")
def get_venue_status(simulation_id: str):
    """Get real-time venue capacity and recommendations"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]
    state = simulator.get_simulation_state()
    
    # Calculate capacity dynamically
    total_capacity = 0
    for node_id, node_data in simulator.twin.node_data.items():
        total_capacity += node_data.get("capacity", 0)
    
    if total_capacity == 0:
        total_area = sum(n.get("area_m2", 0) 
                        for n in simulator.twin.node_data.values())
        total_capacity = int(total_area * 2)
    
    # Calculate node densities
    node_densities = {}
    nodes_data = state.get('nodes', {})
    
    # Count active agents correctly
    active_agents = 0
    
    for node_id, node_state in nodes_data.items():
        twin_node = simulator.twin.node_data.get(node_id, {})
        area_m2 = twin_node.get('area_m2', 1)
        current_count = node_state.get('current_count', 0)
        density = current_count / area_m2 if area_m2 > 0 else 0
        node_densities[node_id] = density
        
        if not node_id.startswith('exit'):
            active_agents += current_count
    
    # Generate recommendations
    recommendations = []
    danger_threshold = 4.0
    warning_threshold = 3.0
    
    for node_id, density in node_densities.items():
        if density > danger_threshold:
            recommendations.append({
                "priority": "CRITICAL",
                "location": node_id.replace('_', ' ').title(),
                "action": "CLOSE_TEMPORARILY",
                "reason": f"Density {density:.1f} p/m² exceeds danger threshold",
                "recommendation": f"Close {node_id} temporarily and reroute",
                "color": "red"
            })
        elif density > warning_threshold:
            recommendations.append({
                "priority": "WARNING",
                "location": node_id.replace('_', ' ').title(),
                "action": "REDUCE_FLOW",
                "reason": f"Density {density:.1f} p/m² approaching danger",
                "recommendation": f"Reduce inflow to {node_id} by 30%",
                "color": "orange"
            })
    
    recommendations.sort(key=lambda x: 0 if x['priority'] == 'CRITICAL' else 1)
    
    occupancy_percent = (active_agents / total_capacity * 100) if total_capacity > 0 else 0
    
    return {
        "venue_status": {
            "name": "Stadium",
            "capacity": total_capacity,
            "current_occupancy": max(0, active_agents),
            "occupancy_percent": max(0, occupancy_percent),
            "status": "FULL" if occupancy_percent >= 100 else "AVAILABLE"
        },
        "recommendations": recommendations[:5],
        "timestamp": state.get('time', 0)
    }


@app.post("/simulation/{simulation_id}/execute-action")
def execute_action(simulation_id: str, action: dict):
    """Execute a safety recommendation action"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator = active_simulations[simulation_id]
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
                    alt_path = simulator.twin.get_shortest_path(
                        agent.current_node, 
                        agent.goal_node
                    )
                    if alt_path:
                        agent.set_path(alt_path)
                        rerouted_count += 1
            
            return {
                "status": "executed",
                "action": "CLOSE_NODE",
                "target": target_node,
                "duration": duration,
                "agents_rerouted": rerouted_count,
                "expires_at": expiration_time
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
            "agents_affected": affected_count
        }
    
    elif action_type == "REROUTE":
        exit_nodes = [n for n, data in simulator.twin.node_data.items() 
                      if data["type"] == "exit" and n != target_node]
        
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
            "agents_rerouted": rerouted_count
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action type: {action_type}")


# ============================================================================
# ✅ SCENARIO BUILDER ENDPOINTS
# ============================================================================

# backend/main.py

@app.post("/simulation/create-custom")
async def create_custom_simulation(request: dict):
    """Create simulation from Scenario Builder"""
    try:
        venue_data = request.get('venue')
        event_config = request.get('event')
        triggers = request.get('triggers', [])
        num_agents = request.get('num_agents', 30000)
        
        # Create digital twin from venue data
        zones = {}
        for zone in venue_data['zones']:
            zones[zone['id']] = {
                'capacity': zone['capacity'],
                'area': zone['area'],
                'type': zone.get('type', 'regular'),
                'panic_multiplier': 1.0,
                'surge_agents': 0,
                'entry_blocked': False,
                'blocked_exits': []
            }
        
        # Create graph structure
        graph = {}
        for conn in venue_data['connections']:
            if conn['from'] not in graph:
                graph[conn['from']] = []
            graph[conn['from']].append(conn['to'])
            
            if conn['to'] not in graph:
                graph[conn['to']] = []
            graph[conn['to']].append(conn['from'])
        
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
        simulations[sim_id] = {
            'digital_twin': {
                'zones': zones,
                'graph': graph,
                'entries': venue_data['entries'],
                'exits': venue_data['exits']
            },
            'event_config': event_config,
            'triggers': triggers,
            'current_step': 0,
            'agents': [],
            'stats': {
                'active_agents': 0,
                'reached_goal': 0,
                'max_density': 0,
                'stampedes': 0
            },
            'applied_interventions': [],
            'ai_actions_log': [],
            # ✅ NEW: Spawn configuration
            'spawn_config': {
                'total_agents': num_agents,
                'spawn_duration': spawn_duration,
                'spawned_count': 0,
                'spawn_rate': num_agents / spawn_duration  # Agents per step
            }
        }
        
        return {
            'simulation_id': sim_id,
            'status': 'created',
            'message': f'Simulation created: {num_agents} agents will arrive over {spawn_duration} steps (~{spawn_duration/2} minutes)',
            'spawn_info': {
                'total': num_agents,
                'duration_steps': spawn_duration,
                'duration_minutes': spawn_duration / 2,
                'rate_per_step': int(num_agents / spawn_duration)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# backend/main.py

@app.post("/simulation/{simulation_id}/step-custom")
async def step_custom_simulation(simulation_id: str):
    """Step custom simulation forward with trigger support"""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = simulations[simulation_id]
    sim['current_step'] += 1
    
    # ✅ NEW: SPAWN AGENTS GRADUALLY
    spawn_config = sim.get('spawn_config', {})
    if spawn_config:
        total_agents = spawn_config['total_agents']
        spawn_duration = spawn_config['spawn_duration']
        spawned_count = spawn_config['spawned_count']
        spawn_rate = spawn_config['spawn_rate']
        
        # Calculate how many agents to spawn this step
        if sim['current_step'] <= spawn_duration and spawned_count < total_agents:
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
                entry = random.choice(sim['digital_twin']['entries'])
                exit_zone = random.choice(sim['digital_twin']['exits'])
                
                agent = {
                    'id': agent_id,
                    'position': entry,
                    'goal': exit_zone,
                    'reached': False,
                    'spawn_step': sim['current_step']
                }
                sim['agents'].append(agent)
            
            # Update spawn count
            spawn_config['spawned_count'] += agents_this_step
    
    # Apply triggers
    active_triggers = apply_triggers(sim, sim['current_step'])
    
    # Calculate zone densities with trigger effects
    zone_data = {}
    ai_actions_taken = []
    
    for zone_id in sim['digital_twin']['zones'].keys():
        agents_in_zone = [a for a in sim['agents'] 
                         if a['position'] == zone_id and not a['reached']]
        
        zone = sim['digital_twin']['zones'][zone_id]
        zone_area = zone['area']
        
        # Base agent count
        agent_count = len(agents_in_zone)
        
        # ADD: Surge agents from triggers
        surge_agents = zone.get('surge_agents', 0)
        if surge_agents > 0:
            agent_count += surge_agents
            zone['surge_agents'] = max(0, surge_agents - 10)
        
        # Calculate density
        density = agent_count / zone_area if zone_area > 0 else 0
        
        # APPLY: Panic multiplier from triggers
        panic_mult = zone.get('panic_multiplier', 1.0)
        density = density * panic_mult
        
        # Decay panic over time
        if panic_mult > 1.0:
            zone['panic_multiplier'] = max(1.0, panic_mult - 0.05)
        
        # ✅ AI INTERVENTION: More aggressive response
        if density > 5.0 and not zone.get('ai_intervention_applied', False):
            intervention_action = None
            
            if density > 8.0:
                # Critical: EMERGENCY CLOSE
                zone['entry_blocked'] = True
                zone['ai_intervention_applied'] = True
                intervention_action = {
                    'step': sim['current_step'],
                    'zone': zone_id,
                    'action': 'EMERGENCY_CLOSE',
                    'reason': f'Critical density {density:.1f} p/m²',
                    'severity': 'CRITICAL'
                }
            elif density > 6.5:
                # High: REDUCE FLOW
                zone['flow_reduction'] = 0.5
                zone['ai_intervention_applied'] = True
                intervention_action = {
                    'step': sim['current_step'],
                    'zone': zone_id,
                    'action': 'REDUCE_FLOW',
                    'reason': f'High density {density:.1f} p/m²',
                    'severity': 'HIGH'
                }
            elif density > 5.0:
                # Moderate: WARNING
                intervention_action = {
                    'step': sim['current_step'],
                    'zone': zone_id,
                    'action': 'WARNING_ISSUED',
                    'reason': f'Elevated density {density:.1f} p/m²',
                    'severity': 'MODERATE'
                }
            
            if intervention_action:
                ai_actions_taken.append(intervention_action)
                
                if 'ai_actions_log' not in sim:
                    sim['ai_actions_log'] = []
                sim['ai_actions_log'].append(intervention_action)
        
        # Reset AI intervention flag if density drops
        if density < 3.0 and zone.get('ai_intervention_applied', False):
            zone['ai_intervention_applied'] = False
            zone['entry_blocked'] = False
            zone['flow_reduction'] = 1.0
        
        zone_data[zone_id] = {
            'density': density,
            'agent_count': agent_count,
            'speed': 1.0 / panic_mult,
            'flow_rate': 0.5 / panic_mult,
            'panic_level': panic_mult - 1.0,
            'is_blocked': zone.get('entry_blocked', False),
            'ai_protected': zone.get('ai_intervention_applied', False)
        }
    
    # Move agents (with AI intervention effects)
    for agent in sim['agents']:
        if not agent['reached'] and agent['position'] != agent['goal']:
            current_zone = sim['digital_twin']['zones'].get(agent['position'], {})
            
            # AI intervention: Block entry
            if current_zone.get('entry_blocked', False):
                continue
            
            # AI intervention: Slow down flow
            flow_reduction = current_zone.get('flow_reduction', 1.0)
            if random.random() > flow_reduction:
                continue
            
            # Check if exit is blocked
            blocked_exits = current_zone.get('blocked_exits', [])
            
            if agent['position'] in sim['digital_twin']['graph']:
                next_positions = sim['digital_twin']['graph'][agent['position']]
                
                available_positions = [p for p in next_positions 
                                      if p not in blocked_exits]
                
                if not available_positions:
                    continue
                
                if agent['goal'] in available_positions:
                    agent['position'] = agent['goal']
                    agent['reached'] = True
                else:
                    agent['position'] = random.choice(available_positions)
    
    # Update stats
    active = len([a for a in sim['agents'] if not a['reached']])
    reached = len([a for a in sim['agents'] if a['reached']])
    max_density = max([z['density'] for z in zone_data.values()]) if zone_data else 0
    
    # Count stampedes (density > 8.5)
    stampedes = len([z for z in zone_data.values() if z['density'] > 8.5])
    
    sim['stats'] = {
        'active_agents': active,
        'reached_goal': reached,
        'max_density': max_density,
        'stampedes': stampedes
    }
    
    return {
        'current_step': sim['current_step'],
        'zone_data': zone_data,
        'active_agents': active,
        'reached_goal': reached,
        'max_density': max_density,
        'stampedes': stampedes,
        'active_triggers': [{'name': t.get('name'), 'type': t.get('type')} 
                           for t in active_triggers],
        'ai_actions_taken': ai_actions_taken,
        'total_ai_actions': len(sim.get('ai_actions_log', [])),
        'spawn_progress': {  # ✅ NEW: Show spawn progress
            'spawned': spawn_config.get('spawned_count', 0),
            'total': spawn_config.get('total_agents', 0),
            'remaining': spawn_config.get('total_agents', 0) - spawn_config.get('spawned_count', 0)
        }
    }


# ✅ NEW: Get full AI action log
@app.get("/simulation/{simulation_id}/ai-actions")
async def get_ai_actions(simulation_id: str):
    """Get all AI actions taken during simulation"""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = simulations[simulation_id]
    actions_log = sim.get('ai_actions_log', [])
    
    return {
        'actions': actions_log,
        'total_actions': len(actions_log)
    }


@app.get("/simulation/{simulation_id}/predictions")
async def get_predictions(simulation_id: str):
    """Get stampede predictions for simulation"""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Use stampede predictor from Phase 1
    from ai.stampede_predictor import StampedePredictor, DensitySnapshot
    
    predictor = StampedePredictor()
    sim = simulations[simulation_id]
    
    predictions = []
    
    # Get zone data from last step
    for zone_id in sim['digital_twin']['zones'].keys():
        agents_in_zone = [a for a in sim['agents'] if a['position'] == zone_id and not a['reached']]
        zone_area = sim['digital_twin']['zones'][zone_id]['area']
        density = len(agents_in_zone) / zone_area if zone_area > 0 else 0
        
        # Create snapshot
        snapshot = DensitySnapshot(
            zone_id=zone_id,
            timestamp=sim['current_step'],
            density=density,
            agent_count=len(agents_in_zone),
            area=zone_area,
            flow_rate=0.5,
            avg_speed=1.0
        )
        
        predictor.update_data(snapshot)
        
        # Get prediction
        pred = predictor.predict(zone_id)
        if pred and pred.risk_level.value not in ['safe', 'low']:
            predictions.append({
                'zone_id': pred.zone_id,
                'risk_level': pred.risk_level.value,
                'probability': pred.probability,
                'time_to_stampede': pred.time_to_stampede,
                'current_density': pred.current_density,
                'predicted_peak_density': pred.predicted_peak_density,
                'confidence': pred.confidence
            })
    
    return {'predictions': predictions}



@app.get("/simulation/{simulation_id}/cascades")
async def get_cascades(simulation_id: str):
    """Get active cascades"""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Simplified for now
    return {'cascades': []}



@app.get("/simulation/{simulation_id}/interventions")
async def get_interventions(simulation_id: str):
    """Get AI intervention recommendations"""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Use intervention engine from Phase 2
    from ai.intervention_engine import InterventionEngine
    from ai.stampede_predictor import StampedePrediction, RiskLevel
    
    engine = InterventionEngine()
    sim = simulations[simulation_id]
    
    interventions = []
    
    # Check each zone for high density
    for zone_id in sim['digital_twin']['zones'].keys():
        agents_in_zone = [a for a in sim['agents'] if a['position'] == zone_id and not a['reached']]
        zone_area = sim['digital_twin']['zones'][zone_id]['area']
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
                predicted_peak_density=density + 1.5
            )
            
            # Get intervention plan
            plan = engine.recommend_for_prediction(prediction, sim['current_step'])
            
            if plan:
                interventions.append({
                    'intervention_id': plan.primary_option.intervention_id,
                    'urgency': plan.primary_option.urgency.value,
                    'action_description': plan.primary_option.action_description,
                    'expected_lives_saved': plan.primary_option.expected_lives_saved,
                    'success_probability': plan.primary_option.success_probability,
                    'deadline_step': plan.primary_option.deadline_step,
                    'resource_cost': plan.primary_option.resource_cost,
                    'reasoning': plan.primary_option.reasoning
                })
    
    return {'interventions': interventions}



@app.post("/simulation/{simulation_id}/intervention")
async def apply_intervention(simulation_id: str, request: dict):
    """Apply an intervention and track it"""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    intervention_id = request.get('intervention_id')
    sim = simulations[simulation_id]
    
    # ✅ Track applied interventions
    sim['applied_interventions'].append({
        'intervention_id': intervention_id,
        'applied_at_step': sim['current_step'],
        'timestamp': time.time()
    })
    
    # ✅ APPLY INTERVENTION EFFECTS
    # Example: Close entry to zone
    if 'close_entry' in intervention_id:
        zone_id = intervention_id.split('_')[-1]  # Extract zone ID
        if zone_id in sim['digital_twin']['zones']:
            sim['digital_twin']['zones'][zone_id]['entry_blocked'] = True
    
    # Example: Open alternate exit
    elif 'open_exit' in intervention_id:
        zone_id = intervention_id.split('_')[-1]
        if zone_id in sim['digital_twin']['zones']:
            sim['digital_twin']['zones'][zone_id]['blocked_exits'] = []
    
    # Example: Deploy security
    elif 'deploy_security' in intervention_id:
        zone_id = intervention_id.split('_')[-1]
        if zone_id in sim['digital_twin']['zones']:
            # Reduce panic
            sim['digital_twin']['zones'][zone_id]['panic_multiplier'] = 1.0
    
    print(f"✅ Applied intervention {intervention_id} to simulation {simulation_id}")
    
    return {
        'status': 'applied',
        'message': f'Intervention {intervention_id} applied successfully',
        'applied_count': len(sim['applied_interventions'])
    }


# ✅ NEW: Get applied interventions
@app.get("/simulation/{simulation_id}/applied-interventions")
async def get_applied_interventions(simulation_id: str):
    """Get list of applied interventions"""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = simulations[simulation_id]
    applied = sim.get('applied_interventions', [])
    
    return {
        'interventions': applied,
        'total_applied': len(applied)
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
