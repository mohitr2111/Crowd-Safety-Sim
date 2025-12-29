# backend/events/cascade_effects.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import time

class CascadeState(Enum):
    """State of a cascade effect"""
    INITIATED = "initiated"
    PROPAGATING = "propagating"
    CRITICAL = "critical"
    RESOLVED = "resolved"
    RESULTED_IN_STAMPEDE = "stampede"

class CascadeType(Enum):
    """Types of cascade patterns"""
    BOTTLENECK_BACKUP = "bottleneck_backup"  # Jam → backup
    PANIC_SPREAD = "panic_spread"  # Panic spreads zone to zone
    FLOW_DIVERSION = "flow_diversion"  # Blocked path → alternate overloads
    DOMINO_OVERFLOW = "domino_overflow"  # Zone fills → adjacent fills
    PRESSURE_BUILD = "pressure_build"  # Static crowd → pressure increases

@dataclass
class CascadeEvent:
    """Single event in a cascade chain"""
    event_id: str
    zone_id: str
    timestamp: int  # Simulation step
    event_type: str  # "density_increase", "flow_blocked", etc.
    severity: float  # 0-1
    density: float
    description: str
    caused_by: Optional[str] = None  # ID of event that caused this

@dataclass
class CascadeChain:
    """Complete cascade chain from start to end"""
    chain_id: str
    cascade_type: CascadeType
    state: CascadeState
    initiated_at: int  # Step when started
    origin_zone: str
    affected_zones: List[str] = field(default_factory=list)
    events: List[CascadeEvent] = field(default_factory=list)
    current_severity: float = 0.0
    predicted_stampede_step: Optional[int] = None
    intervention_windows: List[Tuple[int, str]] = field(default_factory=list)

