"""
Case Study Module (Sub-Phase 2.4)

Provides reproducible case packs for evaluation and reporting.
Enables side-by-side baseline vs AI-aware comparisons with downloadable reports.

Features:
- Reproducible scenario + trigger configurations
- Deterministic seeded runs
- Comprehensive logging of both runs
- Summary metrics for judges/authorities
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import random
import copy

from simulation.scenarios import SCENARIOS, SCENARIO_METADATA
from simulation.simulator import Simulator
from Components.trigger_system import TriggerSystem, TriggerType, Trigger


@dataclass
class CasePackConfig:
    """Configuration for a reproducible case study"""
    case_id: str
    case_name: str
    scenario_id: str
    random_seed: int
    num_agents: int
    num_steps: int
    triggers: List[Dict]  # [{type, time, zones, severity}, ...]
    spawn_config: Optional[List[Dict]] = None
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""


@dataclass
class SimulationLog:
    """Log of a simulation run for case study"""
    step_logs: List[Dict] = field(default_factory=list)
    final_metrics: Dict = field(default_factory=dict)
    recommendations: List[Dict] = field(default_factory=list)
    interventions: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "step_logs": self.step_logs,
            "final_metrics": self.final_metrics,
            "recommendations": self.recommendations,
            "interventions": self.interventions
        }


@dataclass
class CasePack:
    """Complete case study package"""
    config: CasePackConfig
    baseline_log: SimulationLog
    ai_aware_log: SimulationLog
    comparison_summary: Dict
    
    def to_dict(self) -> Dict:
        return {
            "case_id": self.config.case_id,
            "case_name": self.config.case_name,
            "scenario_id": self.config.scenario_id,
            "created_at": self.config.created_at.isoformat(),
            "description": self.config.description,
            "random_seed": self.config.random_seed,
            "num_agents": self.config.num_agents,
            "num_steps": self.config.num_steps,
            "triggers": self.config.triggers,
            "baseline_results": self.baseline_log.to_dict(),
            "ai_aware_results": self.ai_aware_log.to_dict(),
            "comparison_summary": self.comparison_summary
        }


class CaseStudyManager:
    """
    Manages reproducible case studies for evaluation.
    
    Ensures identical conditions between baseline and AI-aware runs
    for fair comparison.
    """
    
    def __init__(self):
        self._stored_cases: Dict[str, CasePack] = {}
        self._case_counter = 0
    
    def create_case_config(
        self,
        scenario_id: str,
        case_name: str,
        triggers: List[Dict],
        seed: int = 42,
        num_agents: Optional[int] = None,
        num_steps: int = 100,
        description: str = ""
    ) -> CasePackConfig:
        """
        Create a case study configuration.
        
        Args:
            scenario_id: ID of the scenario to use
            case_name: Human-readable name
            triggers: List of trigger configurations
            seed: Random seed for reproducibility
            num_agents: Number of agents (None = use scenario default)
            num_steps: Simulation steps to run
            description: Case description
            
        Returns:
            CasePackConfig ready for execution
        """
        self._case_counter += 1
        case_id = f"case_{self._case_counter:04d}_{int(datetime.now().timestamp())}"
        
        # Get default agent count from scenario metadata
        if num_agents is None:
            metadata = SCENARIO_METADATA.get(scenario_id, {})
            agent_range = metadata.get("agent_range", (500, 1000))
            num_agents = (agent_range[0] + agent_range[1]) // 2
        
        return CasePackConfig(
            case_id=case_id,
            case_name=case_name,
            scenario_id=scenario_id,
            random_seed=seed,
            num_agents=num_agents,
            num_steps=num_steps,
            triggers=triggers,
            description=description
        )
    
    def run_case_study(
        self,
        config: CasePackConfig,
        rl_agent = None,
        verbose: bool = True
    ) -> CasePack:
        """
        Run a complete case study with baseline and AI-aware comparison.
        
        Args:
            config: Case configuration
            rl_agent: Optional RL agent for AI-aware run
            verbose: Print progress
            
        Returns:
            CasePack with all logs and metrics
        """
        if config.scenario_id not in SCENARIOS:
            raise ValueError(f"Scenario '{config.scenario_id}' not found")
        
        if verbose:
            print(f"Running case study: {config.case_name}")
            print(f"  Scenario: {config.scenario_id}")
            print(f"  Agents: {config.num_agents}")
            print(f"  Steps: {config.num_steps}")
            print(f"  Triggers: {len(config.triggers)}")
        
        # Run baseline
        if verbose:
            print("\n1. Running baseline simulation...")
        baseline_log = self._run_simulation(
            config, 
            apply_ai_actions=False,
            rl_agent=None
        )
        
        # Run AI-aware
        if verbose:
            print("2. Running AI-aware simulation...")
        ai_log = self._run_simulation(
            config,
            apply_ai_actions=True,
            rl_agent=rl_agent
        )
        
        # Generate comparison
        comparison = self._generate_comparison(
            config, baseline_log, ai_log
        )
        
        case_pack = CasePack(
            config=config,
            baseline_log=baseline_log,
            ai_aware_log=ai_log,
            comparison_summary=comparison
        )
        
        # Store for later retrieval
        self._stored_cases[config.case_id] = case_pack
        
        if verbose:
            print("\n=== Case Study Complete ===")
            print(f"Baseline max density: {baseline_log.final_metrics.get('max_density', 'N/A'):.2f}")
            print(f"AI-aware max density: {ai_log.final_metrics.get('max_density', 'N/A'):.2f}")
            print(f"Improvement: {comparison.get('density_improvement_pct', 0):.1f}%")
        
        return case_pack
    
    def _run_simulation(
        self,
        config: CasePackConfig,
        apply_ai_actions: bool,
        rl_agent = None
    ) -> SimulationLog:
        """Run a single simulation with logging"""
        # Set seed for reproducibility
        random.seed(config.random_seed)
        
        # Create simulator
        twin = SCENARIOS[config.scenario_id]()
        sim = Simulator(twin)
        
        # Create trigger system
        trigger_system = TriggerSystem()
        
        # Add configured triggers
        for t_config in config.triggers:
            trigger_type = TriggerType(t_config.get("type", "false_alarm"))
            trigger_system.create_trigger(
                trigger_type=trigger_type,
                time_seconds=t_config.get("time", 10),
                affected_zones=t_config.get("zones", []),
                severity=t_config.get("severity", 0.7)
            )
        
        # Generate spawn config if not provided
        spawn_config = config.spawn_config or self._generate_spawn_config(
            sim, config.num_agents
        )
        sim.spawn_agents_batch(spawn_config)
        
        # Initialize paths
        for agent in sim.agents.values():
            path = sim.digital_twin.get_shortest_path(
                agent.current_node, agent.goal_node
            )
            if path:
                agent.set_path(path)
        
        # Run simulation
        log = SimulationLog()
        max_densities = []
        danger_violations = 0
        
        for step in range(config.num_steps):
            current_time = sim.time
            
            # Apply active triggers
            active_triggers = trigger_system.get_active_triggers(current_time)
            for trigger in active_triggers:
                trigger_system.apply_trigger_effects(sim, trigger)
                # Apply panic propagation (Phase 2.2)
                trigger_system.propagate_panic(sim, trigger, current_time)
            
            # Get state
            state = self._get_state(sim)
            max_densities.append(state["max_density"])
            
            if state["max_density"] > 4.0:
                danger_violations += 1
            
            # AI recommendations (logged regardless of execution)
            if rl_agent and state["max_density"] > 2.5:
                # Get recommendation
                node_data = sim.digital_twin.node_data
                hotspot = max(node_data.items(), 
                             key=lambda x: x[1].get("density", 0), 
                             default=(None, {}))[0]
                
                if hotspot:
                    action = rl_agent.get_action((
                        round(state["max_density"], 1),
                        state["danger_count"],
                        int(state["avg_density"])
                    ))
                    
                    recommendation = {
                        "step": step,
                        "time": current_time,
                        "node": hotspot,
                        "action": action,
                        "density": state["max_density"],
                        "executed": apply_ai_actions
                    }
                    log.recommendations.append(recommendation)
                    
                    # Execute if AI-aware mode
                    if apply_ai_actions and action and action != "NOOP":
                        self._apply_action(sim, hotspot, action, current_time)
                        log.interventions.append({
                            "step": step,
                            "action": action,
                            "node": hotspot
                        })
            
            # Log step
            step_log = {
                "step": step,
                "time": current_time,
                "max_density": state["max_density"],
                "danger_count": state["danger_count"],
                "agents_exited": state["agents_exited"],
                "active_triggers": len(active_triggers)
            }
            log.step_logs.append(step_log)
            
            # Advance simulation
            sim.step()
        
        # Final metrics
        agents_reached = sum(1 for a in sim.agents.values() if a.has_reached_goal)
        
        log.final_metrics = {
            "max_density": max(max_densities) if max_densities else 0,
            "mean_density": sum(max_densities) / len(max_densities) if max_densities else 0,
            "danger_violations": danger_violations,
            "agents_evacuated": agents_reached,
            "evacuation_rate": agents_reached / len(sim.agents) if sim.agents else 0,
            "recommendations_generated": len(log.recommendations),
            "interventions_executed": len(log.interventions)
        }
        
        return log
    
    def _get_state(self, sim: Simulator) -> Dict:
        """Extract state from simulator"""
        snapshot = sim.digital_twin.get_state_snapshot()
        nodes = snapshot.get("nodes", {})
        
        densities = [n.get("density", 0) for n in nodes.values()]
        
        return {
            "max_density": max(densities) if densities else 0,
            "avg_density": sum(densities) / len(densities) if densities else 0,
            "danger_count": sum(1 for n in nodes.values() 
                               if n.get("risk_level") == "DANGER"),
            "agents_exited": sum(1 for a in sim.agents.values() 
                                if a.has_reached_goal)
        }
    
    def _generate_spawn_config(self, sim: Simulator, num_agents: int) -> List[Dict]:
        """Generate spawn configuration"""
        node_data = sim.digital_twin.node_data
        
        entries = [n for n, d in node_data.items() if d.get("type") == "entry"]
        exits = [n for n, d in node_data.items() if d.get("type") == "exit"]
        
        if not entries:
            entries = [n for n, d in node_data.items() 
                      if d.get("type") in ("general", "waiting")][:3]
        if not exits:
            exits = list(node_data.keys())[-2:]
        
        spawn_config = []
        per_entry = num_agents // len(entries) if entries else num_agents
        
        for entry in entries:
            spawn_config.append({
                "start": entry,
                "goal": random.choice(exits) if exits else entry,
                "count": per_entry,
                "type": "normal"
            })
        
        return spawn_config
    
    def _apply_action(self, sim: Simulator, node_id: str, action: str, current_time: float):
        """Apply intervention action"""
        target_agents = [
            ag for ag in sim.agents.values()
            if not ag.has_reached_goal and 
               (ag.current_node == node_id or ag.get_next_node() == node_id)
        ]
        
        if action == "THROTTLE_25":
            for ag in target_agents[:len(target_agents)//4]:
                ag.block_until(current_time + 1.5)
        elif action == "THROTTLE_50":
            for ag in target_agents[:len(target_agents)//2]:
                ag.block_until(current_time + 2.5)
        elif action == "CLOSE_INFLOW":
            for ag in target_agents:
                ag.block_until(current_time + 5.0)
        elif action == "REROUTE":
            exits = [n for n, d in sim.digital_twin.node_data.items() 
                    if d.get("type") == "exit"]
            for ag in target_agents[:len(target_agents)//3]:
                if exits:
                    alt = random.choice(exits)
                    path = sim.digital_twin.get_shortest_path(ag.current_node, alt)
                    if path:
                        ag.set_path(path)
                        ag.goal_node = alt
    
    def _generate_comparison(
        self,
        config: CasePackConfig,
        baseline: SimulationLog,
        ai_aware: SimulationLog
    ) -> Dict:
        """Generate comparison summary between runs"""
        base_metrics = baseline.final_metrics
        ai_metrics = ai_aware.final_metrics
        
        # Calculate improvements
        density_improvement = 0
        if base_metrics.get("max_density", 0) > 0:
            density_improvement = (
                (base_metrics["max_density"] - ai_metrics.get("max_density", 0)) /
                base_metrics["max_density"] * 100
            )
        
        violation_improvement = 0
        if base_metrics.get("danger_violations", 0) > 0:
            violation_improvement = (
                (base_metrics["danger_violations"] - ai_metrics.get("danger_violations", 0)) /
                base_metrics["danger_violations"] * 100
            )
        
        return {
            "case_id": config.case_id,
            "case_name": config.case_name,
            "baseline": {
                "max_density": base_metrics.get("max_density", 0),
                "danger_violations": base_metrics.get("danger_violations", 0),
                "evacuation_rate": base_metrics.get("evacuation_rate", 0)
            },
            "ai_aware": {
                "max_density": ai_metrics.get("max_density", 0),
                "danger_violations": ai_metrics.get("danger_violations", 0),
                "evacuation_rate": ai_metrics.get("evacuation_rate", 0),
                "recommendations": ai_metrics.get("recommendations_generated", 0),
                "interventions": ai_metrics.get("interventions_executed", 0)
            },
            "density_improvement_pct": round(density_improvement, 2),
            "violation_improvement_pct": round(violation_improvement, 2),
            "recommendation_execution_rate": (
                ai_metrics.get("interventions_executed", 0) / 
                max(1, ai_metrics.get("recommendations_generated", 1)) * 100
            ),
            "trigger_count": len(config.triggers),
            "reproducible": True,
            "seed": config.random_seed
        }
    
    def get_case_pack(self, case_id: str) -> Optional[CasePack]:
        """Retrieve a stored case pack"""
        return self._stored_cases.get(case_id)
    
    def list_cases(self) -> List[Dict]:
        """List all stored case packs"""
        return [
            {
                "case_id": case.config.case_id,
                "case_name": case.config.case_name,
                "scenario_id": case.config.scenario_id,
                "created_at": case.config.created_at.isoformat()
            }
            for case in self._stored_cases.values()
        ]
    
    def export_report(self, case_id: str, format: str = "json") -> str:
        """
        Export case study report.
        
        Args:
            case_id: ID of case to export
            format: "json" or "markdown"
            
        Returns:
            Report as string
        """
        case = self._stored_cases.get(case_id)
        if not case:
            raise ValueError(f"Case '{case_id}' not found")
        
        if format == "json":
            return json.dumps(case.to_dict(), indent=2, default=str)
        
        elif format == "markdown":
            return self._generate_markdown_report(case)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_markdown_report(self, case: CasePack) -> str:
        """Generate markdown report for case study"""
        comp = case.comparison_summary
        base = comp["baseline"]
        ai = comp["ai_aware"]
        
        lines = [
            f"# Case Study Report: {case.config.case_name}",
            "",
            f"**Case ID:** {case.config.case_id}",
            f"**Generated:** {case.config.created_at.isoformat()}",
            f"**Scenario:** {case.config.scenario_id}",
            "",
            "## Configuration",
            "",
            f"- **Agents:** {case.config.num_agents}",
            f"- **Steps:** {case.config.num_steps}",
            f"- **Random Seed:** {case.config.random_seed}",
            f"- **Triggers:** {len(case.config.triggers)}",
            "",
            "## Results Comparison",
            "",
            "| Metric | Baseline | AI-Aware | Improvement |",
            "|--------|----------|----------|-------------|",
            f"| Max Density | {base['max_density']:.2f} | {ai['max_density']:.2f} | {comp['density_improvement_pct']:.1f}% |",
            f"| Danger Violations | {base['danger_violations']} | {ai['danger_violations']} | {comp['violation_improvement_pct']:.1f}% |",
            f"| Evacuation Rate | {base['evacuation_rate']*100:.1f}% | {ai['evacuation_rate']*100:.1f}% | - |",
            "",
            "## AI Activity",
            "",
            f"- **Recommendations Generated:** {ai['recommendations']}",
            f"- **Interventions Executed:** {ai['interventions']}",
            f"- **Execution Rate:** {comp['recommendation_execution_rate']:.1f}%",
            "",
            "## Conclusion",
            "",
            f"The AI-aware simulation {'improved' if comp['density_improvement_pct'] > 0 else 'did not improve'} "
            f"upon the baseline, with a {abs(comp['density_improvement_pct']):.1f}% "
            f"{'reduction' if comp['density_improvement_pct'] > 0 else 'increase'} in max density.",
            "",
            "---",
            "*This report was automatically generated by the Crowd Safety Platform.*"
        ]
        
        return "\n".join(lines)


# Singleton instance
_manager_instance: Optional[CaseStudyManager] = None

def get_case_study_manager() -> CaseStudyManager:
    """Get singleton CaseStudyManager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = CaseStudyManager()
    return _manager_instance
