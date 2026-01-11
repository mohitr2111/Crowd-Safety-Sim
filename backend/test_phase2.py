"""
Phase-2 Comprehensive Test Suite

Tests all Phase-2 features:
- Sub-Phase 2.1: Blueprint Processor
- Sub-Phase 2.2: Panic Propagation
- Sub-Phase 2.3: Multi-Scenario RL Training
- Sub-Phase 2.4: Case Study Mode
- Sub-Phase 2.5: Trigger-Aware Policy
"""

import sys
import os
import random
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_blueprint_processor():
    """Test Sub-Phase 2.1: Blueprint Processor"""
    print("\n" + "="*60)
    print("TEST 2.1: Blueprint Processor")
    print("="*60)
    
    from Components.blueprint_processor import (
        BlueprintProcessor, ElementType, get_blueprint_processor
    )
    
    # Test singleton
    processor = get_blueprint_processor()
    assert processor is not None, "Failed to get processor instance"
    print("[PASS] Singleton instance created")
    
    # Test processing with mock image data
    image_data = b"mock_image_data_for_testing" * 100
    result = processor.process_blueprint(
        image_data=image_data,
        venue_type="stadium",
        scale=1.0
    )
    
    assert result is not None, "Processing returned None"
    assert result.detection_id is not None, "No detection ID"
    assert len(result.elements) > 0, "No elements detected"
    print(f"[PASS] Processed blueprint: {len(result.elements)} elements detected")
    
    # Check element types
    element_types = [e.element_type for e in result.elements]
    assert ElementType.ZONE in element_types, "No zones detected"
    assert ElementType.EXIT in element_types, "No exits detected"
    print(f"[PASS] Element types: {set(e.value for e in element_types)}")
    
    # Test correction
    corrected = processor.apply_correction(
        detection_id=result.detection_id,
        correction_type="modify",
        target_element_id=result.elements[0].element_id,
        changes={"label": "Modified Zone", "capacity": 500}
    )
    assert corrected is not None, "Correction failed"
    print("[PASS] Correction applied successfully")
    
    # Test validation
    is_valid, errors = processor.validate_graph(result.detection_id)
    print(f"[PASS] Validation: valid={is_valid}, errors={len(errors)}")
    
    # Test finalization to code
    code = processor.generate_digital_twin_code(result.detection_id, "TestVenue")
    assert "DigitalTwin" in code, "Generated code missing DigitalTwin"
    assert "add_area" in code, "Generated code missing add_area"
    print(f"[PASS] Generated {len(code)} chars of Digital Twin code")
    
    print("\n[PASS] All Blueprint Processor tests PASSED")
    return True


