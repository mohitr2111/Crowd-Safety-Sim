# backend/events/event_triggers.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime, timedelta

class TriggerType(Enum):
    """Types of event triggers"""
    VIP_DELAYED = "vip_delayed"
    WEATHER_CHANGE = "weather_change"  
    EMERGENCY_EVACUATION = "emergency_evacuation"
    GATE_MALFUNCTION = "gate_malfunction"
    SECURITY_THREAT = "security_threat"
    POWER_OUTAGE = "power_outage"
    OVERCROWDING_ALERT = "overcrowding_alert"
    FIRE_OUTBREAK = "fire_outbreak"
    EXPLOSION = "explosion"
    STRUCTURAL_COLLAPSE = "structural_collapse"
    BOMB_THREAT = "bomb_threat"
    MEDICAL_EMERGENCY = "medical_emergency"  
    RUMOR_SPREAD = "rumor_spread"  


class WeatherType(Enum):
    RAIN = "rain"
    STORM = "storm"
    HEAT_WAVE = "heat_wave"
    FOG = "fog"

@dataclass
class EventTrigger:
    """Represents a time-based event trigger"""
    trigger_type: TriggerType
    trigger_time: int  # Simulation step when trigger activates
    duration: int  # How long the effect lasts (steps)
    severity: float  # 0-1, how severe the trigger is
    affected_areas: List[str]  # Which zones are affected
    description: str
    
    # Specific parameters for different triggers
    delay_hours: Optional[float] = None  # For VIP_DELAYED
    weather_type: Optional[WeatherType] = None  # For WEATHER_CHANGE
    gate_id: Optional[str] = None  # For GATE_MALFUNCTION

@dataclass
class TriggerEffect:
    """Effects of a trigger on crowd behavior"""
    speed_multiplier: float = 1.0  # Multiplier for agent speed
    panic_level: float = 0.0  # 0-1, added panic
    density_tolerance: float = 1.0  # Multiplier for density threshold
    exit_urgency: float = 0.0  # 0-1, urgency to leave
    entry_rate_change: float = 1.0  # Multiplier for new agents spawning

