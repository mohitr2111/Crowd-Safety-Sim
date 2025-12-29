import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional


class DigitalTwin:
    """Graph-based representation of physical space"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for one-way paths
        self.node_data = {}  # Store node metadata
        self.edge_data = {}  # Store edge metadata
        
    def add_area(self, node_id: str, area_m2: float, capacity: int, 
                 position: Tuple[float, float], area_type: str = "general"):
        """
        Add a spatial area (node) to the digital twin
        
        Args:
            node_id: Unique identifier (e.g., "entry_gate_1", "zone_A")
            area_m2: Physical area in square meters
            capacity: Maximum safe occupancy
            position: (x, y) coordinates for visualization
            area_type: "entry", "exit", "general", "waiting", "restricted"
        """
        self.graph.add_node(node_id)
        self.node_data[node_id] = {
            "area_m2": area_m2,
            "capacity": capacity,
            "current_count": 0,
            "position": position,
            "type": area_type,
            "density": 0.0,
            "risk_level": "SAFE",
            "is_blocked": False,  # NEW: Track if node is temporarily closed
            "block_expires": 0.0  # NEW: When block expires
        }

        
    def add_path(self, from_node: str, to_node: str, width_m: float, 
                 length_m: float, flow_capacity: int, bidirectional: bool = True):
        """
        Add a path (edge) between two areas
        
        Args:
            from_node, to_node: Connected node IDs
            width_m: Path width in meters
            length_m: Path length in meters
            flow_capacity: Max people per minute
            bidirectional: If True, create edge in both directions
        """
        edge_key = (from_node, to_node)
        self.graph.add_edge(from_node, to_node)
        self.edge_data[edge_key] = {
            "width_m": width_m,
            "length_m": length_m,
            "flow_capacity": flow_capacity,
            "current_flow": 0,
            "congestion": 0.0  # 0-1 scale
        }
        
        if bidirectional:
            reverse_key = (to_node, from_node)
            self.graph.add_edge(to_node, from_node)
            self.edge_data[reverse_key] = self.edge_data[edge_key].copy()
    
    def update_node_count(self, node_id: str, count: int):
        """Update current occupancy and calculate density"""
        if node_id in self.node_data:
            self.node_data[node_id]["current_count"] = count
            area = self.node_data[node_id]["area_m2"]
            density = count / area if area > 0 else 0
            self.node_data[node_id]["density"] = density
            
            # Calculate risk level based on density thresholds
            self.node_data[node_id]["risk_level"] = self._calculate_risk(density)
    
    def _calculate_risk(self, density: float) -> str:
        """
        Density-based risk calculation
        Industry standard thresholds:
        - < 2 people/m²: SAFE
        - 2-4 people/m²: WARNING
        - > 4 people/m²: DANGER (stampede risk)
        """
        if density < 2.0:
            return "SAFE"
        elif density < 4.0:
            return "WARNING"
        else:
            return "DANGER"
    
    def get_danger_zones(self) -> List[str]:
        """Return list of nodes in DANGER state"""
        return [node for node, data in self.node_data.items() 
                if data["risk_level"] == "DANGER"]
    
    def get_state_snapshot(self) -> Dict:
        """Get current state for visualization/RL"""
        return {
            "nodes": self.node_data.copy(),
            "edges": self.edge_data.copy(),
            "danger_count": len(self.get_danger_zones()),
            "max_density": max((d["density"] for d in self.node_data.values()), default=0)
        }
    
    def get_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find shortest path for agent navigation, avoiding blocked nodes"""
        try:
            # Create a view of the graph excluding blocked nodes
            blocked_nodes = [
                node for node, data in self.node_data.items() 
                if data.get("is_blocked", False)
            ]
            
            # If no blocked nodes, use normal pathfinding
            if not blocked_nodes:
                return nx.shortest_path(self.graph, start, end)
            
            # Create subgraph excluding blocked nodes (except start/end)
            # We must keep start/end even if blocked, so agent can escape
            nodes_to_exclude = [n for n in blocked_nodes if n != start and n != end]
            
            if not nodes_to_exclude:
                return nx.shortest_path(self.graph, start, end)
            
            # Create subgraph without blocked nodes
            active_nodes = [n for n in self.graph.nodes() if n not in nodes_to_exclude]
            subgraph = self.graph.subgraph(active_nodes)
            
            return nx.shortest_path(subgraph, start, end)
            
        except nx.NetworkXNoPath:
            # No path exists (all routes blocked) - return None
            return None
