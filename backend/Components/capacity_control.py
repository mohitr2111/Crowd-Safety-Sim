"""
PHASE 4: Capacity Control Module
Manages dynamic capacity adjustments for nodes and edges
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CapacityAdjustment(Enum):
    """Types of capacity adjustments"""
    EXPAND_AREA = "expand_area"  # Temporarily expand node area
    INCREASE_FLOW = "increase_flow"  # Increase edge flow capacity
    BLOCK_ZONE = "block_zone"  # Block zone entirely
    RESTORE = "restore"  # Restore to original capacity


@dataclass
class CapacityChange:
    """Record of a capacity adjustment"""
    node_id: str
    adjustment_type: str
    original_value: float
    adjusted_value: float
    applied_at: float  # Simulation time
    expires_at: Optional[float] = None  # When to restore (None = permanent)
    is_active: bool = True


@dataclass
class NodeCapacityState:
    """State of capacity adjustments for a node"""
    node_id: str
    original_area_m2: float
    current_area_m2: float
    original_capacity: int
    current_capacity: int
    is_blocked: bool = False
    blocked_until: Optional[float] = None
    adjustments: List[CapacityChange] = field(default_factory=list)
    max_expansion_factor: float = 1.5  # Maximum 50% expansion


@dataclass
class EdgeCapacityState:
    """State of capacity adjustments for an edge"""
    from_node: str
    to_node: str
    original_flow_capacity: int
    current_flow_capacity: int
    is_blocked: bool = False
    blocked_until: Optional[float] = None
    adjustments: List[CapacityChange] = field(default_factory=list)
    max_increase_factor: float = 2.0  # Maximum 100% increase


class CapacityController:
    """
    PHASE 4: Capacity Controller
    
    Manages dynamic capacity adjustments:
    - Temporarily expand node areas (if physically possible)
    - Increase edge flow capacity (add lanes/staff)
    - Block zones entirely
    """
    
    def __init__(self):
        """Initialize capacity controller"""
        self.node_states: Dict[str, NodeCapacityState] = {}
        self.edge_states: Dict[Tuple[str, str], EdgeCapacityState] = {}
    
    def register_node(
        self,
        node_id: str,
        area_m2: float,
        capacity: int,
        max_expansion_factor: float = 1.5
    ):
        """Register a node for capacity control"""
        if node_id not in self.node_states:
            self.node_states[node_id] = NodeCapacityState(
                node_id=node_id,
                original_area_m2=area_m2,
                current_area_m2=area_m2,
                original_capacity=capacity,
                current_capacity=capacity,
                max_expansion_factor=max_expansion_factor,
            )
        else:
            # Update if already exists
            state = self.node_states[node_id]
            state.original_area_m2 = area_m2
            state.original_capacity = capacity
            state.current_area_m2 = area_m2
            state.current_capacity = capacity
    
    def register_edge(
        self,
        from_node: str,
        to_node: str,
        flow_capacity: int,
        max_increase_factor: float = 2.0
    ):
        """Register an edge for capacity control"""
        edge_key = (from_node, to_node)
        if edge_key not in self.edge_states:
            self.edge_states[edge_key] = EdgeCapacityState(
                from_node=from_node,
                to_node=to_node,
                original_flow_capacity=flow_capacity,
                current_flow_capacity=flow_capacity,
                max_increase_factor=max_increase_factor,
            )
        else:
            # Update if already exists
            state = self.edge_states[edge_key]
            state.original_flow_capacity = flow_capacity
            state.current_flow_capacity = flow_capacity
    
    def expand_node_area(
        self,
        node_id: str,
        expansion_factor: float,
        duration: Optional[float] = None,
        current_time: float = 0.0
    ) -> bool:
        """
        Temporarily expand node area (if physically possible)
        
        Args:
            node_id: Node to expand
            expansion_factor: Multiplier (1.0 = no change, 1.5 = 50% larger)
            duration: How long to keep expansion (None = permanent)
            current_time: Current simulation time
        
        Returns:
            bool: True if expansion applied, False if not possible
        """
        if node_id not in self.node_states:
            return False
        
        state = self.node_states[node_id]
        
        # Limit expansion to maximum
        expansion_factor = min(expansion_factor, state.max_expansion_factor)
        
        if expansion_factor <= 1.0:
            return False  # No expansion needed
        
        # Calculate new area
        new_area = state.original_area_m2 * expansion_factor
        new_capacity = int(state.original_capacity * expansion_factor)
        
        # Apply expansion
        original_area = state.current_area_m2
        state.current_area_m2 = new_area
        state.current_capacity = new_capacity
        
        # Record change
        change = CapacityChange(
            node_id=node_id,
            adjustment_type=CapacityAdjustment.EXPAND_AREA.value,
            original_value=original_area,
            adjusted_value=new_area,
            applied_at=current_time,
            expires_at=current_time + duration if duration else None,
        )
        state.adjustments.append(change)
        
        return True
    
    def increase_edge_flow(
        self,
        from_node: str,
        to_node: str,
        increase_factor: float,
        duration: Optional[float] = None,
        current_time: float = 0.0
    ) -> bool:
        """
        Increase edge flow capacity (add lanes/staff)
        
        Args:
            from_node, to_node: Edge endpoints
            increase_factor: Multiplier (1.0 = no change, 2.0 = double capacity)
            duration: How long to keep increase (None = permanent)
            current_time: Current simulation time
        
        Returns:
            bool: True if increase applied
        """
        edge_key = (from_node, to_node)
        if edge_key not in self.edge_states:
            return False
        
        state = self.edge_states[edge_key]
        
        # Limit increase to maximum
        increase_factor = min(increase_factor, state.max_increase_factor)
        
        if increase_factor <= 1.0:
            return False  # No increase needed
        
        # Calculate new capacity
        new_capacity = int(state.original_flow_capacity * increase_factor)
        
        # Apply increase
        original_capacity = state.current_flow_capacity
        state.current_flow_capacity = new_capacity
        
        # Record change
        change = CapacityChange(
            node_id=f"{from_node}->{to_node}",
            adjustment_type=CapacityAdjustment.INCREASE_FLOW.value,
            original_value=float(original_capacity),
            adjusted_value=float(new_capacity),
            applied_at=current_time,
            expires_at=current_time + duration if duration else None,
        )
        state.adjustments.append(change)
        
        return True
    
    def block_zone(
        self,
        node_id: str,
        duration: Optional[float] = None,
        current_time: float = 0.0
    ) -> bool:
        """
        Block zone entirely (set capacity to 0)
        
        Args:
            node_id: Node to block
            duration: How long to keep block (None = permanent)
            current_time: Current simulation time
        
        Returns:
            bool: True if block applied
        """
        if node_id not in self.node_states:
            return False
        
        state = self.node_states[node_id]
        
        # Apply block
        state.is_blocked = True
        state.blocked_until = current_time + duration if duration else None
        state.current_capacity = 0
        
        # Record change
        change = CapacityChange(
            node_id=node_id,
            adjustment_type=CapacityAdjustment.BLOCK_ZONE.value,
            original_value=float(state.current_capacity),
            adjusted_value=0.0,
            applied_at=current_time,
            expires_at=state.blocked_until,
        )
        state.adjustments.append(change)
        
        return True
    
    def restore_node(self, node_id: str):
        """Restore node to original capacity"""
        if node_id not in self.node_states:
            return False
        
        state = self.node_states[node_id]
        state.current_area_m2 = state.original_area_m2
        state.current_capacity = state.original_capacity
        state.is_blocked = False
        state.blocked_until = None
        
        return True
    
    def restore_edge(self, from_node: str, to_node: str):
        """Restore edge to original capacity"""
        edge_key = (from_node, to_node)
        if edge_key not in self.edge_states:
            return False
        
        state = self.edge_states[edge_key]
        state.current_flow_capacity = state.original_flow_capacity
        state.is_blocked = False
        state.blocked_until = None
        
        return True
    
    def update_time(self, current_time: float):
        """Update controller time (check for expired adjustments)"""
        # Check node adjustments
        for state in self.node_states.values():
            # Check if block expired
            if state.blocked_until is not None and current_time >= state.blocked_until:
                self.restore_node(state.node_id)
            
            # Check other adjustments
            for adjustment in state.adjustments:
                if adjustment.expires_at and current_time >= adjustment.expires_at:
                    adjustment.is_active = False
                    # Auto-restore if it was the last active adjustment
                    active_adjustments = [a for a in state.adjustments if a.is_active]
                    if not active_adjustments:
                        self.restore_node(state.node_id)
        
        # Check edge adjustments
        for edge_key, state in self.edge_states.items():
            # Check if block expired
            if state.blocked_until is not None and current_time >= state.blocked_until:
                self.restore_edge(state.from_node, state.to_node)
            
            # Check other adjustments
            for adjustment in state.adjustments:
                if adjustment.expires_at and current_time >= adjustment.expires_at:
                    adjustment.is_active = False
                    # Auto-restore if it was the last active adjustment
                    active_adjustments = [a for a in state.adjustments if a.is_active]
                    if not active_adjustments:
                        self.restore_edge(state.from_node, state.to_node)
    
    def get_node_capacity(self, node_id: str) -> Optional[float]:
        """Get current area/capacity for a node"""
        if node_id not in self.node_states:
            return None
        return self.node_states[node_id].current_area_m2
    
    def get_edge_capacity(self, from_node: str, to_node: str) -> Optional[int]:
        """Get current flow capacity for an edge"""
        edge_key = (from_node, to_node)
        if edge_key not in self.edge_states:
            return None
        return self.edge_states[edge_key].current_flow_capacity
    
    def get_node_state(self, node_id: str) -> Optional[Dict]:
        """Get current state of capacity control for a node"""
        if node_id not in self.node_states:
            return None
        
        state = self.node_states[node_id]
        return {
            "node_id": state.node_id,
            "original_area_m2": state.original_area_m2,
            "current_area_m2": state.current_area_m2,
            "original_capacity": state.original_capacity,
            "current_capacity": state.current_capacity,
            "is_blocked": state.is_blocked,
            "blocked_until": state.blocked_until,
            "expansion_factor": state.current_area_m2 / state.original_area_m2 if state.original_area_m2 > 0 else 1.0,
        }
    
    def get_edge_state(self, from_node: str, to_node: str) -> Optional[Dict]:
        """Get current state of capacity control for an edge"""
        edge_key = (from_node, to_node)
        if edge_key not in self.edge_states:
            return None
        
        state = self.edge_states[edge_key]
        return {
            "from_node": state.from_node,
            "to_node": state.to_node,
            "original_flow_capacity": state.original_flow_capacity,
            "current_flow_capacity": state.current_flow_capacity,
            "is_blocked": state.is_blocked,
            "blocked_until": state.blocked_until,
            "increase_factor": state.current_flow_capacity / state.original_flow_capacity if state.original_flow_capacity > 0 else 1.0,
        }
    
    def reset_all(self):
        """Reset all capacity adjustments"""
        for node_id in list(self.node_states.keys()):
            self.restore_node(node_id)
        
        for edge_key in list(self.edge_states.keys()):
            state = self.edge_states[edge_key]
            self.restore_edge(state.from_node, state.to_node)


# Global instance
capacity_controller = CapacityController()