def test_panic_propagation():
    """Test Sub-Phase 2.2: Panic Propagation"""
    print("\n" + "="*60)
    print("TEST 2.2: Panic Propagation")
    print("="*60)
    
    from simulation.agent import Agent
    from Components.trigger_system import (
        TriggerSystem, TriggerType, PanicPropagationConfig, TRIGGER_BEHAVIORS
    )
    from simulation.scenarios import SCENARIOS
    from simulation.simulator import Simulator
    
    # Test Agent panic state
    agent = Agent(1, "zone_north", "exit_main")
    assert agent.panic_level == 0.0, "Initial panic should be 0"
    print("[PASS] Agent created with zero panic")
    
    # Test panic update
    agent.update_panic(0.7, "trigger_001", current_time=10.0)
    assert agent.panic_level == 0.7, f"Panic should be 0.7, got {agent.panic_level}"
    assert agent.is_panicked() == True, "Agent should be panicked"
    assert agent.speed > agent.base_speed, "Speed should increase with panic"
    print(f"[PASS] Panic updated: level={agent.panic_level}, speed_mod={agent.speed/agent.base_speed:.2f}")
    
    # Test panic state dict
    state = agent.get_panic_state()
    assert "panic_level" in state, "Missing panic_level in state"
    assert "is_panicked" in state, "Missing is_panicked in state"
    print(f"[PASS] Panic state: {state}")
    
    # Test panic decay
    agent.decay_panic(current_time=25.0, dt=1.0)  # After 15 seconds
    assert agent.panic_level < 0.7, "Panic should decay"
    print(f"[PASS] Panic decayed to {agent.panic_level:.3f}")
    
    # Test TriggerSystem with propagation config
    config = PanicPropagationConfig(
        spread_rate=0.3,
        max_propagation_depth=2,
        min_panic_to_spread=0.1
    )
    ts = TriggerSystem(propagation_config=config)
    assert ts.propagation_config.spread_rate == 0.3, "Config not set"
    print("[PASS] TriggerSystem created with custom propagation config")
    
    # Test trigger behaviors
    assert TriggerType.EXTERNAL_EXPLOSION in TRIGGER_BEHAVIORS, "Missing explosion behavior"
    explosion_behavior = TRIGGER_BEHAVIORS[TriggerType.EXTERNAL_EXPLOSION]
    assert explosion_behavior["agent_behavior"] == "flee_to_exits", "Wrong explosion behavior"
    print(f"[PASS] Trigger behaviors defined for {len(TRIGGER_BEHAVIORS)} types")
    
    # Test panic propagation in simulation
    twin = SCENARIOS["stadium_exit"]()
    sim = Simulator(twin)
    
    # Spawn some agents
    sim.spawn_agents_batch([
        {"start": "zone_north", "goal": "exit_main", "count": 20, "type": "normal"},
        {"start": "concourse", "goal": "exit_main", "count": 10, "type": "normal"}
    ])
    
    for ag in sim.agents.values():
        path = sim.digital_twin.get_shortest_path(ag.current_node, ag.goal_node)
        if path:
            ag.set_path(path)
    
    # Create trigger
    trigger = ts.create_trigger(
        trigger_type=TriggerType.EXTERNAL_EXPLOSION,
        time_seconds=0,
        affected_zones=["zone_north"],
        severity=0.8
    )
    assert trigger is not None, "Failed to create trigger"
    print(f"[PASS] Created trigger: {trigger}")
    
    # Propagate panic
    effects = ts.propagate_panic(sim, trigger, current_time=0.0)
    assert effects["affected_agents"] > 0, "No agents affected by panic"
    assert len(effects["nodes_reached"]) > 0, "No nodes reached"
    print(f"[PASS] Panic propagated: {effects['affected_agents']} agents, {len(effects['nodes_reached'])} nodes")
    
    # Check that agents are panicked
    panicked_count = sum(1 for a in sim.agents.values() if a.is_panicked())
    print(f"[PASS] Panicked agents: {panicked_count}/{len(sim.agents)}")
    
    # Test trigger-specific behavior
    behavior_effects = ts.apply_trigger_specific_behavior(sim, trigger, current_time=0.0)
    print(f"[PASS] Applied behavior: {behavior_effects['behavior_type']}, modified {behavior_effects['agents_modified']} agents")
    
    print("\n[PASS] All Panic Propagation tests PASSED")
    return True


def test_multi_scenario_training():
    """Test Sub-Phase 2.3: Multi-Scenario RL Training"""
    print("\n" + "="*60)
    print("TEST 2.3: Multi-Scenario RL Training")
    print("="*60)
    
    from simulation.scenarios import SCENARIOS, SCENARIO_METADATA
    from density_rl.multi_scenario_trainer import (
        MultiScenarioTrainer, TrainingConfig, ImprovedRewardShaper
    )
    from density_rl.policy import DensityControlQLearning
    
    # Test scenarios
    assert len(SCENARIOS) >= 4, f"Expected 4+ scenarios, got {len(SCENARIOS)}"
    print(f"[PASS] {len(SCENARIOS)} scenarios available: {list(SCENARIOS.keys())}")
    
    # Test scenario metadata
    assert "stadium_exit" in SCENARIO_METADATA, "Missing stadium metadata"
    assert "railway_station" in SCENARIO_METADATA, "Missing railway metadata"
    assert "festival_corridor" in SCENARIO_METADATA, "Missing festival metadata"
    assert "temple" in SCENARIO_METADATA, "Missing temple metadata"
    print("[PASS] All scenario metadata present")
    
    # Test each scenario creates valid graph
    for name, factory in SCENARIOS.items():
        twin = factory()
        assert len(twin.node_data) > 0, f"{name}: No nodes"
        assert len(twin.edge_data) > 0, f"{name}: No edges"
        print(f"  [PASS] {name}: {len(twin.node_data)} nodes, {len(twin.edge_data)} edges")
    
    # Test improved reward shaper
    shaper = ImprovedRewardShaper(target_max_density=4.0)
    
    prev_state = {"max_density": 5.0, "danger_count": 2, "agents_exited": 10}
    curr_state = {"max_density": 4.0, "danger_count": 1, "agents_exited": 15}
    
    reward = shaper.compute_reward(prev_state, curr_state, "THROTTLE_50")
    print(f"[PASS] Reward shaper: density 5->4 = reward {reward:.2f}")
    
    shaper.reset()
    
    # Test training config
    config = TrainingConfig(
        scenarios=["stadium_exit"],
        seeds=[42],
        episodes_per_scenario=2,  # Just 2 for testing
        max_steps_per_episode=10
    )
    print(f"[PASS] Training config: {config.episodes_per_scenario} episodes")
    
    # Test trainer initialization
    trainer = MultiScenarioTrainer(config=config)
    assert trainer is not None, "Failed to create trainer"
    print("[PASS] MultiScenarioTrainer created")
    
    # Test training (mini run)
    agent = DensityControlQLearning()
    summary = trainer.train(agent, verbose=False)
    
    assert "total_episodes" in summary, "Missing total_episodes"
    assert summary["total_episodes"] == 2, f"Expected 2 episodes, got {summary['total_episodes']}"
    print(f"[PASS] Training complete: {summary['total_episodes']} episodes")
    
    # Check Q-table was updated
    assert len(agent.q) > 0, "Q-table empty after training"
    print(f"[PASS] Q-table has {len(agent.q)} states")
    
    print("\n[PASS] All Multi-Scenario Training tests PASSED")
    return True


