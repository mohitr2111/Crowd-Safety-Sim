"""Quick Phase-2 validation"""
import sys
sys.path.insert(0, '.')

print("="*60)
print("PHASE-2 QUICK VALIDATION")
print("="*60)

# Test 1: Blueprint Processor
print("\n[2.1] Blueprint Processor...")
from Components.blueprint_processor import get_blueprint_processor
proc = get_blueprint_processor()
result = proc.process_blueprint(b'x'*1000, 'stadium', 1.0)
print(f"  Elements: {len(result.elements)}")
print("  PASSED")

# Test 2: Agent Panic
print("\n[2.2] Panic Propagation...")
from simulation.agent import Agent
from Components.trigger_system import TriggerSystem, TriggerType
from simulation.scenarios import SCENARIOS
from simulation.simulator import Simulator

agent = Agent(1, 'zone_north', 'exit_main')
agent.update_panic(0.8, 'trig1', 0.0)
print(f"  Panic: {agent.panic_level}, panicked: {agent.is_panicked()}")

twin = SCENARIOS['stadium_exit']()
sim = Simulator(twin)
sim.spawn_agents_batch([{'start':'zone_north','goal':'exit_main','count':20,'type':'normal'}])
for a in sim.agents.values():
    p = sim.digital_twin.get_shortest_path(a.current_node, a.goal_node)
    if p: a.set_path(p)

ts = TriggerSystem()
trig = ts.create_trigger(TriggerType.EXTERNAL_EXPLOSION, 0.0, ['zone_north'], 0.9)
effects = ts.propagate_panic(sim, trig, 0.0)
print(f"  Propagated to {effects['affected_agents']} agents")
print("  PASSED")

# Test 3: Scenarios
print("\n[2.3] Multi-Scenario...")
from simulation.scenarios import SCENARIOS, SCENARIO_METADATA
for name in SCENARIOS:
    t = SCENARIOS[name]()
    print(f"  {name}: {len(t.node_data)} nodes")
print("  PASSED")

# Test 4: Case Study
print("\n[2.4] Case Study...")
from Components.case_study import get_case_study_manager
mgr = get_case_study_manager()
cfg = mgr.create_case_config(
    'stadium_exit', 'Test', 
    [{'type':'explosion','time':2,'zones':['zone_north'],'severity':0.5}],
    seed=99, num_agents=30, num_steps=10
)
pack = mgr.run_case_study(cfg, verbose=False)
print(f"  Baseline density: {pack.baseline_log.final_metrics['max_density']:.2f}")
print(f"  AI-aware density: {pack.ai_aware_log.final_metrics['max_density']:.2f}")
print("  PASSED")

# Test 5: Trigger Policy
print("\n[2.5] Trigger-Aware Policy...")
from density_rl.trigger_aware_policy import TriggerAwareQLearning, TriggerContext
ag = TriggerAwareQLearning()
ctx = TriggerContext(
    active_trigger_type=TriggerType.GATE_MALFUNCTION,
    trigger_severity=0.7,
    affected_zones=['exit_main']
)
action = ag.get_action((4.5, 2, 3), trigger_context=ctx)
print(f"  Action: {action}")
expl = ag.get_action_explanation((4.5, 2, 3), action, ctx)
print(f"  Reasons: {len(expl['reasoning'])}")
print("  PASSED")

# Integration
print("\n[INTEGRATION] Full simulation...")
twin = SCENARIOS['festival_corridor']()
sim = Simulator(twin)
sim.spawn_agents_batch([{'start':'entry_gate','goal':'exit_main','count':50,'type':'normal'}])
for a in sim.agents.values():
    p = sim.digital_twin.get_shortest_path(a.current_node, a.goal_node)
    if p: a.set_path(p)

ts = TriggerSystem()
ts.create_trigger(TriggerType.FALSE_ALARM, 3.0, ['stage_1_area'], 0.6)
agent = TriggerAwareQLearning()

for step in range(15):
    active = ts.get_active_triggers(sim.time)
    for t in active:
        ts.propagate_panic(sim, t, sim.time)
    sim.step()

panicked = sum(1 for a in sim.agents.values() if a.is_panicked())
reached = sum(1 for a in sim.agents.values() if a.has_reached_goal)
print(f"  After 15 steps: {panicked} panicked, {reached} evacuated")
print("  PASSED")

print("\n" + "="*60)
print("ALL PHASE-2 TESTS PASSED!")
print("="*60)
