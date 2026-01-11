"""
PHASE 4: Advanced Monitoring Module
Predictive stampede probability, intervention effectiveness tracking, system health monitoring
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math


class HealthStatus(Enum):
    """System health status"""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    FAILED = "FAILED"


@dataclass
class InterventionEffectiveness:
    """Track effectiveness of an intervention"""
    intervention_id: str
    action_type: str
    node_id: str
    applied_at: float
    pre_density: float  # Density before intervention
    post_density: float  # Density after intervention
    density_reduction: float  # Reduction achieved
    effectiveness_score: float  # 0-1 score
    target_met: bool  # Whether target was achieved
    measured_at: float  # When effectiveness was measured


@dataclass
class SystemHealthMetrics:
    """System health metrics"""
    overall_status: HealthStatus
    intervention_frequency: float  # Interventions per minute
    average_effectiveness: float  # Average intervention effectiveness
    danger_zone_count: int
    max_density: float
    active_interventions: int
    system_stability: float  # 0-1 score
    last_updated: float


@dataclass
class StampedePrediction:
    """Predictive stampede probability"""
    probability: float  # 0-1 probability
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    predicted_time: Optional[float] = None  # When stampede might occur
    contributing_factors: List[str] = field(default_factory=list)
    confidence: float = 0.0  # Prediction confidence (0-1)
    last_updated: float = 0.0


class AdvancedMonitoring:
    """
    PHASE 4: Advanced Monitoring
    
    Tracks:
    - Predictive stampede probability
    - Intervention effectiveness
    - System health
    - Real-time metrics
    """
    
    def __init__(self):
        """Initialize advanced monitoring"""
        self.intervention_history: List[InterventionEffectiveness] = []
        self.stampede_predictions: List[StampedePrediction] = []
        self.health_metrics: Optional[SystemHealthMetrics] = None
        self.density_history: List[Tuple[float, Dict[str, float]]] = []  # (time, {node_id: density})
        self.max_history_size = 1000  # Keep last 1000 density snapshots
    
    def record_intervention(
        self,
        intervention_id: str,
        action_type: str,
        node_id: str,
        applied_at: float,
        pre_density: float,
        post_density: Optional[float] = None
    ):
        """Record an intervention for effectiveness tracking"""
        density_reduction = pre_density - (post_density or pre_density)
        effectiveness_score = min(1.0, density_reduction / max(1.0, pre_density))  # Normalize
        
        # Target met if density reduced by at least 20%
        target_met = density_reduction >= (pre_density * 0.2)
        
        effectiveness = InterventionEffectiveness(
            intervention_id=intervention_id,
            action_type=action_type,
            node_id=node_id,
            applied_at=applied_at,
            pre_density=pre_density,
            post_density=post_density or pre_density,
            density_reduction=density_reduction,
            effectiveness_score=effectiveness_score,
            target_met=target_met,
            measured_at=applied_at,
        )
        
        self.intervention_history.append(effectiveness)
        
        # Keep only recent history
        if len(self.intervention_history) > 1000:
            self.intervention_history = self.intervention_history[-1000:]
    
    def measure_intervention_effectiveness(
        self,
        intervention_id: str,
        current_density: float,
        current_time: float
    ) -> Optional[InterventionEffectiveness]:
        """Measure effectiveness of an intervention after some time"""
        # Find the intervention
        intervention = None
        for eff in reversed(self.intervention_history):
            if eff.intervention_id == intervention_id:
                intervention = eff
                break
        
        if not intervention:
            return None
        
        # Update effectiveness
        post_density = current_density
        density_reduction = intervention.pre_density - post_density
        effectiveness_score = min(1.0, density_reduction / max(1.0, intervention.pre_density))
        target_met = density_reduction >= (intervention.pre_density * 0.2)
        
        intervention.post_density = post_density
        intervention.density_reduction = density_reduction
        intervention.effectiveness_score = effectiveness_score
        intervention.target_met = target_met
        intervention.measured_at = current_time
        
        return intervention
    
    def predict_stampede_probability(
        self,
        node_densities: Dict[str, float],
        current_time: float,
        active_triggers: List[any],
        intervention_frequency: float = 0.0
    ) -> StampedePrediction:
        """
        Predict stampede probability based on current conditions
        
        Args:
            node_densities: Current densities per node
            current_time: Current simulation time
            active_triggers: List of active trigger events
            intervention_frequency: Number of interventions per minute
        
        Returns:
            StampedePrediction: Prediction with probability and risk level
        """
        # Calculate risk factors
        max_density = max(node_densities.values()) if node_densities else 0.0
        danger_zones = [node for node, density in node_densities.items() if density >= 4.0]
        high_density_zones = [node for node, density in node_densities.items() if density >= 3.0]
        
        # Base probability from density
        density_prob = min(1.0, max(0.0, (max_density - 2.0) / 4.0))  # 0 at 2.0, 1.0 at 6.0
        
        # Trigger events increase probability
        trigger_factor = len(active_triggers) * 0.2  # Each trigger adds 20%
        
        # High intervention frequency indicates instability (increases risk)
        frequency_factor = min(0.3, intervention_frequency / 10.0)  # Max 30% from frequency
        
        # Multiple danger zones increase risk
        zone_factor = min(0.2, len(danger_zones) * 0.1)  # Max 20% from multiple zones
        
        # Calculate combined probability
        probability = min(1.0, density_prob * 0.5 + trigger_factor + frequency_factor + zone_factor)
        
        # Determine risk level
        if probability >= 0.8:
            risk_level = "CRITICAL"
        elif probability >= 0.6:
            risk_level = "HIGH"
        elif probability >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Contributing factors
        factors = []
        if max_density >= 4.0:
            factors.append(f"High density ({max_density:.1f} p/m²)")
        if len(active_triggers) > 0:
            factors.append(f"{len(active_triggers)} active trigger(s)")
        if len(danger_zones) > 1:
            factors.append(f"{len(danger_zones)} danger zones")
        if intervention_frequency > 5:
            factors.append("High intervention frequency")
        
        # Confidence based on data quality
        confidence = min(1.0, len(self.density_history) / 100.0)  # More history = more confidence
        
        # Predict time (if probability is high)
        predicted_time = None
        if probability >= 0.6:
            # Estimate time based on density trend
            if len(self.density_history) >= 2:
                recent = self.density_history[-1]
                previous = self.density_history[-2] if len(self.density_history) >= 2 else None
                if previous:
                    time_delta = recent[0] - previous[0]
                    density_delta = max_density - max(previous[1].values()) if previous[1] else 0
                    if density_delta > 0 and time_delta > 0:
                        rate = density_delta / time_delta
                        if rate > 0:
                            time_to_critical = (6.0 - max_density) / rate  # Time to reach 6.0
                            predicted_time = current_time + time_to_critical
        
        prediction = StampedePrediction(
            probability=probability,
            risk_level=risk_level,
            predicted_time=predicted_time,
            contributing_factors=factors,
            confidence=confidence,
            last_updated=current_time,
        )
        
        self.stampede_predictions.append(prediction)
        
        # Keep only recent predictions
        if len(self.stampede_predictions) > 100:
            self.stampede_predictions = self.stampede_predictions[-100:]
        
        return prediction
    
    def calculate_system_health(
        self,
        current_time: float,
        node_densities: Dict[str, float],
        active_interventions: int,
        danger_zone_count: int
    ) -> SystemHealthMetrics:
        """
        Calculate system health metrics
        
        Args:
            current_time: Current simulation time
            node_densities: Current densities per node
            active_interventions: Number of active interventions
            danger_zone_count: Number of danger zones
        
        Returns:
            SystemHealthMetrics: Current health status
        """
        max_density = max(node_densities.values()) if node_densities else 0.0
        
        # Calculate intervention frequency (per minute)
        if len(self.intervention_history) > 1:
            time_span = current_time - self.intervention_history[0].applied_at
            intervention_count = len(self.intervention_history)
            intervention_frequency = (intervention_count / max(time_span, 1.0)) * 60.0  # Per minute
        else:
            intervention_frequency = 0.0
        
        # Calculate average effectiveness
        if self.intervention_history:
            recent_effects = [e for e in self.intervention_history if e.effectiveness_score > 0]
            if recent_effects:
                average_effectiveness = sum(e.effectiveness_score for e in recent_effects) / len(recent_effects)
            else:
                average_effectiveness = 0.0
        else:
            average_effectiveness = 0.0
        
        # Calculate system stability (lower intervention frequency + higher effectiveness = more stable)
        stability_score = 1.0 - min(1.0, intervention_frequency / 20.0)  # Penalize high frequency
        stability_score = stability_score * (0.5 + average_effectiveness * 0.5)  # Reward effectiveness
        
        # Determine overall status
        if max_density >= 6.0 or danger_zone_count >= 5:
            overall_status = HealthStatus.CRITICAL
        elif max_density >= 4.0 or danger_zone_count >= 3 or intervention_frequency > 10:
            overall_status = HealthStatus.WARNING
        elif max_density < 3.0 and danger_zone_count == 0 and intervention_frequency < 5:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.WARNING
        
        metrics = SystemHealthMetrics(
            overall_status=overall_status,
            intervention_frequency=intervention_frequency,
            average_effectiveness=average_effectiveness,
            danger_zone_count=danger_zone_count,
            max_density=max_density,
            active_interventions=active_interventions,
            system_stability=stability_score,
            last_updated=current_time,
        )
        
        self.health_metrics = metrics
        return metrics
    
    def record_density_snapshot(self, current_time: float, node_densities: Dict[str, float]):
        """Record a density snapshot for trend analysis"""
        self.density_history.append((current_time, node_densities.copy()))
        
        # Keep only recent history
        if len(self.density_history) > self.max_history_size:
            self.density_history = self.density_history[-self.max_history_size:]
    
    def get_intervention_statistics(self, time_window: Optional[float] = None) -> Dict:
        """Get statistics about interventions"""
        if not self.intervention_history:
            return {
                "total_interventions": 0,
                "average_effectiveness": 0.0,
                "target_met_rate": 0.0,
                "recent_effectiveness": 0.0,
            }
        
        # Filter by time window if specified
        if time_window:
            cutoff_time = self.intervention_history[-1].applied_at - time_window
            interventions = [e for e in self.intervention_history if e.applied_at >= cutoff_time]
        else:
            interventions = self.intervention_history
        
        total = len(interventions)
        if total == 0:
            return {
                "total_interventions": 0,
                "average_effectiveness": 0.0,
                "target_met_rate": 0.0,
                "recent_effectiveness": 0.0,
            }
        
        avg_effectiveness = sum(e.effectiveness_score for e in interventions) / total
        target_met_count = sum(1 for e in interventions if e.target_met)
        target_met_rate = target_met_count / total if total > 0 else 0.0
        
        # Recent effectiveness (last 10)
        recent = interventions[-10:] if len(interventions) >= 10 else interventions
        recent_effectiveness = sum(e.effectiveness_score for e in recent) / len(recent) if recent else 0.0
        
        return {
            "total_interventions": total,
            "average_effectiveness": avg_effectiveness,
            "target_met_rate": target_met_rate,
            "recent_effectiveness": recent_effectiveness,
        }
    
    def get_latest_stampede_prediction(self) -> Optional[StampedePrediction]:
        """Get the latest stampede prediction"""
        return self.stampede_predictions[-1] if self.stampede_predictions else None
    
    def get_current_health(self) -> Optional[SystemHealthMetrics]:
        """Get current system health metrics"""
        return self.health_metrics
    
    def reset(self):
        """Reset monitoring data"""
        self.intervention_history.clear()
        self.stampede_predictions.clear()
        self.health_metrics = None
        self.density_history.clear()


# Global instance
advanced_monitoring = AdvancedMonitoring()