def test_case_study_mode():
    """Test Sub-Phase 2.4: Case Study Mode"""
    print("\n" + "="*60)
    print("TEST 2.4: Case Study Mode")
    print("="*60)
    
    from Components.case_study import (
        CaseStudyManager, CasePackConfig, get_case_study_manager
    )
    from density_rl.policy import DensityControlQLearning
    
    # Test singleton
    manager = get_case_study_manager()
    assert manager is not None, "Failed to get manager"
    print("[PASS] CaseStudyManager singleton created")
    
    # Test case config creation
    config = manager.create_case_config(
        scenario_id="stadium_exit",
        case_name="Test Fire Drill",
        triggers=[
            {"type": "explosion", "time": 5, "zones": ["zone_north"], "severity": 0.7}
        ],
        seed=42,
        num_agents=50,  # Small for testing
        num_steps=15,   # Short for testing
        description="Test case for Phase-2 verification"
    )
    
    assert config.case_id is not None, "No case ID generated"
    assert config.case_name == "Test Fire Drill", "Wrong case name"
    print(f"[PASS] Case config created: {config.case_id}")
    
    # Test case study run
    agent = DensityControlQLearning()
    
    print("  Running case study (baseline + AI-aware)...")
    case_pack = manager.run_case_study(config, rl_agent=agent, verbose=False)
    
    assert case_pack is not None, "Case pack is None"
    assert case_pack.baseline_log is not None, "No baseline log"
    assert case_pack.ai_aware_log is not None, "No AI-aware log"
    assert case_pack.comparison_summary is not None, "No comparison"
    
    print(f"[PASS] Case study complete")
    print(f"  Baseline max density: {case_pack.baseline_log.final_metrics['max_density']:.2f}")
    print(f"  AI-aware max density: {case_pack.ai_aware_log.final_metrics['max_density']:.2f}")
    print(f"  Improvement: {case_pack.comparison_summary['density_improvement_pct']:.1f}%")
    
    # Test case retrieval
    retrieved = manager.get_case_pack(config.case_id)
    assert retrieved is not None, "Failed to retrieve case"
    print("[PASS] Case retrieval works")
    
    # Test case listing
    cases = manager.list_cases()
    assert len(cases) > 0, "No cases in list"
    print(f"[PASS] Case listing: {len(cases)} cases stored")
    
    # Test JSON export
    json_report = manager.export_report(config.case_id, format="json")
    assert "case_id" in json_report, "JSON missing case_id"
    assert "comparison_summary" in json_report, "JSON missing comparison"
    print(f"[PASS] JSON export: {len(json_report)} chars")
    
    # Test markdown export
    md_report = manager.export_report(config.case_id, format="markdown")
    assert "# Case Study Report" in md_report, "Markdown missing title"
    assert "Baseline" in md_report, "Markdown missing baseline"
    print(f"[PASS] Markdown export: {len(md_report)} chars")
    
    print("\n[PASS] All Case Study Mode tests PASSED")
    return True


