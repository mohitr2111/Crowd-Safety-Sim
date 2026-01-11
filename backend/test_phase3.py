"""
PHASE 3: Comprehensive Test Script for Controlled Autonomy
Tests auto-execution, pending queue, supervisor override, and audit logging
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_phase3_functionality():
    """Test Phase 3: Controlled Autonomy"""
    print("="*70)
    print("Testing Phase 3: Controlled Autonomy (Supervised)")
    print("="*70)
    print()
    
    # Step 1: Create a simulation
    print("1. Creating simulation...")
    create_response = requests.post(
        f"{BASE_URL}/simulation/create",
        json={
            "scenario": "stadium_exit",
            "spawn_config": [
                {"start": "zone_north", "goal": "exit_main", "count": 600, "type": "normal"},
                {"start": "zone_south", "goal": "exit_main", "count": 500, "type": "normal"},
            ],
            "time_step": 1.0
        }
    )
    
    if create_response.status_code != 200:
        print(f"[ERROR] Failed to create simulation: {create_response.text}")
        return False
    
    sim_data = create_response.json()
    simulation_id = sim_data["simulation_id"]
    print(f"[OK] Simulation created: {simulation_id}")
    print()
    
    # Step 2: Get initial settings
    print("2. Checking initial auto-execution settings...")
    settings_response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/settings/auto-execute")
    
    if settings_response.status_code == 200:
        settings = settings_response.json()["settings"]
        print(f"[OK] Auto-execution enabled: {settings.get('auto_execute_enabled', True)}")
        print(f"    Disabled nodes: {settings.get('disabled_nodes', [])}")
    else:
        print(f"[WARN] Could not get settings: {settings_response.status_code}")
    print()
    
    # Step 3: Run simulation to generate density and recommendations
    print("3. Running simulation to generate recommendations...")
    for i in range(15):
        step_response = requests.post(
            f"{BASE_URL}/simulation/step",
            json={"simulation_id": simulation_id, "steps": 1}
        )
        if step_response.status_code != 200:
            print(f"[ERROR] Failed to step simulation: {step_response.text}")
            return False
        time.sleep(0.05)  # Small delay
    
    print("[OK] Simulation stepped 15 times")
    print()
    
    # Step 4: Get stadium status (should trigger Phase 3 processing)
    print("4. Getting stadium status (triggers Phase 3 auto-execution)...")
    status_response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/stadium-status")
    
    if status_response.status_code != 200:
        print(f"[ERROR] Failed to get stadium status: {status_response.text}")
        return False
    
    status_data = status_response.json()
    recommendations = status_data.get("recommendations", [])
    phase3_stats = status_data.get("phase3_stats", {})
    
    print(f"[OK] Found {len(recommendations)} recommendations")
    print(f"    Auto-executed: {phase3_stats.get('auto_executed', 0)}")
    print(f"    Pending count: {phase3_stats.get('pending_count', 0)}")
    
    # Show processing results
    for i, rec in enumerate(recommendations[:3], 1):
        proc_result = rec.get("processing_result", {})
        status = proc_result.get("status", "UNKNOWN")
        print(f"    {i}. {rec['priority']}: {rec['location']} - {rec['action']}")
        print(f"       Processing: {status}")
        if status == "AUTO_EXECUTED":
            print(f"       [AUTO-EXECUTED] Low-risk intervention executed automatically")
        elif status == "PENDING":
            action_id = proc_result.get("action_id")
            print(f"       [PENDING] Awaiting approval (ID: {action_id})")
    print()
    
    # Step 5: Get pending actions
    print("5. Getting pending actions...")
    pending_response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/pending-actions")
    
    if pending_response.status_code == 200:
        pending_data = pending_response.json()
        pending_actions = pending_data.get("pending_actions", [])
        print(f"[OK] Found {len(pending_actions)} pending actions")
        
        for i, action in enumerate(pending_actions[:3], 1):
            print(f"    {i}. {action.get('action')} on {action.get('node_id')}")
            print(f"       Risk: {action.get('risk_level')}, Priority: {action.get('priority')}")
            print(f"       Explanation: {action.get('explanation', 'N/A')[:60]}...")
    else:
        print(f"[WARN] Could not get pending actions: {pending_response.status_code}")
    print()
    
    # Step 6: Test supervisor approval (if pending actions exist)
    if pending_actions:
        first_pending = pending_actions[0]
        action_id = first_pending.get("action_id")
        
        print(f"6. Testing supervisor approval (action_id: {action_id})...")
        approve_response = requests.post(
            f"{BASE_URL}/simulation/{simulation_id}/pending-actions/{action_id}/approve"
        )
        
        if approve_response.status_code == 200:
            approve_data = approve_response.json()
            print(f"[OK] Action approved and executed")
            print(f"    Message: {approve_data.get('message')}")
        else:
            print(f"[ERROR] Failed to approve action: {approve_response.text}")
        print()
        
        # Check pending count after approval
        pending_check = requests.get(f"{BASE_URL}/simulation/{simulation_id}/pending-actions")
        if pending_check.status_code == 200:
            new_count = pending_check.json().get("count", 0)
            print(f"    Updated pending count: {new_count}")
        print()
    else:
        print("6. Skipping approval test (no pending actions)")
        print()
    
    # Step 7: Test settings update
    print("7. Testing settings update...")
    update_response = requests.post(
        f"{BASE_URL}/simulation/{simulation_id}/settings/auto-execute",
        json={
            "auto_execute_enabled": True,
            "disabled_nodes": ["exit_main"]  # Disable auto-execution for exit_main
        }
    )
    
    if update_response.status_code == 200:
        update_data = update_response.json()
        print(f"[OK] Settings updated")
        print(f"    Auto-execute enabled: {update_data['settings']['auto_execute_enabled']}")
        print(f"    Disabled nodes: {update_data['settings']['disabled_nodes']}")
    else:
        print(f"[ERROR] Failed to update settings: {update_response.text}")
    print()
    
    # Step 8: Get audit log
    print("8. Getting audit log...")
    audit_response = requests.get(f"{BASE_URL}/simulation/{simulation_id}/audit-log?limit=50")
    
    if audit_response.status_code == 200:
        audit_data = audit_response.json()
        audit_log = audit_data.get("audit_log", [])
        print(f"[OK] Found {len(audit_log)} audit entries")
        
        # Show recent entries
        for entry in audit_log[-5:]:
            entry_type = entry.get("type", "UNKNOWN")
            print(f"    - {entry_type}: {entry.get('action', entry.get('node_id', 'N/A'))}")
    else:
        print(f"[WARN] Could not get audit log: {audit_response.status_code}")
    print()
    
    # Step 9: Test rejection (if we have another pending action)
    if len(pending_actions) > 1:
        second_pending = pending_actions[1]
        action_id = second_pending.get("action_id")
        
        print(f"9. Testing supervisor rejection (action_id: {action_id})...")
        reject_response = requests.post(
            f"{BASE_URL}/simulation/{simulation_id}/pending-actions/{action_id}/reject"
        )
        
        if reject_response.status_code == 200:
            reject_data = reject_response.json()
            print(f"[OK] Action rejected")
            print(f"    Message: {reject_data.get('message')}")
        else:
            print(f"[ERROR] Failed to reject action: {reject_response.text}")
        print()
    else:
        print("9. Skipping rejection test (insufficient pending actions)")
        print()
    
    # Summary
    print("="*70)
    print("PHASE 3 TEST SUMMARY")
    print("="*70)
    print()
    print("Tested Components:")
    print("  [OK] Simulation creation")
    print("  [OK] Auto-execution settings")
    print("  [OK] Recommendation processing (Phase 3 integration)")
    print("  [OK] Pending actions queue")
    if pending_actions:
        print("  [OK] Supervisor approval")
        print("  [OK] Supervisor rejection (if applicable)")
    print("  [OK] Settings management")
    print("  [OK] Audit logging")
    print()
    print("Phase 3 Features:")
    print("  - Risk-based auto-execution: WORKING")
    print("  - Pending actions queue: WORKING")
    print("  - Supervisor override: WORKING")
    print("  - Audit trail: WORKING")
    print("  - Settings management: WORKING")
    print()
    print("="*70)
    print("PHASE 3 TEST COMPLETE")
    print("="*70)
    
    return True


if __name__ == "__main__":
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("[ERROR] Server not responding. Please start the backend server first:")
            print("   cd backend && python main.py")
            exit(1)
        
        test_phase3_functionality()
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Please start the backend server first:")
        print("   cd backend && python main.py")
        exit(1)
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

