# backend/events/event_types.py

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

class EventType(Enum):
    """Different event types with unique crowd dynamics"""
    POLITICAL_RALLY = "political_rally"
    CONCERT = "concert"
    RELIGIOUS_GATHERING = "religious_gathering"
    SPORTS_MATCH = "sports_match"
    TRANSPORT_HUB = "transport_hub"  # Bonus: railway stations

@dataclass
class CrowdProfile:
    """Defines crowd behavior characteristics"""
    event_type: EventType
    
    # Movement characteristics
    avg_speed: float  # m/s
    speed_variance: float  # How unpredictable
    
    # Density tolerance
    max_comfortable_density: float  # p/m²
    panic_threshold: float  # p/m² when panic starts
    
    # Wait behavior
    max_wait_time: int  # seconds before frustration
    patience_factor: float  # 0-1, higher = more patient
    
    # Risk factors
    rush_tendency: float  # 0-1, tendency to rush
    alcohol_factor: float  # 0-1, impairment level
    elderly_percentage: float  # 0-1
    
    # Event-specific
    vip_dependent: bool  # Does VIP timing affect crowd?
    predictability: float  # 0-1, how predictable the crowd is

# Define profiles for each event type
EVENT_PROFILES: Dict[EventType, CrowdProfile] = {
    EventType.POLITICAL_RALLY: CrowdProfile(
        event_type=EventType.POLITICAL_RALLY,
        avg_speed=0.8,
        speed_variance=0.4,  # Very unpredictable
        max_comfortable_density=3.5,
        panic_threshold=6.0,
        max_wait_time=7200,  # 2 hours (waiting for leader)
        patience_factor=0.6,
        rush_tendency=0.7,  # High rush when leader arrives
        alcohol_factor=0.1,
        elderly_percentage=0.3,
        vip_dependent=True,  # CRITICAL: VIP delays affect everything
        predictability=0.3  # Very unpredictable
    ),
    
    EventType.CONCERT: CrowdProfile(
        event_type=EventType.CONCERT,
        avg_speed=1.2,  # Fast-moving young crowd
        speed_variance=0.3,
        max_comfortable_density=4.0,  # Tolerate higher density
        panic_threshold=7.0,
        max_wait_time=1800,  # 30 min
        patience_factor=0.4,  # Impatient
        rush_tendency=0.9,  # VERY high rush tendency
        alcohol_factor=0.4,  # Significant alcohol influence
        elderly_percentage=0.05,
        vip_dependent=False,
        predictability=0.6
    ),
    
    EventType.RELIGIOUS_GATHERING: CrowdProfile(
        event_type=EventType.RELIGIOUS_GATHERING,
        avg_speed=0.5,  # Slow-moving elderly crowd
        speed_variance=0.2,
        max_comfortable_density=5.0,  # High tolerance (spiritual devotion)
        panic_threshold=6.5,
        max_wait_time=10800,  # 3 hours (high patience)
        patience_factor=0.9,  # Very patient
        rush_tendency=0.4,
        alcohol_factor=0.0,
        elderly_percentage=0.5,  # 50% elderly
        vip_dependent=False,
        predictability=0.7  # More predictable
    ),
    
    EventType.SPORTS_MATCH: CrowdProfile(
        event_type=EventType.SPORTS_MATCH,
        avg_speed=1.0,
        speed_variance=0.2,
        max_comfortable_density=3.0,
        panic_threshold=5.5,
        max_wait_time=1200,  # 20 min
        patience_factor=0.5,
        rush_tendency=0.5,
        alcohol_factor=0.3,
        elderly_percentage=0.2,
        vip_dependent=False,
        predictability=0.8  # Controlled environment
    ),
    
    EventType.TRANSPORT_HUB: CrowdProfile(
        event_type=EventType.TRANSPORT_HUB,
        avg_speed=1.1,
        speed_variance=0.3,
        max_comfortable_density=2.5,  # Low tolerance (time pressure)
        panic_threshold=5.0,
        max_wait_time=600,  # 10 min (missing train anxiety)
        patience_factor=0.3,  # Very impatient
        rush_tendency=0.8,
        alcohol_factor=0.1,
        elderly_percentage=0.3,
        vip_dependent=False,
        predictability=0.5
    )
}

def get_event_profile(event_type: EventType) -> CrowdProfile:
    """Get crowd profile for specific event type"""
    return EVENT_PROFILES[event_type]

def calculate_risk_score(event_type: EventType, crowd_size: int) -> float:
    """
    Calculate overall risk score (0-10) for an event
    Higher = more dangerous
    """
    profile = get_event_profile(event_type)
    
    # Base risk from crowd characteristics
    behavior_risk = (
        profile.rush_tendency * 3 +
        (1 - profile.predictability) * 2 +
        profile.alcohol_factor * 2 +
        (1 - profile.patience_factor) * 1
    )
    
    # Size multiplier (more people = exponentially more risk)
    if crowd_size < 5000:
        size_multiplier = 0.5
    elif crowd_size < 20000:
        size_multiplier = 1.0
    elif crowd_size < 50000:
        size_multiplier = 1.5
    else:
        size_multiplier = 2.0
    
    # VIP dependency adds uncertainty
    vip_risk = 1.5 if profile.vip_dependent else 1.0
    
    risk_score = behavior_risk * size_multiplier * vip_risk
    
    return min(risk_score, 10.0)  # Cap at 10

# Example usage
if __name__ == "__main__":
    # Test different event types
    for event_type in EventType:
        profile = get_event_profile(event_type)
        risk = calculate_risk_score(event_type, crowd_size=30000)
        
        print(f"\n{event_type.value.upper()}")
        print(f"  Risk Score: {risk:.1f}/10")
        print(f"  Avg Speed: {profile.avg_speed} m/s")
        print(f"  Panic Threshold: {profile.panic_threshold} p/m²")
        print(f"  VIP Dependent: {profile.vip_dependent}")
