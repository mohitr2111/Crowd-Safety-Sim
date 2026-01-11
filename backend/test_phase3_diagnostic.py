"""
PHASE 3: Diagnostic Test - Check densities and recommendation generation
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_phase3_diagnostic():
    """Diagnostic test to check densities and recommendations"""
    print("="*70)
    print("Phase 3 Diagnostic Test")
    print("="*70)
    print()
    
    # Step 1: Create simulation
    print("1. Creating simulation...")
    create_response = requests.post(
        f"{BASE_URL}/simulation/create",
        json={
            "scenario": "stadium_exit",
            "spawn_config": [
                {"start": "zone_north", "goal": "exit_main", "count": 1000, "type": "normal"},
                {"start": "zone_south", "goal": "exit_main", "count": 900, "type": "normal"},
            ],
            "time_step": 1.0
        }
    )
    
    if create_response.status_code != 200:
        print(f"[ERROR] Failed to create: {create_response.text}")
        return False
    
    sim_data = create_response.json()
    simulation_id = sim_data["simulation_id"]
    print(f"[OK] Simulation: {simulation_id}")
    print()
    
    # Step 2: Run simulation steps
    print("2. Running simulation (40 steps)...")
    for i in range(40):
        step_response = requests.post(
            f"{BASE_URL}/simulation/step",
            json={"simulation_id": simulation_id, "steps": 1}
        )
        if step_response.status_code != 200:
            print(f"[ERROR] Step failed: {step_response.status_code}")
            return False
        time.sleep(0.02)
    
    print("[OK] Simulation complete")
    print()
    
    # Step 3: Get state and analyze
    print("3. Getting simulation state...")
    state_response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/state")
    
    if state_response.status_code != 200:
        print(f"[ERROR] Failed to get state: {state_response.status_code}")
        return False
    
    state = state_response.json()
    print(f"[OK] State retrieved")
    print(f"    Keys: {list(state.keys())}")
    print()
    
    # Step 4: Check nodes data
    print("4. Analyzing nodes data...")
    nodes_data = state.get("nodes", {})
    print(f"    Node count: {len(nodes_data)}")
    
    # Calculate densities manually
    print("    Node densities:")
    node_densities = {}
    
    for node_id, node_state in nodes_data.items():
        current_count = node_state.get("current_count", 0)
        # We need area from digital twin, but for now just show counts
        print(f"      {node_id}: {current_count} agents")
        node_densities[node_id] = current_count
    
    print()
    
    # Step 5: Get stadium status (this should trigger recommendations)
    print("5. Getting stadium status (triggers Phase 3)...")
    status_response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/stadium-status")
    
    if status_response.status_code != 200:
        print(f"[ERROR] Failed: {status_response.status_code}")
        print(f"    Response: {status_response.text[:300]}")
        return False
    
    status_data = status_response.json()
    print(f"[OK] Status retrieved")
    
    recommendations = status_data.get("recommendations", [])
    phase3_stats = status_data.get("phase3_stats", {})
    debug = status_data.get("debug", {})
    
    print(f"    Recommendations: {len(recommendations)}")
    print(f"    Auto-executed: {phase3_stats.get('auto_executed', 0)}")
    print(f"    Pending: {phase3_stats.get('pending_count', 0)}")
    print(f"    Max density: {debug.get('max_density', 0):.2f} p/m²")
    print(f"    Active agents: {debug.get('active_agents', 0)}")
    print()
    
    # Step 6: Show recommendations
    if recommendations:
        print("6. Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"    {i}. {rec.get('priority')}: {rec.get('location')} - {rec.get('action')}")
            print(f"       Reason: {rec.get('reason')}")
            proc_result = rec.get("processing_result", {})
            status = proc_result.get("status", "UNKNOWN")
            print(f"       Processing: {status}")
    else:
        print("6. No recommendations generated")
        print("    This means densities did not exceed thresholds:")
        print("    - Warning threshold: 3.0 p/m²")
        print("    - Danger threshold: 4.0 p/m²")
    print()
    
    # Step 7: Check pending actions
    print("7. Checking pending actions...")
    pending_response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/pending-actions")
    
    if pending_response.status_code == 200:
        pending_data = pending_response.json()
        pending_actions = pending_data.get("pending_actions", [])
        print(f"[OK] Pending actions: {len(pending_actions)}")
    else:
        print(f"[WARN] Failed: {pending_response.status_code}")
    print()
    
    # Summary
    print("="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    print(f"Recommendations: {len(recommendations)}")
    print(f"Max density: {debug.get('max_density', 0):.2f} p/m²")
    print(f"Phase 3 integration: {'WORKING' if 'phase3_stats' in status_data else 'MISSING'}")
    print()
    
    if len(recommendations) == 0:
        print("NOTE: No recommendations generated because densities are below thresholds.")
        print("This is expected behavior - the system only recommends interventions")
        print("when densities exceed safe levels (3.0 p/m² warning, 4.0 p/m² danger).")
        print()
        print("To test Phase 3 with recommendations, you would need:")
        print("1. Higher agent counts")
        print("2. Smaller node areas (more congestion)")
        print("3. Trigger events (fire, gate malfunction)")
        print("4. More simulation steps to allow density to build")
    print()
    
    return True


if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("[ERROR] Server not responding. Start server: cd backend && python main.py")
            exit(1)
        
        test_phase3_diagnostic()
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Start server: cd backend && python main.py")
        exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

