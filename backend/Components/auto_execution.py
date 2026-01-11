"""
PHASE 3: Auto-Execution Engine for Controlled Autonomy
Handles automatic execution of low-risk interventions and pending actions queue
"""
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from Components.risk_assessment import risk_assessor, RiskLevel


@dataclass
class PendingIntervention:
    """Represents a pending intervention awaiting approval"""
    action_id: str
    node_id: str
    action: str  # Intervention action (THROTTLE_25, THROTTLE_50, etc.)
    recommendation_action: str  # Original recommendation action
    priority: str  # CRITICAL, WARNING, INFO
    risk_level: str  # LOW, MEDIUM, HIGH
    context: Dict[str, Any]
    created_at: float  # Simulation time when created
    explanation: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED, EXECUTED
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class AutoExecutionEngine:
    """
    PHASE 3: Auto-Execution Engine
    
    Manages:
    - Auto-execution of low-risk interventions
    - Pending actions queue for medium/high-risk interventions
    - Supervisor override capabilities
    """
    
    def __init__(self):
        """Initialize auto-execution engine"""
        self.pending_actions: Dict[str, List[PendingIntervention]] = {}  # simulation_id -> list of pending
        self.execution_settings: Dict[str, Dict[str, Any]] = {}  # simulation_id -> settings
        self.audit_log: Dict[str, List[Dict]] = {}  # simulation_id -> audit entries
    
    def initialize_simulation(self, simulation_id: str, auto_execute_enabled: bool = True):
        """Initialize auto-execution for a simulation"""
        self.pending_actions[simulation_id] = []
        self.execution_settings[simulation_id] = {
            "auto_execute_enabled": auto_execute_enabled,
            "disabled_nodes": [],  # Nodes where auto-execution is disabled
            "max_pending_actions": 10,  # Maximum pending actions before blocking
        }
        self.audit_log[simulation_id] = []
    
    def process_recommendation(
        self,
        simulation_id: str,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a recommendation and decide: auto-execute or add to pending queue
        
        Args:
            simulation_id: Simulation ID
            recommendation: Recommendation dict with node_id, action, priority, etc.
            context: Context dict with density, trigger state, etc.
        
        Returns:
            Dict with:
                - status: "AUTO_EXECUTED", "PENDING", "REQUIRES_APPROVAL"
                - action_id: ID of action (if pending)
                - intervention: Intervention details
        """
        if simulation_id not in self.execution_settings:
            self.initialize_simulation(simulation_id)
        
        settings = self.execution_settings[simulation_id]
        
        # Check if auto-execution is disabled
        if not settings["auto_execute_enabled"]:
            return {
                "status": "REQUIRES_APPROVAL",
                "reason": "Auto-execution disabled for this simulation"
            }
        
        # Check if node is disabled
        node_id = recommendation.get("node_id")
        if node_id in settings["disabled_nodes"]:
            return {
                "status": "REQUIRES_APPROVAL",
                "reason": f"Auto-execution disabled for node {node_id}"
            }
        
        # Map recommendation action to intervention action
        recommendation_action = recommendation.get("action")
        intervention_action = self._map_recommendation_action(recommendation_action, recommendation)
        
        # Build context for risk assessment
        assessment_context = {
            "node_id": node_id,
            "density": context.get("density", 0.0),
            "priority": recommendation.get("priority", "WARNING"),
            "has_active_trigger": context.get("has_active_trigger", False),
            "simulation_time": context.get("simulation_time", 0.0),
        }
        
        # Assess risk
        risk_level = risk_assessor.assess_risk(
            intervention_action,
            assessment_context,
            recommendation_action
        )
        
        # Check if should auto-execute
        should_auto = risk_assessor.should_auto_execute(
            intervention_action,
            assessment_context,
            settings["auto_execute_enabled"]
        )
        
        # Get explanation
        explanation = risk_assessor.get_risk_explanation(intervention_action, assessment_context)
        
        if should_auto and risk_level == RiskLevel.LOW:
            # Auto-execute low-risk interventions
            return {
                "status": "AUTO_EXECUTED",
                "intervention": {
                    "node_id": node_id,
                    "action": intervention_action,
                    "recommendation_action": recommendation_action,
                    "priority": recommendation.get("priority"),
                    "risk_level": risk_level.value,
                },
                "explanation": explanation,
            }
        else:
            # Add to pending queue
            action_id = str(uuid.uuid4())
            pending = PendingIntervention(
                action_id=action_id,
                node_id=node_id,
                action=intervention_action,
                recommendation_action=recommendation_action,
                priority=recommendation.get("priority", "WARNING"),
                risk_level=risk_level.value,
                context=assessment_context,
                created_at=context.get("simulation_time", 0.0),
                explanation=explanation,
            )
            
            # Add to pending queue
            if simulation_id not in self.pending_actions:
                self.pending_actions[simulation_id] = []
            
            # Check max pending limit
            if len(self.pending_actions[simulation_id]) >= settings["max_pending_actions"]:
                return {
                    "status": "QUEUE_FULL",
                    "reason": "Pending actions queue is full",
                }
            
            self.pending_actions[simulation_id].append(pending)
            
            # Log to audit
            self._log_action(simulation_id, {
                "type": "PENDING_ADDED",
                "action_id": action_id,
                "node_id": node_id,
                "action": intervention_action,
                "risk_level": risk_level.value,
                "time": context.get("simulation_time", 0.0),
            })
            
            return {
                "status": "PENDING",
                "action_id": action_id,
                "intervention": pending.to_dict(),
            }
    
    def _map_recommendation_action(self, recommendation_action: str, recommendation: Dict) -> str:
        """Map recommendation action to intervention action"""
        mapping = {
            "CLOSE_TEMPORARILY": "CLOSE_INFLOW",
            "REDUCE_FLOW": "THROTTLE_25" if recommendation.get("priority") == "WARNING" else "THROTTLE_50",
            "REROUTE": "REROUTE",
        }
        return mapping.get(recommendation_action, "NOOP")
    
    def get_pending_actions(self, simulation_id: str) -> List[Dict]:
        """Get all pending actions for a simulation"""
        if simulation_id not in self.pending_actions:
            return []
        return [p.to_dict() for p in self.pending_actions[simulation_id] if p.status == "PENDING"]
    
    def approve_action(self, simulation_id: str, action_id: str) -> Optional[PendingIntervention]:
        """Approve a pending action"""
        if simulation_id not in self.pending_actions:
            return None
        
        for pending in self.pending_actions[simulation_id]:
            if pending.action_id == action_id and pending.status == "PENDING":
                pending.status = "APPROVED"
                
                # Log to audit
                self._log_action(simulation_id, {
                    "type": "ACTION_APPROVED",
                    "action_id": action_id,
                    "node_id": pending.node_id,
                    "action": pending.action,
                    "time": pending.created_at,
                })
                
                return pending
        return None
    
    def reject_action(self, simulation_id: str, action_id: str) -> Optional[PendingIntervention]:
        """Reject a pending action"""
        if simulation_id not in self.pending_actions:
            return None
        
        for pending in self.pending_actions[simulation_id]:
            if pending.action_id == action_id and pending.status == "PENDING":
                pending.status = "REJECTED"
                
                # Log to audit
                self._log_action(simulation_id, {
                    "type": "ACTION_REJECTED",
                    "action_id": action_id,
                    "node_id": pending.node_id,
                    "action": pending.action,
                    "time": pending.created_at,
                })
                
                return pending
        return None
    
    def update_settings(
        self,
        simulation_id: str,
        auto_execute_enabled: Optional[bool] = None,
        disabled_nodes: Optional[List[str]] = None
    ):
        """Update auto-execution settings"""
        if simulation_id not in self.execution_settings:
            self.initialize_simulation(simulation_id)
        
        settings = self.execution_settings[simulation_id]
        
        if auto_execute_enabled is not None:
            settings["auto_execute_enabled"] = auto_execute_enabled
        
        if disabled_nodes is not None:
            settings["disabled_nodes"] = disabled_nodes
    
    def get_audit_log(self, simulation_id: str, limit: int = 100) -> List[Dict]:
        """Get audit log for a simulation"""
        if simulation_id not in self.audit_log:
            return []
        return self.audit_log[simulation_id][-limit:]
    
    def _log_action(self, simulation_id: str, entry: Dict):
        """Log an action to audit trail"""
        if simulation_id not in self.audit_log:
            self.audit_log[simulation_id] = []
        
        self.audit_log[simulation_id].append({
            **entry,
            "timestamp": datetime.now().isoformat(),
        })


# Global instance
auto_execution_engine = AutoExecutionEngine()