class CascadeEngine:
    """
    Tracks and predicts cascade effects in crowd dynamics
    """
    
    def __init__(self, zone_connections: Dict[str, List[str]]):
        """
        Args:
            zone_connections: Graph of which zones are connected
                Example: {"zone_a": ["zone_b", "zone_c"]}
        """
        self.zone_connections = zone_connections
        self.active_cascades: List[CascadeChain] = []
        self.cascade_history: List[CascadeChain] = []
        self.current_step = 0
        self.cascade_counter = 0
    
    def update(self, current_step: int, zone_data: Dict[str, Dict]) -> List[CascadeChain]:
        """
        Update cascade tracking with new zone data
        
        Args:
            zone_data: {
                "zone_a": {
                    "density": 5.2,
                    "flow_rate": 0.5,
                    "speed": 0.8,
                    "agent_count": 250
                },
                ...
            }
        
        Returns:
            List of active cascade chains
        """
        self.current_step = current_step
        
        # Check for new cascades
        new_cascades = self._detect_new_cascades(zone_data)
        for cascade in new_cascades:
            self.active_cascades.append(cascade)
            print(f"🔗 NEW CASCADE: {cascade.cascade_type.value} in {cascade.origin_zone}")
        
        # Update existing cascades
        for cascade in self.active_cascades[:]:  # Copy list to allow removal
            self._update_cascade(cascade, zone_data)
            
            # Remove resolved cascades
            if cascade.state in [CascadeState.RESOLVED, CascadeState.RESULTED_IN_STAMPEDE]:
                self.active_cascades.remove(cascade)
                self.cascade_history.append(cascade)
        
        return self.active_cascades
    
    def _detect_new_cascades(self, zone_data: Dict[str, Dict]) -> List[CascadeChain]:
        """Detect new cascade initiations"""
        new_cascades = []
        
        for zone_id, data in zone_data.items():
            density = data.get('density', 0)
            flow_rate = data.get('flow_rate', 0)
            speed = data.get('speed', 1.0)
            
            # BOTTLENECK BACKUP: High density + stopped flow
            if density > 5.0 and abs(flow_rate) < 0.1:
                # Check if not already in an active cascade
                if not self._zone_in_active_cascade(zone_id):
                    cascade = self._create_bottleneck_cascade(zone_id, data)
                    new_cascades.append(cascade)
            
            # PANIC SPREAD: High density + high speed (rushing)
            elif density > 4.5 and speed > 1.5:
                if not self._zone_in_active_cascade(zone_id):
                    cascade = self._create_panic_spread_cascade(zone_id, data)
                    new_cascades.append(cascade)
            
            # DOMINO OVERFLOW: Zone at/near capacity
            elif density > 6.5:
                if not self._zone_in_active_cascade(zone_id):
                    cascade = self._create_domino_cascade(zone_id, data)
                    new_cascades.append(cascade)
        
        return new_cascades
    
    def _create_bottleneck_cascade(self, zone_id: str, data: Dict) -> CascadeChain:
        """Create bottleneck backup cascade"""
        self.cascade_counter += 1
        
        initial_event = CascadeEvent(
            event_id=f"evt_{self.cascade_counter}_1",
            zone_id=zone_id,
            timestamp=self.current_step,
            event_type="flow_blocked",
            severity=min(data['density'] / 7.0, 1.0),
            density=data['density'],
            description=f"Flow blocked in {zone_id} (density {data['density']:.1f} p/m²)"
        )
        
        cascade = CascadeChain(
            chain_id=f"cascade_{self.cascade_counter}",
            cascade_type=CascadeType.BOTTLENECK_BACKUP,
            state=CascadeState.INITIATED,
            initiated_at=self.current_step,
            origin_zone=zone_id,
            affected_zones=[zone_id],
            events=[initial_event],
            current_severity=initial_event.severity
        )
        
        # Calculate intervention windows
        cascade.intervention_windows = [
            (self.current_step + 5, "Open alternative route"),
            (self.current_step + 10, "Stop upstream flow"),
            (self.current_step + 15, "Emergency intervention required")
        ]
        
        return cascade
    
    def _create_panic_spread_cascade(self, zone_id: str, data: Dict) -> CascadeChain:
        """Create panic spread cascade"""
        self.cascade_counter += 1
        
        initial_event = CascadeEvent(
            event_id=f"evt_{self.cascade_counter}_1",
            zone_id=zone_id,
            timestamp=self.current_step,
            event_type="panic_initiated",
            severity=0.7,
            density=data['density'],
            description=f"Panic behavior detected in {zone_id}"
        )
        
        cascade = CascadeChain(
            chain_id=f"cascade_{self.cascade_counter}",
            cascade_type=CascadeType.PANIC_SPREAD,
            state=CascadeState.INITIATED,
            initiated_at=self.current_step,
            origin_zone=zone_id,
            affected_zones=[zone_id],
            events=[initial_event],
            current_severity=0.7
        )
        
        cascade.intervention_windows = [
            (self.current_step + 3, "Deploy staff to calm crowd"),
            (self.current_step + 7, "Activate communication system"),
            (self.current_step + 12, "Emergency evacuation")
        ]
        
        return cascade
    
    def _create_domino_cascade(self, zone_id: str, data: Dict) -> CascadeChain:
        """Create domino overflow cascade"""
        self.cascade_counter += 1
        
        initial_event = CascadeEvent(
            event_id=f"evt_{self.cascade_counter}_1",
            zone_id=zone_id,
            timestamp=self.current_step,
            event_type="zone_overflow",
            severity=min(data['density'] / 8.0, 1.0),
            density=data['density'],
            description=f"Zone {zone_id} overflowing (density {data['density']:.1f} p/m²)"
        )
        
        cascade = CascadeChain(
            chain_id=f"cascade_{self.cascade_counter}",
            cascade_type=CascadeType.DOMINO_OVERFLOW,
            state=CascadeState.INITIATED,
            initiated_at=self.current_step,
            origin_zone=zone_id,
            affected_zones=[zone_id],
            events=[initial_event],
            current_severity=initial_event.severity
        )
        
        cascade.intervention_windows = [
            (self.current_step + 4, "Close entry to this zone"),
            (self.current_step + 8, "Open emergency exits"),
            (self.current_step + 12, "Critical - immediate action")
        ]
        
        return cascade
    
    def _update_cascade(self, cascade: CascadeChain, zone_data: Dict[str, Dict]):
        """Update existing cascade with new data"""
        
        # Check if cascade has propagated to connected zones
        for zone_id in cascade.affected_zones[:]:  # Copy to allow modification
            if zone_id in self.zone_connections:
                for connected_zone in self.zone_connections[zone_id]:
                    if connected_zone not in cascade.affected_zones:
                        # Check if connected zone is affected
                        if connected_zone in zone_data:
                            data = zone_data[connected_zone]
                            
                            # Propagation conditions
                            if (cascade.cascade_type == CascadeType.BOTTLENECK_BACKUP and 
                                data['density'] > 4.5):
                                self._propagate_cascade(cascade, connected_zone, data)
                            
                            elif (cascade.cascade_type == CascadeType.PANIC_SPREAD and 
                                  data['speed'] > 1.5):
                                self._propagate_cascade(cascade, connected_zone, data)
                            
                            elif (cascade.cascade_type == CascadeType.DOMINO_OVERFLOW and 
                                  data['density'] > 5.5):
                                self._propagate_cascade(cascade, connected_zone, data)
        
        # Update cascade state
        max_density = max(
            zone_data[z]['density'] for z in cascade.affected_zones 
            if z in zone_data
        )
        
        cascade.current_severity = min(max_density / 8.0, 1.0)
        
        # Check for stampede conditions
        if max_density > 8.5:
            cascade.state = CascadeState.RESULTED_IN_STAMPEDE
            cascade.predicted_stampede_step = self.current_step
            print(f"⚠️  CASCADE {cascade.chain_id} RESULTED IN STAMPEDE at step {self.current_step}")
        
        elif cascade.current_severity > 0.8:
            cascade.state = CascadeState.CRITICAL
        
        elif len(cascade.affected_zones) > 1:
            cascade.state = CascadeState.PROPAGATING
        
        # Check if resolved (density decreased)
        if max_density < 3.0 and cascade.state != CascadeState.RESULTED_IN_STAMPEDE:
            cascade.state = CascadeState.RESOLVED
            print(f"✅ CASCADE {cascade.chain_id} RESOLVED at step {self.current_step}")
    
    def _propagate_cascade(self, cascade: CascadeChain, new_zone: str, data: Dict):
        """Propagate cascade to new zone"""
        cascade.affected_zones.append(new_zone)
        
        event = CascadeEvent(
            event_id=f"{cascade.chain_id}_evt_{len(cascade.events)+1}",
            zone_id=new_zone,
            timestamp=self.current_step,
            event_type="cascade_propagation",
            severity=min(data['density'] / 7.0, 1.0),
            density=data['density'],
            description=f"Cascade spread to {new_zone}",
            caused_by=cascade.events[-1].event_id
        )
        
        cascade.events.append(event)
        print(f"🔗 CASCADE PROPAGATED: {cascade.origin_zone} → {new_zone}")
    
    def _zone_in_active_cascade(self, zone_id: str) -> bool:
        """Check if zone already in an active cascade"""
        for cascade in self.active_cascades:
            if zone_id in cascade.affected_zones:
                return True
        return False
    
    def get_critical_cascades(self) -> List[CascadeChain]:
        """Get all critical/stampede cascades"""
        return [
            c for c in self.active_cascades 
            if c.state in [CascadeState.CRITICAL, CascadeState.RESULTED_IN_STAMPEDE]
        ]
    
    def get_intervention_opportunities(self) -> List[Tuple[CascadeChain, int, str]]:
        """Get current intervention opportunities"""
        opportunities = []
        
        for cascade in self.active_cascades:
            for step, action in cascade.intervention_windows:
                if step >= self.current_step and step <= self.current_step + 5:
                    opportunities.append((cascade, step, action))
        
        return opportunities