class TriggerEngine:
    """Manages and applies event triggers during simulation"""
    
    def __init__(self):
        self.active_triggers: List[EventTrigger] = []
        self.trigger_history: List[EventTrigger] = []
        self.current_step = 0
    
    def add_trigger(self, trigger: EventTrigger):
        """Add a trigger to the simulation"""
        self.active_triggers.append(trigger)
        print(f"⚠️  Trigger scheduled: {trigger.description} at step {trigger.trigger_time}")
    
    def update(self, current_step: int) -> List[EventTrigger]:
        """Check and activate triggers for current step"""
        self.current_step = current_step
        activated = []
        
        for trigger in self.active_triggers:
            # Check if trigger should activate
            if trigger.trigger_time == current_step:
                activated.append(trigger)
                self.trigger_history.append(trigger)
                print(f"🔥 TRIGGER ACTIVATED: {trigger.description}")
            
            # Remove expired triggers
            elif current_step > trigger.trigger_time + trigger.duration:
                if trigger in self.active_triggers:
                    self.active_triggers.remove(trigger)
                    print(f"✅ Trigger ended: {trigger.description}")
        
        return activated
    
    def get_cumulative_effect(self, current_step: int, area: str) -> TriggerEffect:
        """
        Calculate cumulative effect of all active triggers on a specific area
        """
        effect = TriggerEffect()
        
        for trigger in self.active_triggers:
            # Check if trigger is currently active
            if (trigger.trigger_time <= current_step < 
                trigger.trigger_time + trigger.duration):
                
                # Check if this area is affected
                if area in trigger.affected_areas or "all" in trigger.affected_areas:
                    trigger_effect = self._calculate_trigger_effect(trigger)
                    effect = self._merge_effects(effect, trigger_effect)
        
        return effect
    
    def _calculate_trigger_effect(self, trigger: EventTrigger) -> TriggerEffect:
            """Calculate effect based on trigger type"""
            
            if trigger.trigger_type == TriggerType.VIP_DELAYED:
                return TriggerEffect(
                    speed_multiplier=1.0 + (trigger.severity * 0.3),
                    panic_level=trigger.severity * 0.4,
                    density_tolerance=0.8,
                    exit_urgency=0.0,
                    entry_rate_change=1.5
                )
            
            # 🆕 FIRE OUTBREAK (Most dangerous)
            elif trigger.trigger_type == TriggerType.FIRE_OUTBREAK:
                return TriggerEffect(
                    speed_multiplier=3.0,  # EXTREME panic rush
                    panic_level=1.0,  # MAXIMUM panic
                    density_tolerance=0.3,  # Crush risk
                    exit_urgency=1.0,  # Everyone fleeing
                    entry_rate_change=0.0  # No one entering
                )
            
            # 🆕 EXPLOSION (Instant panic)
            elif trigger.trigger_type == TriggerType.EXPLOSION:
                return TriggerEffect(
                    speed_multiplier=3.5,  # Faster than fire (sudden shock)
                    panic_level=1.0,
                    density_tolerance=0.2,  # People trampling
                    exit_urgency=1.0,
                    entry_rate_change=0.0
                )
            
            # 🆕 STRUCTURAL COLLAPSE (Ceiling/stage falls)
            elif trigger.trigger_type == TriggerType.STRUCTURAL_COLLAPSE:
                return TriggerEffect(
                    speed_multiplier=2.8,
                    panic_level=0.95,
                    density_tolerance=0.3,
                    exit_urgency=1.0,
                    entry_rate_change=0.0
                )
            
            # 🆕 BOMB THREAT (Directed panic)
            elif trigger.trigger_type == TriggerType.BOMB_THREAT:
                return TriggerEffect(
                    speed_multiplier=2.5,
                    panic_level=0.9,
                    density_tolerance=0.4,
                    exit_urgency=1.0,
                    entry_rate_change=0.0
                )
            
            # 🆕 MEDICAL EMERGENCY (Someone falls, crowd panics)
            elif trigger.trigger_type == TriggerType.MEDICAL_EMERGENCY:
                return TriggerEffect(
                    speed_multiplier=1.8,
                    panic_level=0.6,
                    density_tolerance=0.6,
                    exit_urgency=0.4,
                    entry_rate_change=0.5
                )
            
            # 🆕 RUMOR SPREAD (False alarm, but causes panic)
            elif trigger.trigger_type == TriggerType.RUMOR_SPREAD:
                return TriggerEffect(
                    speed_multiplier=2.0,
                    panic_level=0.7,
                    density_tolerance=0.5,
                    exit_urgency=0.7,
                    entry_rate_change=0.2
                )
            
            # Keep weather for outdoor events
            elif trigger.trigger_type == TriggerType.WEATHER_CHANGE:
                if trigger.weather_type == WeatherType.RAIN:
                    return TriggerEffect(
                        speed_multiplier=1.5,
                        panic_level=0.3,
                        density_tolerance=0.7,
                        exit_urgency=0.8,
                        entry_rate_change=0.2
                    )
                elif trigger.weather_type == WeatherType.STORM:
                    return TriggerEffect(
                        speed_multiplier=2.0,
                        panic_level=0.7,
                        density_tolerance=0.5,
                        exit_urgency=1.0,
                        entry_rate_change=0.0
                    )
            
            elif trigger.trigger_type == TriggerType.EMERGENCY_EVACUATION:
                return TriggerEffect(
                    speed_multiplier=2.5,  # Panic sprint
                    panic_level=0.9,
                    density_tolerance=0.4,
                    exit_urgency=1.0,
                    entry_rate_change=0.0
                )
            
            elif trigger.trigger_type == TriggerType.GATE_MALFUNCTION:
                return TriggerEffect(
                    speed_multiplier=0.7,  # Slowed entry
                    panic_level=0.2,
                    density_tolerance=0.9,
                    exit_urgency=0.0,
                    entry_rate_change=0.3  # Reduced entry rate
                )
            
            elif trigger.trigger_type == TriggerType.SECURITY_THREAT:
                return TriggerEffect(
                    speed_multiplier=1.8,
                    panic_level=0.8,
                    density_tolerance=0.5,
                    exit_urgency=0.9,
                    entry_rate_change=0.0
                )
            
            elif trigger.trigger_type == TriggerType.POWER_OUTAGE:
                return TriggerEffect(
                    speed_multiplier=0.6,  # Slower in dark
                    panic_level=0.5,
                    density_tolerance=0.6,
                    exit_urgency=0.6,
                    entry_rate_change=0.1
                )
            
            return TriggerEffect()
    
    def _merge_effects(self, base: TriggerEffect, new: TriggerEffect) -> TriggerEffect:
        """Merge multiple trigger effects (cumulative)"""
        return TriggerEffect(
            speed_multiplier=base.speed_multiplier * new.speed_multiplier,
            panic_level=min(base.panic_level + new.panic_level, 1.0),
            density_tolerance=base.density_tolerance * new.density_tolerance,
            exit_urgency=max(base.exit_urgency, new.exit_urgency),
            entry_rate_change=base.entry_rate_change * new.entry_rate_change
        )
    
    def get_active_triggers(self) -> List[EventTrigger]:
        """Get currently active triggers"""
        active = []
        for trigger in self.active_triggers:
            if (trigger.trigger_time <= self.current_step < 
                trigger.trigger_time + trigger.duration):
                active.append(trigger)
        return active

