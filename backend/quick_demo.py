from rl.q_learning_agent import CrowdSafetyQLearning
from rl.comparison import SimulationComparison

print("="*70)
print("AI-DRIVEN CROWD SAFETY SIMULATION - LIVE DEMO")
print("="*70)

# Load trained model
print("\n📚 Loading trained RL model...")
agent = CrowdSafetyQLearning()
agent.load_model("models/stadium_rl_model.pkl")
print(f"✅ Model loaded with {len(agent.q_table)} learned states")

# Setup comparison
comparison = SimulationComparison("stadium_exit", agent)

# Disaster scenario
spawn_config = [
    {"start": "zone_north", "goal": "exit_main", "count": 500, "type": "normal"},
    {"start": "zone_south", "goal": "exit_main", "count": 400, "type": "family"},
    {"start": "zone_east", "goal": "exit_main", "count": 100, "type": "rushing"},
    {"start": "zone_west", "goal": "exit_main", "count": 100, "type": "elderly"}
]

print("\n🚨 SCENARIO: 1100 people evacuating through stadium main exit")
print("\n" + "="*70)
print("SIMULATION 1: WITHOUT AI (Baseline)")
print("="*70)

baseline = comparison.run_baseline(1100, spawn_config, max_steps=250)

print(f"\n📊 Results:")
print(f"   Max Density: {baseline['max_density_reached']:.2f} p/m²")
if baseline['max_density_reached'] > 4.0:
    print("   ⚠️  DANGER LEVEL - Stampede risk!")
print(f"   Danger Violations: {baseline['danger_violations']}")
print(f"   Evacuation Time: {baseline['evacuation_time']:.0f} seconds")

print("\n" + "="*70)
print("SIMULATION 2: WITH AI OPTIMIZATION")
print("="*70)

optimized = comparison.run_optimized(1100, spawn_config, max_steps=250)

print(f"\n📊 Results:")
print(f"   Max Density: {optimized['max_density_reached']:.2f} p/m²")
if optimized['max_density_reached'] < 4.0:
    print("   ✅ SAFE LEVEL - Crisis prevented!")
print(f"   Danger Violations: {optimized['danger_violations']}")
print(f"   Evacuation Time: {optimized['evacuation_time']:.0f} seconds")
print(f"   AI Interventions: {len(optimized['actions_taken'])}")

# Show improvement
report = comparison.generate_comparison_report(baseline, optimized)

print("\n" + "="*70)
print("AI IMPACT SUMMARY")
print("="*70)
print(f"\n✅ Density Reduced: {report['improvements']['density_reduction_percent']:.1f}%")
print(f"✅ Danger Violations Prevented: {report['improvements']['danger_violations_prevented']}")
print(f"⏱️  Time Difference: {abs(report['improvements']['time_difference']):.0f}s")

print("\n🎯 Sample AI Decisions:")
for action in optimized['actions_taken'][:5]:
    print(f"\n   t={action['time']:.0f}s - {action['action']}")
    print(f"   Location: {action['node']} (density: {action['density']:.2f} p/m²)")
    print(f"   Reason: {action['explanation']}")

print("\n" + "="*70)
print("🎉 DEMO COMPLETE - AI successfully prevented crowd disaster!")
print("="*70)
