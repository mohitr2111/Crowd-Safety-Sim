# backend/ai/intervention_engine.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import sys
import os

# Add parent directory to path to import other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from events.cascade_effects import CascadeChain, CascadeState, CascadeType
from ai.stampede_predictor import StampedePrediction, RiskLevel

class InterventionType(Enum):
    """Types of interventions"""
    CLOSE_ENTRY = "close_entry"
    OPEN_EXIT = "open_exit"
    REROUTE_FLOW = "reroute_flow"
    DEPLOY_STAFF = "deploy_staff"
    STOP_UPSTREAM = "stop_upstream"
    EMERGENCY_EVACUATION = "emergency_evacuation"
    ACTIVATE_ALTERNATIVE = "activate_alternative"
    COMMUNICATION_ANNOUNCEMENT = "communication_announcement"

class InterventionUrgency(Enum):
    """How urgent the intervention is"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    IMMEDIATE = "immediate"

@dataclass
class InterventionOption:
    """A specific intervention recommendation"""
    intervention_id: str
    intervention_type: InterventionType
    urgency: InterventionUrgency
    target_zone: str
    action_description: str
    
    # Timing
    recommended_step: int
    deadline_step: int  # Must act before this
    
    # Impact predictions
    expected_lives_saved: int
    expected_density_reduction: float  # p/m²
    success_probability: float  # 0-1
    
    # Costs
    implementation_time: int  # Steps to implement
    inconvenience_cost: float  # 0-1, how much disruption
    resource_cost: str  # "Low", "Medium", "High"
    
    # Context
    reasoning: List[str]
    risks_if_ignored: List[str]
    prerequisites: List[str] = field(default_factory=list)

@dataclass
class InterventionPlan:
    """Complete intervention plan with alternatives"""
    plan_id: str
    primary_option: InterventionOption
    alternative_options: List[InterventionOption]
    combined_impact: Dict[str, float]
    confidence: float

class InterventionEngine:
    """
    Recommends specific interventions to prevent stampedes
    """
    
    # Impact estimation constants
    LIVES_PER_DENSITY_UNIT = 15  # Rough estimate: 1 p/m² reduction = 15 lives
    
    def __init__(self):
        self.intervention_counter = 0
        self.issued_interventions: List[InterventionOption] = []
    
    def recommend_for_cascade(self, cascade: CascadeChain, 
                             current_step: int) -> Optional[InterventionPlan]:
        """
        Recommend interventions for an active cascade
        """
        if cascade.state == CascadeState.RESOLVED:
            return None
        
        # Generate intervention options based on cascade type
        if cascade.cascade_type == CascadeType.BOTTLENECK_BACKUP:
            return self._recommend_for_bottleneck(cascade, current_step)
        
        elif cascade.cascade_type == CascadeType.PANIC_SPREAD:
            return self._recommend_for_panic(cascade, current_step)
        
        elif cascade.cascade_type == CascadeType.DOMINO_OVERFLOW:
            return self._recommend_for_overflow(cascade, current_step)
        
        return None
    
    def recommend_for_prediction(self, prediction: StampedePrediction,
                                 current_step: int) -> Optional[InterventionPlan]:
        """
        Recommend interventions based on stampede prediction
        """
        if prediction.risk_level in [RiskLevel.SAFE, RiskLevel.LOW]:
            return None
        
        # Determine urgency
        if prediction.risk_level == RiskLevel.IMMINENT:
            urgency = InterventionUrgency.IMMEDIATE
        elif prediction.risk_level == RiskLevel.CRITICAL:
            urgency = InterventionUrgency.CRITICAL
        elif prediction.risk_level == RiskLevel.HIGH:
            urgency = InterventionUrgency.HIGH
        else:
            urgency = InterventionUrgency.MODERATE
        
        # Generate options
        primary = self._create_density_reduction_intervention(
            prediction.zone_id,
            current_step,
            prediction,
            urgency
        )
        
        alternatives = self._generate_alternatives(
            prediction.zone_id,
            current_step,
            prediction
        )
        
        plan = InterventionPlan(
            plan_id=f"plan_{self.intervention_counter}",
            primary_option=primary,
            alternative_options=alternatives,
            combined_impact={
                "expected_density": prediction.predicted_peak_density - primary.expected_density_reduction,
                "risk_reduction": prediction.probability * primary.success_probability
            },
            confidence=prediction.confidence * 0.9
        )
        
        self.intervention_counter += 1
        return plan
    
    def _recommend_for_bottleneck(self, cascade: CascadeChain, 
                                  current_step: int) -> InterventionPlan:
        """Recommend interventions for bottleneck cascade"""
        
        # Primary: Stop upstream flow
        primary = InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_primary",
            intervention_type=InterventionType.STOP_UPSTREAM,
            urgency=self._determine_urgency(cascade),
            target_zone=cascade.origin_zone,
            action_description=f"Stop new entries to {cascade.origin_zone}",
            recommended_step=current_step,
            deadline_step=current_step + 5,
            expected_lives_saved=int(cascade.current_severity * 50),
            expected_density_reduction=2.5,
            success_probability=0.85,
            implementation_time=1,
            inconvenience_cost=0.6,
            resource_cost="Low",
            reasoning=[
                "Bottleneck detected in origin zone",
                f"Cascade affecting {len(cascade.affected_zones)} zones",
                "Stopping upstream prevents further backup"
            ],
            risks_if_ignored=[
                "Cascade will propagate to adjacent zones",
                f"Estimated stampede in {self._estimate_time_to_stampede(cascade)} steps",
                "Density could reach critical levels"
            ]
        )
        
        # Alternative 1: Open alternative route
        alt1 = InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_alt1",
            intervention_type=InterventionType.ACTIVATE_ALTERNATIVE,
            urgency=self._determine_urgency(cascade),
            target_zone=cascade.origin_zone,
            action_description=f"Open alternative exit from {cascade.origin_zone}",
            recommended_step=current_step,
            deadline_step=current_step + 7,
            expected_lives_saved=int(cascade.current_severity * 35),
            expected_density_reduction=1.8,
            success_probability=0.75,
            implementation_time=2,
            inconvenience_cost=0.3,
            resource_cost="Medium",
            reasoning=[
                "Provides alternative flow path",
                "Reduces pressure in bottleneck",
                "Less disruptive than closing entries"
            ],
            risks_if_ignored=[
                "Requires available alternative path",
                "May take longer to implement"
            ],
            prerequisites=["Alternative path must be available"]
        )
        
        # Alternative 2: Deploy crowd control staff
        alt2 = InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_alt2",
            intervention_type=InterventionType.DEPLOY_STAFF,
            urgency=InterventionUrgency.HIGH,
            target_zone=cascade.origin_zone,
            action_description=f"Deploy 5+ staff to {cascade.origin_zone} for crowd management",
            recommended_step=current_step,
            deadline_step=current_step + 3,
            expected_lives_saved=int(cascade.current_severity * 20),
            expected_density_reduction=1.0,
            success_probability=0.65,
            implementation_time=1,
            inconvenience_cost=0.2,
            resource_cost="High",
            reasoning=[
                "Staff can manage crowd flow",
                "Can redirect people manually",
                "Provides immediate human intervention"
            ],
            risks_if_ignored=[
                "Requires available trained staff",
                "Lower success rate than structural changes"
            ],
            prerequisites=["Trained staff available", "Communication system operational"]
        )
        
        plan = InterventionPlan(
            plan_id=f"plan_{self.intervention_counter}",
            primary_option=primary,
            alternative_options=[alt1, alt2],
            combined_impact={
                "max_lives_saved": primary.expected_lives_saved,
                "combined_success_probability": 0.95  # At least one works
            },
            confidence=0.82
        )
        
        self.intervention_counter += 1
        return plan
    
    def _recommend_for_panic(self, cascade: CascadeChain, 
                            current_step: int) -> InterventionPlan:
        """Recommend interventions for panic spread"""
        
        primary = InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_primary",
            intervention_type=InterventionType.COMMUNICATION_ANNOUNCEMENT,
            urgency=InterventionUrgency.IMMEDIATE,
            target_zone="all",
            action_description="Broadcast calming announcement to all zones",
            recommended_step=current_step,
            deadline_step=current_step + 2,
            expected_lives_saved=int(cascade.current_severity * 60),
            expected_density_reduction=0.8,
            success_probability=0.70,
            implementation_time=1,
            inconvenience_cost=0.1,
            resource_cost="Low",
            reasoning=[
                "Panic spreads through misinformation",
                "Clear communication can calm crowd",
                "Fast implementation"
            ],
            risks_if_ignored=[
                "Panic will spread to all connected zones",
                "People may trample in chaos",
                "Situation will escalate rapidly"
            ]
        )
        
        alt1 = InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_alt1",
            intervention_type=InterventionType.DEPLOY_STAFF,
            urgency=InterventionUrgency.IMMEDIATE,
            target_zone=cascade.origin_zone,
            action_description=f"Deploy all available staff to {cascade.origin_zone}",
            recommended_step=current_step,
            deadline_step=current_step + 1,
            expected_lives_saved=int(cascade.current_severity * 40),
            expected_density_reduction=1.2,
            success_probability=0.60,
            implementation_time=1,
            inconvenience_cost=0.3,
            resource_cost="High",
            reasoning=[
                "Physical presence calms panic",
                "Can physically guide crowd"
            ],
            risks_if_ignored=[
                "Staff may be overwhelmed by panic"
            ]
        )
        
        plan = InterventionPlan(
            plan_id=f"plan_{self.intervention_counter}",
            primary_option=primary,
            alternative_options=[alt1],
            combined_impact={
                "max_lives_saved": primary.expected_lives_saved,
                "panic_reduction": 0.7
            },
            confidence=0.75
        )
        
        self.intervention_counter += 1
        return plan
    
    def _recommend_for_overflow(self, cascade: CascadeChain,
                               current_step: int) -> InterventionPlan:
        """Recommend interventions for domino overflow"""
        
        primary = InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_primary",
            intervention_type=InterventionType.EMERGENCY_EVACUATION,
            urgency=InterventionUrgency.CRITICAL,
            target_zone=cascade.origin_zone,
            action_description=f"Activate emergency evacuation for {cascade.origin_zone}",
            recommended_step=current_step,
            deadline_step=current_step + 3,
            expected_lives_saved=int(cascade.current_severity * 80),
            expected_density_reduction=4.0,
            success_probability=0.90,
            implementation_time=2,
            inconvenience_cost=0.9,
            resource_cost="High",
            reasoning=[
                "Zone at critical capacity",
                "Immediate evacuation necessary",
                "High success rate"
            ],
            risks_if_ignored=[
                "Zone will overflow into adjacent areas",
                "Stampede highly likely",
                "Casualties expected"
            ]
        )
        
        plan = InterventionPlan(
            plan_id=f"plan_{self.intervention_counter}",
            primary_option=primary,
            alternative_options=[],
            combined_impact={
                "max_lives_saved": primary.expected_lives_saved
            },
            confidence=0.88
        )
        
        self.intervention_counter += 1
        return plan
    
    def _create_density_reduction_intervention(self, zone_id: str,
                                               current_step: int,
                                               prediction: StampedePrediction,
                                               urgency: InterventionUrgency) -> InterventionOption:
        """Create intervention to reduce density"""
        
        density_excess = prediction.predicted_peak_density - 5.0  # Target: below 5 p/m²
        
        return InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_primary",
            intervention_type=InterventionType.CLOSE_ENTRY,
            urgency=urgency,
            target_zone=zone_id,
            action_description=f"Close entries to {zone_id} immediately",
            recommended_step=current_step,
            deadline_step=current_step + max(prediction.time_to_stampede or 5, 1),
            expected_lives_saved=int(density_excess * self.LIVES_PER_DENSITY_UNIT),
            expected_density_reduction=density_excess,
            success_probability=0.85,
            implementation_time=1,
            inconvenience_cost=0.5,
            resource_cost="Low",
            reasoning=[
                f"Predicted peak density: {prediction.predicted_peak_density:.1f} p/m²",
                f"Current risk: {prediction.risk_level.value}",
                f"Probability: {prediction.probability:.0%}"
            ],
            risks_if_ignored=[
                f"Stampede predicted in {prediction.time_to_stampede} steps",
                f"Expected casualties: {int(density_excess * self.LIVES_PER_DENSITY_UNIT * 0.3)}"
            ]
        )
    
    def _generate_alternatives(self, zone_id: str, current_step: int,
                              prediction: StampedePrediction) -> List[InterventionOption]:
        """Generate alternative intervention options"""
        
        alternatives = []
        
        # Alternative 1: Reroute flow
        alt1 = InterventionOption(
            intervention_id=f"intv_{self.intervention_counter}_alt1",
            intervention_type=InterventionType.REROUTE_FLOW,
            urgency=InterventionUrgency.HIGH,
            target_zone=zone_id,
            action_description=f"Reroute crowd flow away from {zone_id}",
            recommended_step=current_step,
            deadline_step=current_step + 5,
            expected_lives_saved=int(prediction.probability * 30),
            expected_density_reduction=1.5,
            success_probability=0.70,
            implementation_time=2,
            inconvenience_cost=0.4,
            resource_cost="Medium",
            reasoning=[
                "Distributes crowd more evenly",
                "Prevents buildup in danger zone"
            ],
            risks_if_ignored=[
                "May create bottleneck in alternate route"
            ]
        )
        alternatives.append(alt1)
        
        return alternatives
    
    def _determine_urgency(self, cascade: CascadeChain) -> InterventionUrgency:
        """Determine urgency based on cascade state"""
        if cascade.state == CascadeState.RESULTED_IN_STAMPEDE:
            return InterventionUrgency.IMMEDIATE
        elif cascade.state == CascadeState.CRITICAL:
            return InterventionUrgency.CRITICAL
        elif cascade.state == CascadeState.PROPAGATING:
            return InterventionUrgency.HIGH
        else:
            return InterventionUrgency.MODERATE
    
    def _estimate_time_to_stampede(self, cascade: CascadeChain) -> int:
        """Estimate steps until stampede"""
        if cascade.current_severity >= 1.0:
            return 0
        elif cascade.current_severity >= 0.9:
            return 3
        elif cascade.current_severity >= 0.8:
            return 8
        else:
            return 15
    
    def format_intervention_plan(self, plan: InterventionPlan) -> str:
        """Format intervention plan for display"""
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"🎯 INTERVENTION PLAN: {plan.plan_id}")
        output.append(f"{'='*70}\n")
        
        # Primary option
        opt = plan.primary_option
        output.append(f"PRIMARY RECOMMENDATION:")
        output.append(f"  🚨 Urgency: {opt.urgency.value.upper()}")
        output.append(f"  📍 Action: {opt.action_description}")
        output.append(f"  ⏰ Recommended: Step {opt.recommended_step} | Deadline: Step {opt.deadline_step}")
        output.append(f"\n  📊 EXPECTED IMPACT:")
        output.append(f"     Lives saved: {opt.expected_lives_saved}")
        output.append(f"     Density reduction: {opt.expected_density_reduction:.1f} p/m²")
        output.append(f"     Success probability: {opt.success_probability:.0%}")
        output.append(f"\n  💰 COSTS:")
        output.append(f"     Implementation time: {opt.implementation_time} steps")
        output.append(f"     Inconvenience: {opt.inconvenience_cost:.0%}")
        output.append(f"     Resources: {opt.resource_cost}")
        output.append(f"\n  🔍 REASONING:")
        for reason in opt.reasoning:
            output.append(f"     • {reason}")
        output.append(f"\n  ⚠️  RISKS IF IGNORED:")
        for risk in opt.risks_if_ignored:
            output.append(f"     • {risk}")
        
        # Alternatives
        if plan.alternative_options:
            output.append(f"\n  🔄 ALTERNATIVE OPTIONS:")
            for i, alt in enumerate(plan.alternative_options, 1):
                output.append(f"\n     Option {i}: {alt.action_description}")
                output.append(f"     Expected lives saved: {alt.expected_lives_saved}")
                output.append(f"     Success rate: {alt.success_probability:.0%}")
                output.append(f"     Cost: {alt.resource_cost}")
        
        output.append(f"\n  ✅ Plan Confidence: {plan.confidence:.0%}")
        output.append(f"{'='*70}\n")
        
        return "\n".join(output)

# Example usage
if __name__ == "__main__":
    print("🧪 Testing Intervention Engine\n")
    
    # Import mock objects
    from stampede_predictor import StampedePrediction, RiskLevel
    from events.cascade_effects import CascadeChain, CascadeType, CascadeState
    
    engine = InterventionEngine()
    
    # Test 1: Recommendation for stampede prediction
    print("TEST 1: Stampede Prediction Intervention")
    print("=" * 70)
    
    prediction = StampedePrediction(
        zone_id="corridor_s",
        risk_level=RiskLevel.CRITICAL,
        probability=0.88,
        time_to_stampede=6,
        confidence=0.85,
        contributing_factors=["High density", "Stopped flow"],
        recommendations=["Close entries"],
        current_density=7.2,
        predicted_peak_density=9.5
    )
    
    plan = engine.recommend_for_prediction(prediction, current_step=100)
    if plan:
        print(engine.format_intervention_plan(plan))
    
    # Test 2: Recommendation for cascade
    print("\nTEST 2: Cascade Intervention")
    print("=" * 70)
    
    cascade = CascadeChain(
        chain_id="cascade_test",
        cascade_type=CascadeType.BOTTLENECK_BACKUP,
        state=CascadeState.CRITICAL,
        initiated_at=95,
        origin_zone="entry_gate",
        affected_zones=["entry_gate", "corridor_main"],
        current_severity=0.85
    )
    
    plan2 = engine.recommend_for_cascade(cascade, current_step=105)
    if plan2:
        print(engine.format_intervention_plan(plan2))
    
    print("✅ Intervention Engine Test Complete")