# Predefined trigger scenarios
def create_vip_delay_scenario(delay_hours: float, start_step: int = 100) -> EventTrigger:
    """
    Create VIP delay trigger (e.g., politician running late)
    """
    return EventTrigger(
        trigger_type=TriggerType.VIP_DELAYED,
        trigger_time=start_step,
        duration=int(delay_hours * 3600 / 30),  # Convert hours to steps (30s/step)
        severity=min(delay_hours / 3.0, 1.0),  # 3+ hours = max severity
        affected_areas=["all"],
        description=f"VIP delayed by {delay_hours} hours",
        delay_hours=delay_hours
    )

def create_rain_scenario(start_step: int = 200, duration_minutes: int = 30) -> EventTrigger:
    """
    Create sudden rain trigger
    """
    return EventTrigger(
        trigger_type=TriggerType.WEATHER_CHANGE,
        trigger_time=start_step,
        duration=int(duration_minutes * 60 / 30),  # Convert to steps
        severity=0.7,
        affected_areas=["all"],
        description=f"Heavy rain starts (lasts {duration_minutes} min)",
        weather_type=WeatherType.RAIN
    )

def create_emergency_evacuation(start_step: int) -> EventTrigger:
    """
    Create emergency evacuation trigger
    """
    return EventTrigger(
        trigger_type=TriggerType.EMERGENCY_EVACUATION,
        trigger_time=start_step,
        duration=1000,  # Long duration
        severity=1.0,
        affected_areas=["all"],
        description="Emergency evacuation ordered"
    )

def create_gate_malfunction(gate_id: str, start_step: int, duration_minutes: int = 20) -> EventTrigger:
    """
    Create gate malfunction trigger
    """
    return EventTrigger(
        trigger_type=TriggerType.GATE_MALFUNCTION,
        trigger_time=start_step,
        duration=int(duration_minutes * 60 / 30),
        severity=0.8,
        affected_areas=[gate_id, "entry_points"],
        description=f"Gate {gate_id} malfunction ({duration_minutes} min)",
        gate_id=gate_id
    )
def create_fire_outbreak(location: str, start_step: int, severity: float = 0.9) -> EventTrigger:
    """
    Create fire outbreak trigger
    Args:
        location: Where fire starts (e.g., "stage", "kitchen", "corridor_n")
        start_step: When fire detected
        severity: 0-1, size of fire
    """
    return EventTrigger(
        trigger_type=TriggerType.FIRE_OUTBREAK,
        trigger_time=start_step,
        duration=1000,  # Until evacuation complete
        severity=severity,
        affected_areas=["all"],  # Fire affects everyone
        description=f"Fire outbreak at {location}"
    )