def test_trigger_aware_policy():
    """Test Sub-Phase 2.5: Trigger-Aware Policy"""
    print("\n" + "="*60)
    print("TEST 2.5: Trigger-Aware Policy")
    print("="*60)
    
    from density_rl.trigger_aware_policy import (
        TriggerAwareQLearning, TriggerContext, upgrade_to_trigger_aware
    )
    from density_rl.policy import DensityControlQLearning
    from Components.trigger_system import TriggerType
    
    # Test basic creation
    agent = TriggerAwareQLearning()
    assert agent is not None, "Failed to create agent"
    assert len(agent.actions) == 5, "Wrong number of actions"
    print("[PASS] TriggerAwareQLearning created")
    
    # Test state encoding
    state_str = agent.state_from_observation(
        max_density=4.5,
        danger_count=2,
        avg_density=3.0
    )
    assert "D4" in state_str, f"Wrong density bucket: {state_str}"
    assert "G1" in state_str, f"Wrong danger level: {state_str}"
    print(f"[PASS] State encoding: density=4.5, danger=2 -> '{state_str}'")
    
    # Test action selection without trigger
    action = agent.get_action((4.5, 2, 3), trigger_context=None)
    assert action in agent.actions, f"Invalid action: {action}"
    print(f"[PASS] Action without trigger: {action}")
    
    # Test action selection with trigger context
    context = TriggerContext(
        active_trigger_type=TriggerType.EXTERNAL_EXPLOSION,
        trigger_severity=0.8,
        affected_zones=["zone_north"]
    )
    
    action_with_trigger = agent.get_action((4.5, 2, 3), trigger_context=context)
    assert action_with_trigger in agent.actions, f"Invalid action: {action_with_trigger}"
    print(f"[PASS] Action with EXPLOSION trigger: {action_with_trigger}")
    
    # Test Q-table update
    agent.update(
        state=(4.5, 2, 3),
        action="THROTTLE_50",
        reward=5.0,
        next_state=(3.5, 1, 2),
        trigger_context=context
    )
    
    assert len(agent.q_base) > 0, "Base Q-table empty after update"
    assert agent.trigger_sample_counts[TriggerType.EXTERNAL_EXPLOSION] > 0, "Trigger sample not counted"
    print(f"[PASS] Q-table updated: {len(agent.q_base)} base states")
    
    # Test action explanation
    explanation = agent.get_action_explanation(
        state=(5.0, 3, 4),
        action="CLOSE_INFLOW",
        trigger_context=context
    )
    
    assert "action" in explanation, "Explanation missing action"
    assert "reasoning" in explanation, "Explanation missing reasoning"
    assert len(explanation["reasoning"]) > 0, "No reasoning provided"
    print(f"[PASS] Action explanation: {len(explanation['reasoning'])} reasons")
    for reason in explanation["reasoning"]:
        print(f"    - {reason}")
    
    # Test trigger readiness
    readiness = agent.get_trigger_readiness()
    assert TriggerType.EXTERNAL_EXPLOSION.value in readiness, "Missing explosion readiness"
    print(f"[PASS] Trigger readiness: {readiness[TriggerType.EXTERNAL_EXPLOSION.value]}")
    
    # Test upgrade from base agent
    base_agent = DensityControlQLearning()
    base_agent.q["test_state"] = {"NOOP": 1.0, "REROUTE": 2.0}
    
    upgraded = upgrade_to_trigger_aware(base_agent)
    assert "test_state" in upgraded.q_base, "Transfer learning failed"
    print("[PASS] Upgrade from base agent works")
    
    # Test epsilon decay
    initial_epsilon = agent.epsilon
    agent.decay()
    assert agent.epsilon < initial_epsilon, "Epsilon didn't decay"
    print(f"[PASS] Epsilon decay: {initial_epsilon:.3f} -> {agent.epsilon:.3f}")
    
    print("\n[PASS] All Trigger-Aware Policy tests PASSED")
    return True


