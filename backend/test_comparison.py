from rl.q_learning_agent import CrowdSafetyQLearning
from rl.comparison import SimulationComparison

# Load trained model
agent = CrowdSafetyQLearning()
agent.load_model("models/stadium_rl_model.pkl")

# Create comparison
comparison = SimulationComparison("stadium_exit", agent)

# Test configuration - EVERYONE rushes to main exit (worst case)
spawn_config = [
    {"start": "zone_north", "goal": "exit_main", "count": 500, "type": "normal"},
    {"start": "zone_south", "goal": "exit_main", "count": 400, "type": "family"},
    {"start": "zone_east", "goal": "exit_main", "count": 100, "type": "rushing"},  # Changed to exit_main
    {"start": "zone_west", "goal": "exit_main", "count": 100, "type": "elderly"}   # Changed to exit_main
]

print("🚨 STRESS TEST: All 1100 agents heading to MAIN EXIT")
print("Running BASELINE simulation (no RL)...")
baseline = comparison.run_baseline(1100, spawn_config, max_steps=250)

print("\nRunning RL-OPTIMIZED simulation...")
optimized = comparison.run_optimized(1000, spawn_config, max_steps=200)  # Added max_steps

print("\n" + "="*60)
print("COMPARISON RESULTS")
print("="*60)

report = comparison.generate_comparison_report(baseline, optimized)

print(f"\n📊 BASELINE (No AI):")
print(f"  Max Density: {report['baseline']['max_density']:.2f} p/m²")
print(f"  Danger Violations: {report['baseline']['danger_violations']}")
print(f"  Evacuation Time: {report['baseline']['evacuation_time']:.1f}s")
print(f"  Agents Reached Goal: {report['baseline']['agents_reached']}")

print(f"\n🤖 RL-OPTIMIZED (With AI):")
print(f"  Max Density: {report['optimized']['max_density']:.2f} p/m²")
print(f"  Danger Violations: {report['optimized']['danger_violations']}")
print(f"  Evacuation Time: {report['optimized']['evacuation_time']:.1f}s")
print(f"  Agents Reached Goal: {report['optimized']['agents_reached']}")

print(f"\n✅ IMPROVEMENTS:")
print(f"  Density Reduction: {report['improvements']['density_reduction_percent']:.1f}%")
print(f"  Violations Prevented: {report['improvements']['danger_violations_prevented']}")

print(f"\n🎯 AI Actions Taken: {len(report['actions_taken'])}")
if len(report['actions_taken']) > 0:
    print("\nSample AI Decisions:")
    for action in report['actions_taken'][:10]:  # Show first 10
        print(f"  t={action['time']:.0f}s: {action['action']} at {action['node']}")
        print(f"      Density: {action['density']:.2f} p/m²")
        print(f"      Reason: {action['explanation']}")
else:
    print("  ⚠️ No actions taken - agents moved too fast or density stayed low")

# Save report
comparison.save_report(report, "comparison_report.json")
print(f"\nDetailed report saved to comparison_report.json")