def create_explosion(location: str, start_step: int, casualties: int = 0) -> EventTrigger:
    """
    Create explosion trigger (bomb, gas leak, etc.)
    """
    severity = min(casualties / 50.0, 1.0)  # More casualties = higher severity
    return EventTrigger(
        trigger_type=TriggerType.EXPLOSION,
        trigger_time=start_step,
        duration=1000,
        severity=max(severity, 0.8),  # At least 0.8 for any explosion
        affected_areas=["all"],
        description=f"Explosion at {location}"
    )

def create_structural_collapse(location: str, start_step: int) -> EventTrigger:
    """
    Create structural collapse trigger (ceiling, stage, barrier falls)
    """
    return EventTrigger(
        trigger_type=TriggerType.STRUCTURAL_COLLAPSE,
        trigger_time=start_step,
        duration=1000,
        severity=0.95,
        affected_areas=["all"],
        description=f"Structural collapse at {location}"
    )

def create_bomb_threat(start_step: int, credibility: float = 0.7) -> EventTrigger:
    """
    Create bomb threat trigger
    Args:
        credibility: 0-1, how believable the threat is
    """
    return EventTrigger(
        trigger_type=TriggerType.BOMB_THREAT,
        trigger_time=start_step,
        duration=500,
        severity=credibility,
        affected_areas=["all"],
        description="Bomb threat received"
    )

def create_medical_emergency(location: str, start_step: int) -> EventTrigger:
    """
    Create medical emergency (someone collapses, crowd panics)
    """
    return EventTrigger(
        trigger_type=TriggerType.MEDICAL_EMERGENCY,
        trigger_time=start_step,
        duration=100,  # Short duration
        severity=0.6,
        affected_areas=[location, "adjacent"],
        description=f"Medical emergency at {location}"
    )

def create_rumor_panic(rumor: str, start_step: int, spread_rate: float = 0.7) -> EventTrigger:
    """
    Create rumor-based panic (false alarm spreads through crowd)
    """
    return EventTrigger(
        trigger_type=TriggerType.RUMOR_SPREAD,
        trigger_time=start_step,
        duration=200,  # Spreads then calms
        severity=spread_rate,
        affected_areas=["all"],
        description=f"Rumor spreading: {rumor}"
    )


if __name__ == "__main__":
    print("🧪 Testing Event Trigger System\n")
    
    engine = TriggerEngine()
    
    # 🔥 NEW SCENARIO: Concert with fire outbreak
    print("📋 SCENARIO: Concert Fire Emergency")
    print("=" * 60)
    
    # Timeline of disaster
    vip_delay = create_vip_delay_scenario(delay_hours=1.0, start_step=50)
    fire = create_fire_outbreak(location="stage", start_step=200, severity=0.9)
    medical = create_medical_emergency(location="exit_a", start_step=220)
    
    engine.add_trigger(vip_delay)
    engine.add_trigger(fire)
    engine.add_trigger(medical)
    
    print("\n⏱️  Simulating timeline:\n")
    
    test_steps = [0, 50, 100, 200, 220, 250, 300]
    
    for step in test_steps:
        activated = engine.update(step)
        
        if activated:
            print(f"Step {step}: {len(activated)} trigger(s) activated")
        
        effect = engine.get_cumulative_effect(step, "main_area")
        
        if effect.panic_level > 0 or effect.speed_multiplier != 1.0:
            print(f"  📊 Step {step} Effects:")
            print(f"     Speed: {effect.speed_multiplier:.2f}x")
            print(f"     Panic: {effect.panic_level:.2f}")
            print(f"     Exit Urgency: {effect.exit_urgency:.2f}")
            print(f"     Entry Rate: {effect.entry_rate_change:.2f}x")
            
            # Risk assessment
            if effect.panic_level >= 0.9:
                print(f"     ⚠️  STATUS: EXTREME DANGER - STAMPEDE IMMINENT")
            elif effect.panic_level >= 0.7:
                print(f"     ⚠️  STATUS: HIGH DANGER - EVACUATION URGENT")
            elif effect.panic_level >= 0.5:
                print(f"     ⚠️  STATUS: MODERATE DANGER - MONITOR CLOSELY")
            print()
