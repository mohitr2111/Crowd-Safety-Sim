from enum import Enum
from typing import Dict, List, Callable
from dataclasses import dataclass
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

@dataclass
class Trigger:
    """Represents a stampede trigger event"""
    trigger_type: TriggerType
    time_seconds: float  # When trigger activates
    affected_zones: List[str]  # Which zones are affected
    severity: float  # 0.0-1.0 (1.0 = maximum panic)
    duration: float  # How long does it last
    description: str
    
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
    
    def __init__(self):
        self.active_triggers: List[Trigger] = []
        self.trigger_history: List[Trigger] = []
    
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