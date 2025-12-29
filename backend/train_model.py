from rl.q_learning_agent import CrowdSafetyQLearning
from rl.trainer import RLTrainer
import matplotlib.pyplot as plt

# Create agent with BETTER hyperparameters
agent = CrowdSafetyQLearning(
    learning_rate=0.2,       # Increased from 0.15 - learn faster
    discount_factor=0.95,    # Keep same
    epsilon=0.3              # Reduced from 0.4 - less random exploration
)

# Train on stadium scenario with MORE episodes
trainer = RLTrainer("stadium_exit", agent)

print("="*60)
print("ENHANCED TRAINING SESSION")
print("="*60)
print("Episodes: 500")
print("Agent range: 800-1200")
print("Estimated time: 10-15 minutes")
print("="*60)

history = trainer.train(
    num_episodes=500,        # Increased from 300
    agent_range=(800, 1200)  # More varied crowd sizes
)

# Save trained model
agent.save_model("models/stadium_rl_model.pkl")

print("\n" + "="*60)
print("TRAINING SUMMARY")
print("="*60)
print(f"Final Q-Table size: {len(agent.q_table)} states")
print(f"Total actions learned: {sum(len(actions) for actions in agent.q_table.values())}")

# Show learning curve
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.plot(history["total_rewards"], alpha=0.6)
# Add moving average
window = 20
if len(history["total_rewards"]) >= window:
    moving_avg = [sum(history["total_rewards"][i:i+window])/window 
                  for i in range(len(history["total_rewards"])-window)]
    plt.plot(range(window, len(history["total_rewards"])), moving_avg, 
             'r-', linewidth=2, label='20-episode average')
plt.title("Total Reward per Episode")
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 2)
plt.plot(history["max_densities"], alpha=0.6)
if len(history["max_densities"]) >= window:
    moving_avg = [sum(history["max_densities"][i:i+window])/window 
                  for i in range(len(history["max_densities"])-window)]
    plt.plot(range(window, len(history["max_densities"])), moving_avg, 
             'g-', linewidth=2, label='20-episode average')
plt.axhline(y=4.0, color='r', linestyle='--', label='Danger Threshold', linewidth=2)
plt.title("Max Density per Episode")
plt.xlabel("Episode")
plt.ylabel("Density (people/m²)")
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 3)
plt.plot(history["danger_violations"], alpha=0.6)
if len(history["danger_violations"]) >= window:
    moving_avg = [sum(history["danger_violations"][i:i+window])/window 
                  for i in range(len(history["danger_violations"])-window)]
    plt.plot(range(window, len(history["danger_violations"])), moving_avg, 
             'orange', linewidth=2, label='20-episode average')
plt.title("Danger Violations per Episode")
plt.xlabel("Episode")
plt.ylabel("Violations")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("training_progress.png", dpi=150)
print("\n✅ Training graphs saved to training_progress.png")

# Show best learned policies
print("\n" + "="*60)
print("LEARNED POLICIES (Best Q-values)")
print("="*60)
sorted_states = sorted(agent.q_table.items(), 
                      key=lambda x: max(x[1].values()), 
                      reverse=True)
for state, actions in sorted_states[:10]:  # Top 10 states
    best_action = max(actions.items(), key=lambda x: x[1])
    print(f"\nState: {state}")
    print(f"  Best Action: {best_action[0]}")
    print(f"  Q-value: {best_action[1]:.2f}")
    # Show all actions for this state
    for action, q_val in sorted(actions.items(), key=lambda x: x[1], reverse=True):
        if q_val != 0:
            print(f"    {action}: {q_val:.2f}")

print("\n" + "="*60)
print("🎉 TRAINING COMPLETE!")
print("="*60)
