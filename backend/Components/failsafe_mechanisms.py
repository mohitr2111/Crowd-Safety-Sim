"""
PHASE 4: Fail-Safe Mechanisms Module
Maximum intervention frequency, minimum time between interventions, rollback capability, safety constraints
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class SafetyConstraint(Enum):
    """Types of safety constraints"""
    MAX_FREQUENCY = "max_frequency"  # Maximum interventions per time window
    MIN_INTERVAL = "min_interval"  # Minimum time between interventions
    MAX_ACTIVE = "max_active"  # Maximum active interventions
    ROLLBACK = "rollback"  # Rollback capability
    MANUAL_OVERRIDE = "manual_override"  # Manual override always available


@dataclass
class InterventionRecord:
    """Record of an intervention for rollback"""
    intervention_id: str
    action_type: str
    node_id: str
    applied_at: float
    parameters: Dict[str, Any]  # Action-specific parameters
    rollback_data: Dict[str, Any]  # Data needed for rollback
    can_rollback: bool = True
    rolled_back: bool = False
    rolled_back_at: Optional[float] = None


@dataclass
class SafetyConstraints:
    """Safety constraint configuration"""
    max_interventions_per_minute: float = 10.0  # Max interventions per minute
    min_interval_seconds: float = 5.0  # Minimum seconds between interventions
    max_active_interventions: int = 5  # Max simultaneous active interventions
    enable_rollback: bool = True  # Enable rollback capability
    enable_manual_override: bool = True  # Always allow manual override


@dataclass
class SafetyViolation:
    """Record of a safety constraint violation"""
    violation_type: str
    intervention_id: Optional[str]
    timestamp: float
    constraint_name: str
    actual_value: float
    limit_value: float
    was_blocked: bool  # Whether intervention was blocked due to violation
    message: str


class FailSafeMechanisms:
    """
    PHASE 4: Fail-Safe Mechanisms
    
    Enforces safety constraints:
    - Maximum intervention frequency (prevent oscillation)
    - Minimum time between interventions
    - Maximum active interventions
    - Rollback capability
    - Manual override always available
    """
    
    def __init__(self):
        """Initialize fail-safe mechanisms"""
        self.intervention_history: List[InterventionRecord] = []
        self.safety_constraints = SafetyConstraints()
        self.violations: List[SafetyViolation] = []
        self.active_interventions: Dict[str, InterventionRecord] = {}
        self.rollback_stack: List[InterventionRecord] = []  # For rollback operations
    
    def configure_constraints(
        self,
        max_interventions_per_minute: Optional[float] = None,
        min_interval_seconds: Optional[float] = None,
        max_active_interventions: Optional[int] = None,
        enable_rollback: Optional[bool] = None,
        enable_manual_override: Optional[bool] = None
    ):
        """Configure safety constraints"""
        if max_interventions_per_minute is not None:
            self.safety_constraints.max_interventions_per_minute = max_interventions_per_minute
        if min_interval_seconds is not None:
            self.safety_constraints.min_interval_seconds = min_interval_seconds
        if max_active_interventions is not None:
            self.safety_constraints.max_active_interventions = max_active_interventions
        if enable_rollback is not None:
            self.safety_constraints.enable_rollback = enable_rollback
        if enable_manual_override is not None:
            self.safety_constraints.enable_manual_override = enable_manual_override
    
    def check_safety_constraints(
        self,
        intervention_id: str,
        action_type: str,
        node_id: str,
        current_time: float,
        is_manual: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if intervention violates safety constraints
        
        Args:
            intervention_id: Unique intervention ID
            action_type: Type of intervention
            node_id: Target node
            current_time: Current simulation time
            is_manual: Whether this is a manual override
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        # Manual overrides always allowed
        if is_manual and self.safety_constraints.enable_manual_override:
            return True, None
        
        # Check minimum interval
        if len(self.intervention_history) > 0:
            last_intervention = self.intervention_history[-1]
            time_since_last = current_time - last_intervention.applied_at
            if time_since_last < self.safety_constraints.min_interval_seconds:
                violation = SafetyViolation(
                    violation_type=SafetyConstraint.MIN_INTERVAL.value,
                    intervention_id=intervention_id,
                    timestamp=current_time,
                    constraint_name="min_interval_seconds",
                    actual_value=time_since_last,
                    limit_value=self.safety_constraints.min_interval_seconds,
                    was_blocked=True,
                    message=f"Minimum interval violated: {time_since_last:.1f}s < {self.safety_constraints.min_interval_seconds:.1f}s"
                )
                self.violations.append(violation)
                return False, violation.message
        
        # Check maximum active interventions
        active_count = len(self.active_interventions)
        if active_count >= self.safety_constraints.max_active_interventions:
            violation = SafetyViolation(
                violation_type=SafetyConstraint.MAX_ACTIVE.value,
                intervention_id=intervention_id,
                timestamp=current_time,
                constraint_name="max_active_interventions",
                actual_value=active_count,
                limit_value=self.safety_constraints.max_active_interventions,
                was_blocked=True,
                message=f"Maximum active interventions reached: {active_count} >= {self.safety_constraints.max_active_interventions}"
            )
            self.violations.append(violation)
            return False, violation.message
        
        # Check maximum frequency (interventions per minute)
        if len(self.intervention_history) > 0:
            # Check interventions in last minute
            one_minute_ago = current_time - 60.0
            recent_interventions = [
                i for i in self.intervention_history
                if i.applied_at >= one_minute_ago
            ]
            frequency = len(recent_interventions) / 60.0 * 60.0  # Per minute
            
            if frequency >= self.safety_constraints.max_interventions_per_minute:
                violation = SafetyViolation(
                    violation_type=SafetyConstraint.MAX_FREQUENCY.value,
                    intervention_id=intervention_id,
                    timestamp=current_time,
                    constraint_name="max_interventions_per_minute",
                    actual_value=frequency,
                    limit_value=self.safety_constraints.max_interventions_per_minute,
                    was_blocked=True,
                    message=f"Maximum frequency violated: {frequency:.1f} >= {self.safety_constraints.max_interventions_per_minute:.1f} per minute"
                )
                self.violations.append(violation)
                return False, violation.message
        
        return True, None
    
    def record_intervention(
        self,
        intervention_id: str,
        action_type: str,
        node_id: str,
        current_time: float,
        parameters: Dict[str, Any],
        rollback_data: Dict[str, Any],
        is_manual: bool = False
    ) -> InterventionRecord:
        """
        Record an intervention (after safety checks passed)
        
        Args:
            intervention_id: Unique intervention ID
            action_type: Type of intervention
            node_id: Target node
            current_time: Current simulation time
            parameters: Action-specific parameters
            rollback_data: Data needed for rollback
            is_manual: Whether this was a manual override
        
        Returns:
            InterventionRecord: Recorded intervention
        """
        record = InterventionRecord(
            intervention_id=intervention_id,
            action_type=action_type,
            node_id=node_id,
            applied_at=current_time,
            parameters=parameters,
            rollback_data=rollback_data,
            can_rollback=self.safety_constraints.enable_rollback,
        )
        
        self.intervention_history.append(record)
        self.active_interventions[intervention_id] = record
        
        # Add to rollback stack
        if self.safety_constraints.enable_rollback:
            self.rollback_stack.append(record)
        
        # Keep only recent history
        if len(self.intervention_history) > 1000:
            self.intervention_history = self.intervention_history[-1000:]
        
        # Keep only recent violations
        if len(self.violations) > 100:
            self.violations = self.violations[-100:]
        
        return record
    
    def complete_intervention(self, intervention_id: str):
        """Mark an intervention as completed (no longer active)"""
        if intervention_id in self.active_interventions:
            del self.active_interventions[intervention_id]
    
    def rollback_intervention(
        self,
        intervention_id: Optional[str] = None,
        current_time: float = 0.0
    ) -> Optional[InterventionRecord]:
        """
        Rollback an intervention (most recent if no ID specified)
        
        Args:
            intervention_id: ID of intervention to rollback (None = most recent)
            current_time: Current simulation time
        
        Returns:
            InterventionRecord: Rolled back intervention, or None if not possible
        """
        if not self.safety_constraints.enable_rollback:
            return None
        
        # Find intervention to rollback
        if intervention_id:
            # Find specific intervention
            record = None
            for r in reversed(self.rollback_stack):
                if r.intervention_id == intervention_id and not r.rolled_back:
                    record = r
                    break
        else:
            # Rollback most recent
            record = None
            for r in reversed(self.rollback_stack):
                if not r.rolled_back and r.can_rollback:
                    record = r
                    break
        
        if not record:
            return None
        
        # Mark as rolled back
        record.rolled_back = True
        record.rolled_back_at = current_time
        
        # Remove from active
        if record.intervention_id in self.active_interventions:
            del self.active_interventions[record.intervention_id]
        
        return record
    
    def get_safety_status(self, current_time: float) -> Dict:
        """Get current safety status"""
        # Calculate current frequency
        if len(self.intervention_history) > 0:
            one_minute_ago = current_time - 60.0
            recent = [i for i in self.intervention_history if i.applied_at >= one_minute_ago]
            current_frequency = len(recent)  # Per minute
        else:
            current_frequency = 0.0
        
        # Calculate time since last intervention
        time_since_last = None
        if len(self.intervention_history) > 0:
            time_since_last = current_time - self.intervention_history[-1].applied_at
        
        # Count violations
        recent_violations = [v for v in self.violations if current_time - v.timestamp < 300.0]  # Last 5 minutes
        
        return {
            "constraints": {
                "max_interventions_per_minute": self.safety_constraints.max_interventions_per_minute,
                "min_interval_seconds": self.safety_constraints.min_interval_seconds,
                "max_active_interventions": self.safety_constraints.max_active_interventions,
                "enable_rollback": self.safety_constraints.enable_rollback,
                "enable_manual_override": self.safety_constraints.enable_manual_override,
            },
            "current_status": {
                "current_frequency": current_frequency,
                "time_since_last": time_since_last,
                "active_interventions": len(self.active_interventions),
                "total_interventions": len(self.intervention_history),
                "violations_last_5min": len(recent_violations),
            },
            "can_intervene": current_frequency < self.safety_constraints.max_interventions_per_minute,
            "active_intervention_ids": list(self.active_interventions.keys()),
        }
    
    def get_recent_violations(self, time_window: float = 300.0) -> List[Dict]:
        """Get recent safety violations"""
        cutoff_time = max(v.timestamp for v in self.violations) - time_window if self.violations else 0.0
        recent = [v for v in self.violations if v.timestamp >= cutoff_time]
        
        return [
            {
                "violation_type": v.violation_type,
                "intervention_id": v.intervention_id,
                "timestamp": v.timestamp,
                "constraint_name": v.constraint_name,
                "actual_value": v.actual_value,
                "limit_value": v.limit_value,
                "was_blocked": v.was_blocked,
                "message": v.message,
            }
            for v in recent
        ]
    
    def reset(self):
        """Reset fail-safe mechanisms"""
        self.intervention_history.clear()
        self.violations.clear()
        self.active_interventions.clear()
        self.rollback_stack.clear()


# Global instance
failsafe_mechanisms = FailSafeMechanisms()

