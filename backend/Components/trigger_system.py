from enum import Enum
from typing import Dict, List, Callable, Optional, Set
from dataclasses import dataclass, field
import random
import numpy as np



class TriggerType(Enum):
    """Real-world stampede triggers based on historical analysis"""
    FALSE_ALARM = "false_alarm"  # Hoax/false information spreading
    GATE_MALFUNCTION = "gate_malfunction"  # Exit gate closes/jams
    EXTERNAL_EXPLOSION = "explosion"  # Noise/rumor of explosion
    WEATHER_CHANGE = "weather"  # Sudden weather (rain, heat)
    INFRASTRUCTURE_FAILURE = "infra_failure"  # Bridge sway, structure instability
    PANIC_CHAIN_REACTION = "panic_cascade"  # One person falls → cascading panic


# ============================================================
# PHASE 2.2: Panic Propagation Configuration
# ============================================================

@dataclass
class PanicPropagationConfig:
    """Configuration for spatial panic propagation"""
    spread_rate: float = 0.3       # How much panic decays per hop (0-1)
    decay_rate: float = 0.05       # Panic decay per second when safe
    max_propagation_depth: int = 3  # Max hops panic can spread
    min_panic_to_spread: float = 0.1  # Minimum panic level to propagate


# Trigger-specific behavior configurations
TRIGGER_BEHAVIORS = {
    TriggerType.EXTERNAL_EXPLOSION: {
        "panic_multiplier": 1.5,
        "agent_behavior": "flee_to_exits",
        "avoid_trigger_zone": True,  # Agents avoid the trigger zone
        "flow_impact": 0.2,  # 80% reduction in affected corridors
        "base_panic": 0.9,   # High initial panic
    },
    TriggerType.GATE_MALFUNCTION: {
        "panic_multiplier": 1.1,
        "agent_behavior": "localized_wait",
        "avoid_trigger_zone": False,  # Congestion, not avoidance
        "flow_impact": 0.3,  # 70% reduction at specific gate
        "base_panic": 0.5,
    },
    TriggerType.FALSE_ALARM: {
        "panic_multiplier": 1.3,
        "agent_behavior": "exit_surge",
        "avoid_trigger_zone": False,
        "flow_impact": 1.0,  # No physical impact, pure panic
        "base_panic": 0.7,
    },
    TriggerType.WEATHER_CHANGE: {
        "panic_multiplier": 1.2,
        "agent_behavior": "seek_shelter",
        "avoid_trigger_zone": False,
        "flow_impact": 0.8,
        "base_panic": 0.4,
    },
    TriggerType.INFRASTRUCTURE_FAILURE: {
        "panic_multiplier": 1.4,
        "agent_behavior": "flee_to_exits",
        "avoid_trigger_zone": True,
        "flow_impact": 0.1,  # Major restriction
        "base_panic": 0.85,
    },
    TriggerType.PANIC_CHAIN_REACTION: {
        "panic_multiplier": 1.6,
        "agent_behavior": "cascade",
        "avoid_trigger_zone": False,  # Panic spreads from person
        "flow_impact": 1.0,
        "base_panic": 0.6,
    }
}


@dataclass
class Trigger:
    """Represents a stampede trigger event"""
    trigger_type: TriggerType
    time_seconds: float  # When trigger activates
    affected_zones: List[str]  # Which zones are affected
    severity: float  # 0.0-1.0 (1.0 = maximum panic)
    duration: float  # How long does it last
    description: str
    trigger_id: str = field(default_factory=lambda: f"trigger_{random.randint(1000, 9999)}")
    
    def __repr__(self):
        return f"Trigger({self.trigger_type.value} at {self.time_seconds}s, severity={self.severity:.1%})"