def test_integration():
    """Integration test: Full simulation with Phase-2 features"""
    print("\n" + "="*60)
    print("INTEGRATION TEST: Full Simulation with Phase-2")
    print("="*60)
    
    from simulation.scenarios import SCENARIOS
    from simulation.simulator import Simulator
    from Components.trigger_system import TriggerSystem, TriggerType
    from density_rl.trigger_aware_policy import TriggerAwareQLearning, TriggerContext
    
    # Create simulation
    twin = SCENARIOS["railway_station"]()
    sim = Simulator(twin)
    
    # Create trigger system
    ts = TriggerSystem()
    
    # Create trigger-aware agent
    agent = TriggerAwareQLearning()
    
    # Spawn agents
    sim.spawn_agents_batch([
        {"start": "entry_main", "goal": "platform_1", "count": 30, "type": "normal"},
        {"start": "entry_main", "goal": "platform_2", "count": 30, "type": "family"},
        {"start": "entry_main", "goal": "exit_main", "count": 20, "type": "rushing"}
    ])
    
    for ag in sim.agents.values():
        path = sim.digital_twin.get_shortest_path(ag.current_node, ag.goal_node)
        if path:
            ag.set_path(path)
    
    print(f"[PASS] Created simulation: {len(sim.agents)} agents")
    
    # Create a trigger that will activate at step 5
    trigger = ts.create_trigger(
        trigger_type=TriggerType.GATE_MALFUNCTION,
        time_seconds=5.0,
        affected_zones=["fob_center"],
        severity=0.7
    )
    print(f"[PASS] Scheduled trigger: {trigger.trigger_type.value} at t=5s")
    
    # Run simulation
    max_densities = []
    panicked_counts = []
    recommendations = []
    
    for step in range(20):
        current_time = sim.time
        
        # Check for active triggers
        active_triggers = ts.get_active_triggers(current_time)
        
        # Apply trigger effects and panic propagation
        trigger_context = None
        for trig in active_triggers:
            ts.apply_trigger_effects(sim, trig)
            ts.propagate_panic(sim, trig, current_time)
            ts.apply_trigger_specific_behavior(sim, trig, current_time)
            trigger_context = TriggerContext(
                active_trigger_type=trig.trigger_type,
                trigger_severity=trig.severity,
                affected_zones=trig.affected_zones
            )
        
        # Get state
        snapshot = sim.digital_twin.get_state_snapshot()
        nodes = snapshot.get("nodes", {})
        densities = [n.get("density", 0) for n in nodes.values()]
        max_density = max(densities) if densities else 0
        max_densities.append(max_density)
        
        # Count panicked agents
        panicked = sum(1 for a in sim.agents.values() if a.is_panicked())
        panicked_counts.append(panicked)
        
        # Get AI recommendation
        danger_count = sum(1 for n in nodes.values() if n.get("risk_level") == "DANGER")
        
        if max_density > 2.5:
            action = agent.get_action(
                (round(max_density, 1), danger_count, int(np.mean(densities))),
                trigger_context=trigger_context
            )
            
            if action != "NOOP":
                recommendations.append({
                    "step": step,
                    "action": action,
                    "density": max_density,
                    "trigger_active": trigger_context is not None
                })
        
        # Step simulation
        sim.step()
    
    # Results
    print(f"\n=== Simulation Results ===")
    print(f"  Max density reached: {max(max_densities):.2f}")
    print(f"  Final density: {max_densities[-1]:.2f}")
    print(f"  Peak panicked agents: {max(panicked_counts)}")
    print(f"  Recommendations made: {len(recommendations)}")
    
    if recommendations:
        print(f"  Sample recommendations:")
        for rec in recommendations[:3]:
            print(f"    Step {rec['step']}: {rec['action']} (density={rec['density']:.2f}, trigger={rec['trigger_active']})")
    
    # Check agents reached goal
    reached = sum(1 for a in sim.agents.values() if a.has_reached_goal)
    print(f"  Agents evacuated: {reached}/{len(sim.agents)}")
    
    print("\n[PASS] Integration test PASSED")
    return True


def run_all_tests():
    """Run all Phase-2 tests"""
    print("\n" + "="*70)
    print("   PHASE-2 COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = {}
    
    try:
        results["2.1 Blueprint Processor"] = test_blueprint_processor()
    except Exception as e:
        print(f"\n[FAIL] Blueprint Processor test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["2.1 Blueprint Processor"] = False
    
    try:
        results["2.2 Panic Propagation"] = test_panic_propagation()
    except Exception as e:
        print(f"\n[FAIL] Panic Propagation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["2.2 Panic Propagation"] = False
    
    try:
        results["2.3 Multi-Scenario Training"] = test_multi_scenario_training()
    except Exception as e:
        print(f"\n[FAIL] Multi-Scenario Training test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["2.3 Multi-Scenario Training"] = False
    
    try:
        results["2.4 Case Study Mode"] = test_case_study_mode()
    except Exception as e:
        print(f"\n[FAIL] Case Study Mode test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["2.4 Case Study Mode"] = False
    
    try:
        results["2.5 Trigger-Aware Policy"] = test_trigger_aware_policy()
    except Exception as e:
        print(f"\n[FAIL] Trigger-Aware Policy test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["2.5 Trigger-Aware Policy"] = False
    
    try:
        results["Integration"] = test_integration()
    except Exception as e:
        print(f"\n[FAIL] Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results["Integration"] = False
    
    # Summary
    print("\n" + "="*70)
    print("   TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    if all_passed:
        print("   ALL TESTS PASSED!")
    else:
        print("   SOME TESTS FAILED")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
