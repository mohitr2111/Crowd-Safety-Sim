from fastapi import APIRouter, HTTPException

try:
    from backend.models.schemas import SimulationRequest
    from backend.simulation.scenarios import SCENARIOS
    from backend.rl.comparison import SimulationComparison
    from backend.rl.q_learning_agent import CrowdSafetyQLearning
except ImportError:
    from models.schemas import SimulationRequest
    from simulation.scenarios import SCENARIOS
    from rl.comparison import SimulationComparison
    from rl.q_learning_agent import CrowdSafetyQLearning


router = APIRouter()


@router.post("/simulation/compare")
def compare_simulations(request: SimulationRequest):
    """Run both baseline and RL-optimized simulations for comparison"""
    # Load trained RL model
    agent = CrowdSafetyQLearning()
    try:
        agent.load_model("models/stadium_rl_model.pkl")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="RL model not found. Please train the model first by running: python train_model.py",
        )

    # Validate scenario
    if request.scenario not in SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario. Available: {list(SCENARIOS.keys())}",
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
        "optimized_history": optimized.get("history", []),
    }