class TriggerSystem:
    """
    Generates realistic stampede triggers.
    
    Real cases analyzed:
    - Mahakumbh 2024: Gate malfunction → 121 dead
    - Itaewon 2022: False rumor → 156 dead (HIGH DENSITY + TRIGGER)
    - Vijay Thalapathy Rally 2024: Gate closure → 26 dead
    - RCB Stadium 2011: Infrastructure sway → crowd panic
    
    Phase 2.2: Now includes spatial panic propagation.
    """
    
    # Trigger profiles based on historical stampedes
    TRIGGER_PROFILES = {
        TriggerType.FALSE_ALARM: {
            "name": "False Alarm / Hoax",
            "severity_range": (0.4, 0.8),  # Moderate to high panic
            "affected_zone_count": (2, 5),  # Spreads to multiple zones
            "panic_multiplier": 2.0,  # People move 2x faster (chaotic)
            "historical_example": "Itaewon 2022: Rumor of crowd surge",
            "real_cases": [
                {"year": 2022, "location": "Itaewon, Seoul", "deaths": 156, "cause": "False information + high density"},
                {"year": 2024, "location": "Vijay Thalapathy Rally", "deaths": 26, "cause": "Gate closure rumor"},
            ]
        },
        
        TriggerType.GATE_MALFUNCTION: {
            "name": "Exit Gate Malfunction",
            "severity_range": (0.6, 1.0),  # High severity (physical blockage)
            "affected_zone_count": (1, 3),  # Affects zones near gate
            "panic_multiplier": 1.8,
            "flow_reduction": 0.3,  # Gate handles only 30% flow
            "historical_example": "Mahakumbh 2024: Gate jam",
            "real_cases": [
                {"year": 2024, "location": "Mahakumbh, Prayagraj", "deaths": 121, "cause": "Gate jam + high density (80M pilgrims)"},
                {"year": 2013, "location": "Mahakumbh, Allahabad", "deaths": 36, "cause": "Crowd surge at gate"},
            ]
        },
        
        TriggerType.EXTERNAL_EXPLOSION: {
            "name": "Explosion / Loud Noise",
            "severity_range": (0.7, 1.0),  # Very high panic (fight-or-flight)
            "affected_zone_count": (3, 8),  # Spreads across venue
            "panic_multiplier": 3.0,  # EXTREME panic (3x faster movement)
            "duration_range": (30, 120),  # Panic lasts longer
            "historical_example": "Boston Marathon 2013 (if had crowd): Sudden noise",
        },
        
        TriggerType.WEATHER_CHANGE: {
            "name": "Sudden Weather Change",
            "severity_range": (0.3, 0.6),  # Moderate panic
            "affected_zone_count": (1, 4),
            "panic_multiplier": 1.5,
            "reduced_visibility": True,
            "historical_example": "Heavy rain causes crowd to rush inside",
        },
        
        TriggerType.INFRASTRUCTURE_FAILURE: {
            "name": "Infrastructure Instability",
            "severity_range": (0.8, 1.0),  # Very high (physical threat)
            "affected_zone_count": (2, 6),
            "panic_multiplier": 2.5,
            "historical_example": "Bridge sway triggers crowd surge",
        },
        
        TriggerType.PANIC_CHAIN_REACTION: {
            "name": "One Person Falls → Cascading Panic",
            "severity_range": (0.5, 0.9),
            "affected_zone_count": (1, 2),  # Starts small, spreads
            "panic_multiplier": 2.2,
            "cascade_effect": 1.3,  # Panic amplifies
            "historical_example": "Love Parade 2010: One person falls → 21 dead",
        }
    }
    
    def __init__(self, propagation_config: Optional[PanicPropagationConfig] = None):
        self.active_triggers: List[Trigger] = []
        self.trigger_history: List[Trigger] = []
        self.propagation_config = propagation_config or PanicPropagationConfig()
        # Track panic levels per node for propagation
        self._node_panic_levels: Dict[str, float] = {}
    
    def create_trigger(self, trigger_type: TriggerType, 
                      time_seconds: float,
                      affected_zones: List[str],
                      severity: float = None,
                      custom_description: str = None) -> Trigger:
        """
        Create a trigger event.
        
        Args:
            trigger_type: Type of trigger
            time_seconds: When it activates
            affected_zones: Which zones are affected
            severity: 0-1 (if None, random in range)
            custom_description: Custom description
        """
        profile = self.TRIGGER_PROFILES[trigger_type]
        
        if severity is None:
            severity = random.uniform(*profile["severity_range"])
        
        duration = random.uniform(
            profile.get("duration_range", (15, 60))[0],
            profile.get("duration_range", (15, 60))[1]
        )
        
        description = custom_description or (
            f"{profile['name']} - Severity: {severity:.0%}\n"
            f"Example: {profile['historical_example']}"
        )
        
        trigger = Trigger(
            trigger_type=trigger_type,
            time_seconds=time_seconds,
            affected_zones=affected_zones,
            severity=severity,
            duration=duration,
            description=description
        )
        
        self.active_triggers.append(trigger)
        self.trigger_history.append(trigger)
        
        return trigger
    
    def get_active_triggers(self, current_time: float) -> List[Trigger]:
        """Get triggers active at current time"""
        return [t for t in self.active_triggers 
                if t.time_seconds <= current_time < t.time_seconds + t.duration]
    
    def apply_trigger_effects(self, simulator, trigger: Trigger) -> Dict:
        """
        Apply trigger effects to simulation.
        
        Returns: Effects applied
        """
        profile = self.TRIGGER_PROFILES[trigger.trigger_type]
        effects = {
            'trigger': trigger.trigger_type.value,
            'zones_affected': trigger.affected_zones,
            'severity': trigger.severity,
            'actions_taken': []
        }
        
        # Increase panic in affected zones
        for zone_id in trigger.affected_zones:
            if zone_id in simulator.digital_twin.node_data:
                # Increase agent movement speed (panic)
                panic_multiplier = profile.get('panic_multiplier', 1.5)
                
                for agent in simulator.agents.values():
                    if agent.current_node == zone_id:
                        agent.speed *= panic_multiplier
                        agent.panic_threshold *= 0.7  # Lower threshold (easier to panic)
                
                effects['actions_taken'].append(
                    f"Increased panic in {zone_id}: movement +{(panic_multiplier-1)*100:.0f}%"
                )
        
        # Reduce flow capacity (gates jam, etc.)
        if trigger.trigger_type == TriggerType.GATE_MALFUNCTION:
            profile = self.TRIGGER_PROFILES[TriggerType.GATE_MALFUNCTION]
            reduction = profile.get('flow_reduction', 0.5)
            
            for zone_id in trigger.affected_zones:
                # Reduce exit flow
                for u, v in simulator.digital_twin.edge_data.keys():
                    if v in trigger.affected_zones:  # Edge TO blocked zone
                        original_cap = simulator.digital_twin.edge_data[(u, v)]['flow_capacity']
                        simulator.digital_twin.edge_data[(u, v)]['flow_capacity'] = int(original_cap * reduction)
                        effects['actions_taken'].append(
                            f"Blocked exit from {u} to {v}: flow {original_cap} → {int(original_cap * reduction)}"
                        )
        
        return effects
    
    def get_stampede_prediction(self, simulator, trigger: Trigger = None) -> Dict:
        """
        Predict stampede probability based on:
        - Current max density
        - Active triggers
        - Exit capacity vs crowd
        """
        densities = simulator.digital_twin.get_state_snapshot()['nodes']
        max_density = max([d['density'] for d in densities.values()]) if densities else 0
        
        # Base probability from density
        if max_density > 6.0:
            base_prob = 0.95
        elif max_density > 4.0:
            base_prob = 0.70
        elif max_density > 3.0:
            base_prob = 0.40
        else:
            base_prob = 0.10
        
        # Increase if trigger active
        if trigger:
            base_prob *= (1 + trigger.severity)
            base_prob = min(base_prob, 1.0)
        
        # Minutes until stampede (based on current trajectory)
        if max_density > 2.0:
            minutes_until = max(1, 15 - (max_density * 2))
        else:
            minutes_until = 60
        
        return {
            'stampede_probability': round(base_prob * 100, 1),
            'max_density': round(max_density, 2),
            'minutes_until_critical': round(minutes_until, 1),
            'critical_density_threshold': 4.0,
            'recommendation': self._get_recommendation(base_prob, trigger)
        }
    
    def _get_recommendation(self, probability: float, trigger: Trigger = None) -> str:
        """Get AI recommendation based on stampede probability"""
        if trigger:
            recommendations = {
                TriggerType.FALSE_ALARM: "URGENT: Amplify official announcements. Use loudspeakers. Direct crowd to all exits.",
                TriggerType.GATE_MALFUNCTION: "CRITICAL: IMMEDIATELY open backup exits. Deploy traffic control to secondary routes.",
                TriggerType.EXTERNAL_EXPLOSION: "EMERGENCY: Establish calm evacuation. Use PA system. Deploy security to prevent panic.",
                TriggerType.WEATHER_CHANGE: "MODERATE: Redirect crowd to covered areas. Monitor density at shelter zones.",
                TriggerType.INFRASTRUCTURE_FAILURE: "CRITICAL: Immediate structural evacuation. Close affected areas. Reroute all traffic.",
                TriggerType.PANIC_CHAIN_REACTION: "URGENT: Deploy medical to incident. Prevent cascade. Calm surrounding crowd.",
            }
            return recommendations.get(trigger.trigger_type, "Take immediate action")
        
        if probability > 0.7:
            return "🚨 CRITICAL: Immediate evacuation required"
        elif probability > 0.5:
            return "⚠️  WARNING: Close entries, open all exits"
        elif probability > 0.3:
            return "🟡 CAUTION: Monitor density, prepare contingency"
        else:
            return "✅ SAFE: Normal operations"
    
    def get_historical_case_study(self, trigger_type: TriggerType) -> Dict:
        """Get historical stampede case study for trigger type"""
        profile = self.TRIGGER_PROFILES[trigger_type]
        cases = profile.get('real_cases', [])
        
        if not cases:
            return {
                'trigger': trigger_type.value,
                'cases': [],
                'message': 'No historical data'
            }
        
        return {
            'trigger': trigger_type.value,
            'cases': cases,
            'lessons_learned': self._get_lessons(trigger_type)
        }
    
    def _get_lessons(self, trigger_type: TriggerType) -> List[str]:
        """Extract lessons from historical stampedes"""
        lessons = {
            TriggerType.FALSE_ALARM: [
                "Official communication is critical",
                "Misinformation spreads faster than facts",
                "Need PA system in every zone",
                "Social media monitoring needed"
            ],
            TriggerType.GATE_MALFUNCTION: [
                "Backup exit protocols essential",
                "Regular maintenance prevents jams",
                "Multiple route options required",
                "Capacity calculations must be conservative"
            ],
            TriggerType.EXTERNAL_EXPLOSION: [
                "Panic control more important than actual danger",
                "Pre-trained evacuation procedures needed",
                "Security presence calms crowds",
                "Clear, calm communication is life-saving"
            ],
            TriggerType.WEATHER_CHANGE: [
                "Weather-aware crowd planning",
                "Covered areas must be capacious",
                "Temperature monitoring in crowds",
                "Weather-based density limits"
            ],
            TriggerType.INFRASTRUCTURE_FAILURE: [
                "Structural inspection before events",
                "Weight distribution management",
                "Real-time monitoring of infrastructure",
                "Quick closure procedures"
            ],
            TriggerType.PANIC_CHAIN_REACTION: [
                "First aid stations in high-density zones",
                "Quick removal of fallen persons",
                "Barrier systems to prevent crush",
                "Staff training on crowd psychology"
            ]
        }
        
        return lessons.get(trigger_type, [])
    
    # ============================================================
    # PHASE 2.2: Spatial Panic Propagation
    # ============================================================
    
    def propagate_panic(self, simulator, trigger: Trigger, current_time: float) -> Dict:
        """
        Propagate panic spatially across connected nodes.
        
        Uses BFS to spread panic from affected zones to neighboring zones,
        with decay based on distance from trigger source.
        
        Args:
            simulator: The simulation instance
            trigger: The active trigger
            current_time: Current simulation time
            
        Returns:
            Dict with propagation effects and statistics
        """
        effects = {
            "trigger_id": trigger.trigger_id,
            "trigger_type": trigger.trigger_type.value,
            "affected_agents": 0,
            "nodes_reached": [],
            "panic_by_node": {}
        }
        
        # Get trigger-specific behavior
        behavior = TRIGGER_BEHAVIORS.get(trigger.trigger_type, {})
        base_panic = behavior.get("base_panic", 0.5) * trigger.severity
        
        # Get graph adjacency from digital twin
        graph = simulator.digital_twin.graph
        
        # BFS propagation from affected zones
        visited: Set[str] = set()
        queue = []  # (node_id, depth, panic_level)
        
        # Initialize with affected zones
        for zone_id in trigger.affected_zones:
            if zone_id in simulator.digital_twin.node_data:
                queue.append((zone_id, 0, base_panic))
                self._node_panic_levels[zone_id] = base_panic
        
        while queue:
            node_id, depth, panic_level = queue.pop(0)
            
            if node_id in visited:
                continue
            if depth > self.propagation_config.max_propagation_depth:
                continue
            if panic_level < self.propagation_config.min_panic_to_spread:
                continue
            
            visited.add(node_id)
            effects["nodes_reached"].append(node_id)
            effects["panic_by_node"][node_id] = panic_level
            
            # Update panic level for this node
            self._node_panic_levels[node_id] = max(
                self._node_panic_levels.get(node_id, 0), 
                panic_level
            )
            
            # Apply panic to agents in this node
            for agent in simulator.agents.values():
                if agent.current_node == node_id and not agent.has_reached_goal:
                    agent.update_panic(panic_level, trigger.trigger_id, current_time)
                    effects["affected_agents"] += 1
            
            # Propagate to neighbors with decay
            if node_id in graph:
                for neighbor in graph.neighbors(node_id):
                    if neighbor not in visited:
                        # Panic decays with distance
                        new_panic = panic_level * (1 - self.propagation_config.spread_rate)
                        queue.append((neighbor, depth + 1, new_panic))
        
        return effects
    
    def apply_trigger_specific_behavior(self, simulator, trigger: Trigger, current_time: float) -> Dict:
        """
        Apply trigger-specific agent behavior modifications.
        
        Different triggers cause different movement patterns:
        - EXPLOSION: Agents flee away from trigger zone
        - GATE_MALFUNCTION: Agents wait/reroute
        - FALSE_ALARM: Agents surge toward exits
        
        Args:
            simulator: The simulation instance  
            trigger: The active trigger
            current_time: Current simulation time
            
        Returns:
            Dict with behavior modifications applied
        """
        behavior = TRIGGER_BEHAVIORS.get(trigger.trigger_type, {})
        effects = {
            "trigger_id": trigger.trigger_id,
            "behavior_type": behavior.get("agent_behavior", "none"),
            "agents_modified": 0,
            "reroutes": 0
        }
        
        agent_behavior = behavior.get("agent_behavior", "none")
        avoid_trigger = behavior.get("avoid_trigger_zone", False)
        
        for agent in simulator.agents.values():
            if agent.has_reached_goal:
                continue
            
            # Check if agent is affected (in or near trigger zones)
            is_in_affected_zone = agent.current_node in trigger.affected_zones
            is_panicked = agent.is_panicked()
            
            if is_in_affected_zone or is_panicked:
                effects["agents_modified"] += 1
                
                # Apply behavior-specific modifications
                if agent_behavior == "flee_to_exits" and avoid_trigger:
                    # Reroute away from trigger zone if possible
                    self._reroute_away_from_trigger(
                        simulator, agent, trigger.affected_zones
                    )
                    effects["reroutes"] += 1
                    
                elif agent_behavior == "exit_surge":
                    # Increase urgency toward exits
                    agent.patience = max(0.1, agent.patience * 0.5)
                    
                elif agent_behavior == "localized_wait":
                    # Agents near malfunction wait
                    if is_in_affected_zone:
                        agent.block_until(current_time + 5.0)
                        
                elif agent_behavior == "seek_shelter":
                    # Would reroute to covered areas (not implemented yet)
                    pass
        
        return effects
    
    def _reroute_away_from_trigger(self, simulator, agent, avoid_zones: List[str]):
        """
        Attempt to reroute agent away from trigger zones.
        
        Tries to find alternative path that doesn't go through avoided zones.
        """
        if not agent.path or agent.path_index >= len(agent.path) - 1:
            return
        
        # Check if current path goes through avoid zones
        remaining_path = agent.path[agent.path_index:]
        path_intersects = any(node in avoid_zones for node in remaining_path)
        
        if not path_intersects:
            return  # Current path is fine
        
        # Try to find alternative exit that doesn't require going through danger
        current = agent.current_node
        exits = [
            node_id for node_id, data in simulator.digital_twin.node_data.items()
            if data.get("type") == "exit"
        ]
        
        # Find path to each exit, prefer ones not through danger zones
        best_path = None
        best_score = float('inf')
        
        for exit_node in exits:
            try:
                path = simulator.digital_twin.get_shortest_path(current, exit_node)
                if path:
                    # Score = path length + penalty for going through danger
                    danger_count = sum(1 for n in path if n in avoid_zones)
                    score = len(path) + (danger_count * 10)  # Heavy penalty
                    
                    if score < best_score:
                        best_score = score
                        best_path = path
            except:
                continue
        
        if best_path:
            agent.path = best_path
            agent.path_index = 0
            agent.goal_node = best_path[-1]
    
    def decay_node_panic(self, simulator, current_time: float, dt: float):
        """
        Decay panic levels at nodes over time when no active triggers.
        
        Args:
            simulator: The simulation instance
            current_time: Current simulation time
            dt: Time step
        """
        active_trigger_zones = set()
        for trigger in self.get_active_triggers(current_time):
            active_trigger_zones.update(trigger.affected_zones)
        
        # Decay panic at nodes not currently under active trigger
        for node_id in list(self._node_panic_levels.keys()):
            if node_id not in active_trigger_zones:
                self._node_panic_levels[node_id] -= self.propagation_config.decay_rate * dt
                if self._node_panic_levels[node_id] <= 0:
                    del self._node_panic_levels[node_id]
    
    def get_panic_state(self) -> Dict:
        """Get current panic state for visualization/logging"""
        return {
            "node_panic_levels": self._node_panic_levels.copy(),
            "active_trigger_count": len(self.active_triggers),
            "max_panic": max(self._node_panic_levels.values()) if self._node_panic_levels else 0.0
        }