"""
PHASE 3: Risk Assessment Module
Classifies intervention risk levels for controlled autonomy
"""
from typing import Dict, Any, Optional
from enum import Enum


class RiskLevel(Enum):
    """Intervention risk levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InterventionRiskAssessment:
    """
    Assesses risk level of interventions for Phase 3: Controlled Autonomy
    
    Risk Classification:
    - LOW: Safe to auto-execute (THROTTLE_25, REROUTE when density < 3.5)
    - MEDIUM: Requires approval (THROTTLE_50, REROUTE when density > 3.5)
    - HIGH: Always requires approval (CLOSE_INFLOW, trigger events)
    """
    
    # Risk thresholds
    LOW_DENSITY_THRESHOLD = 3.5  # Density below this = LOW risk for REROUTE
    
    # Action risk mapping (base risk level)
    ACTION_RISK_MAP = {
        "THROTTLE_25": RiskLevel.LOW,
        "THROTTLE_50": RiskLevel.MEDIUM,
        "CLOSE_INFLOW": RiskLevel.HIGH,
        "REROUTE": RiskLevel.LOW,  # Base is LOW, but can be MEDIUM based on density
        "NOOP": RiskLevel.LOW,
    }
    
    def __init__(self):
        """Initialize risk assessor"""
        pass
    
    def assess_risk(
        self, 
        action: str, 
        context: Dict[str, Any],
        recommendation_action: Optional[str] = None
    ) -> RiskLevel:
        """
        Assess risk level of an intervention action.
        
        Args:
            action: Intervention action (THROTTLE_25, THROTTLE_50, CLOSE_INFLOW, REROUTE)
            context: Context dict with:
                - node_id: Target node
                - density: Current density at node
                - priority: Recommendation priority (CRITICAL, WARNING, INFO)
                - has_active_trigger: bool - Whether trigger events are active
                - simulation_time: float - Current simulation time
            recommendation_action: Original recommendation action (CLOSE_TEMPORARILY, REDUCE_FLOW, etc.)
        
        Returns:
            RiskLevel: LOW, MEDIUM, or HIGH
        """
        # Map recommendation actions to intervention actions if needed
        if recommendation_action:
            action = self._map_recommendation_action(recommendation_action, context)
        
        # Base risk from action type
        base_risk = self.ACTION_RISK_MAP.get(action, RiskLevel.HIGH)
        
        # High-risk actions always require approval
        if base_risk == RiskLevel.HIGH:
            return RiskLevel.HIGH
        
        # Check for active triggers (always increases risk)
        if context.get("has_active_trigger", False):
            return RiskLevel.HIGH
        
        # REROUTE risk depends on density
        if action == "REROUTE":
            density = context.get("density", 0.0)
            if density >= self.LOW_DENSITY_THRESHOLD:
                return RiskLevel.MEDIUM  # Higher density = higher risk
            else:
                return RiskLevel.LOW
        
        # THROTTLE_25 is always LOW risk
        if action == "THROTTLE_25":
            return RiskLevel.LOW
        
        # THROTTLE_50 is MEDIUM by default
        if action == "THROTTLE_50":
            # Can be HIGH if density is extremely high
            density = context.get("density", 0.0)
            if density > 5.0:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
        
        # Default: return base risk
        return base_risk
    
    def _map_recommendation_action(self, recommendation_action: str, context: Dict) -> str:
        """Map recommendation action to intervention action"""
        mapping = {
            "CLOSE_TEMPORARILY": "CLOSE_INFLOW",
            "REDUCE_FLOW": self._determine_throttle_level(context),
            "REROUTE": "REROUTE",
        }
        return mapping.get(recommendation_action, "NOOP")
    
    def _determine_throttle_level(self, context: Dict) -> str:
        """Determine throttle level based on priority and density"""
        priority = context.get("priority", "WARNING")
        if priority == "CRITICAL":
            return "THROTTLE_50"
        return "THROTTLE_25"
    
    def should_auto_execute(
        self, 
        action: str, 
        context: Dict[str, Any],
        auto_execute_enabled: bool = True
    ) -> bool:
        """
        Determine if action should be auto-executed.
        
        Args:
            action: Intervention action
            context: Context dict
            auto_execute_enabled: Whether auto-execution is enabled for this simulation
        
        Returns:
            bool: True if should auto-execute, False if requires approval
        """
        if not auto_execute_enabled:
            return False
        
        risk_level = self.assess_risk(action, context)
        
        # Only LOW risk actions can be auto-executed
        return risk_level == RiskLevel.LOW
    
    def get_risk_explanation(self, action: str, context: Dict[str, Any]) -> str:
        """Get human-readable explanation of risk assessment"""
        risk_level = self.assess_risk(action, context)
        
        explanations = {
            RiskLevel.LOW: f"{action} is LOW risk - safe to auto-execute. This is a gentle intervention with minimal impact.",
            RiskLevel.MEDIUM: f"{action} is MEDIUM risk - requires supervisor approval. This intervention has moderate impact and should be reviewed.",
            RiskLevel.HIGH: f"{action} is HIGH risk - always requires approval. This is a critical intervention with significant impact.",
        }
        
        base_explanation = explanations.get(risk_level, f"{action} risk assessment: {risk_level.value}")
        
        # Add context-specific details
        if context.get("has_active_trigger"):
            base_explanation += " Active trigger event increases risk level."
        
        density = context.get("density", 0.0)
        if density > self.LOW_DENSITY_THRESHOLD and action == "REROUTE":
            base_explanation += f" High density ({density:.1f} p/m²) increases rerouting risk."
        
        return base_explanation


# Global instance
risk_assessor = InterventionRiskAssessment()