# Example usage
if __name__ == "__main__":
    print("🧪 Testing Cascade Effects Engine\n")
    print("=" * 70)
    
    # Define venue layout (connections between zones)
    venue_layout = {
        "entry_gate": ["corridor_main"],
        "corridor_main": ["entry_gate", "zone_north", "zone_south"],
        "zone_north": ["corridor_main", "exit_a"],
        "zone_south": ["corridor_main", "exit_b"],
        "exit_a": ["zone_north"],
        "exit_b": ["zone_south"]
    }
    
    engine = CascadeEngine(venue_layout)
    
    print("📋 SCENARIO: Bottleneck cascade simulation\n")
    
    # Simulate 20 steps with increasing congestion
    for step in range(20):
        # Simulate zone data
        zone_data = {
            "entry_gate": {
                "density": 2.0 + step * 0.1,
                "flow_rate": 1.0 - step * 0.05,
                "speed": 1.0,
                "agent_count": 100
            },
            "corridor_main": {
                "density": 3.0 + step * 0.3,
                "flow_rate": 0.5 if step < 10 else 0.05,  # Flow stops at step 10
                "speed": 1.0 - step * 0.04,
                "agent_count": 150
            },
            "zone_north": {
                "density": 2.5 + step * 0.2,
                "flow_rate": 0.8,
                "speed": 0.9,
                "agent_count": 120
            }
        }
        
        # Update cascade engine
        active = engine.update(step, zone_data)
        
        # Report on key steps
        if step % 5 == 0 or len(active) > 0:
            print(f"\n⏱️  Step {step}:")
            print(f"   Active cascades: {len(active)}")
            
            for cascade in active:
                print(f"   └─ {cascade.chain_id}: {cascade.cascade_type.value}")
                print(f"      State: {cascade.state.value}")
                print(f"      Affected zones: {', '.join(cascade.affected_zones)}")
                print(f"      Severity: {cascade.current_severity:.2f}")
            
            # Check intervention opportunities
            opportunities = engine.get_intervention_opportunities()
            if opportunities:
                print(f"\n   💡 INTERVENTION OPPORTUNITIES:")
                for cascade, intervene_step, action in opportunities:
                    print(f"      Step {intervene_step}: {action}")
    
    print("\n" + "=" * 70)
    print("✅ Cascade Engine Test Complete")
