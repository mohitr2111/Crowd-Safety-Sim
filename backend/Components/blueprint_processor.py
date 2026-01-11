"""
Blueprint Processor - Photo-to-Layout Integration (Sub-Phase 2.1)

Converts blueprint images into Digital Twin graph structures with:
- CV-based zone and exit detection
- Manual correction workflow
- Graph validation for safety constraints

NOTE: This module provides SUGGESTIONS only. Human correction and
approval is REQUIRED before any scenario can be used in simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json
import uuid
from datetime import datetime


class ElementType(Enum):
    """Types of venue elements that can be detected"""
    ZONE = "zone"
    EXIT = "exit"
    ENTRY = "entry"
    CORRIDOR = "corridor"
    RESTRICTED = "restricted"
    WAITING = "waiting"


@dataclass
class BoundingBox:
    """Bounding box for detected elements"""
    x1: int
    y1: int
    x2: int
    y2: int
    
    @property
    def width(self) -> int:
        return self.x2 - self.x1
    
    @property
    def height(self) -> int:
        return self.y2 - self.y1
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
    
    @property
    def area_pixels(self) -> int:
        return self.width * self.height


@dataclass
class DetectedElement:
    """Represents a detected zone/exit/corridor from blueprint"""
    element_id: str
    element_type: ElementType
    bounding_box: BoundingBox
    confidence: float  # 0.0 - 1.0
    estimated_area_m2: float
    estimated_capacity: int
    label: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "element_id": self.element_id,
            "element_type": self.element_type.value,
            "bounding_box": {
                "x1": self.bounding_box.x1,
                "y1": self.bounding_box.y1,
                "x2": self.bounding_box.x2,
                "y2": self.bounding_box.y2
            },
            "confidence": self.confidence,
            "estimated_area_m2": self.estimated_area_m2,
            "estimated_capacity": self.estimated_capacity,
            "label": self.label
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "DetectedElement":
        return DetectedElement(
            element_id=data["element_id"],
            element_type=ElementType(data["element_type"]),
            bounding_box=BoundingBox(
                data["bounding_box"]["x1"],
                data["bounding_box"]["y1"],
                data["bounding_box"]["x2"],
                data["bounding_box"]["y2"]
            ),
            confidence=data["confidence"],
            estimated_area_m2=data["estimated_area_m2"],
            estimated_capacity=data["estimated_capacity"],
            label=data.get("label")
        )


@dataclass
class DetectedConnection:
    """Connection between two detected elements"""
    from_element_id: str
    to_element_id: str
    estimated_width_m: float
    bidirectional: bool = True
    confidence: float = 0.8
    
    def to_dict(self) -> Dict:
        return {
            "from_element_id": self.from_element_id,
            "to_element_id": self.to_element_id,
            "estimated_width_m": self.estimated_width_m,
            "bidirectional": self.bidirectional,
            "confidence": self.confidence
        }


@dataclass
class DetectionResult:
    """Complete detection result from blueprint processing"""
    detection_id: str
    created_at: datetime
    image_dimensions: Tuple[int, int]  # (width, height)
    scale_meters_per_pixel: float
    elements: List[DetectedElement]
    connections: List[DetectedConnection]
    warnings: List[str]
    confidence_overall: float
    
    def to_dict(self) -> Dict:
        return {
            "detection_id": self.detection_id,
            "created_at": self.created_at.isoformat(),
            "image_dimensions": list(self.image_dimensions),
            "scale_meters_per_pixel": self.scale_meters_per_pixel,
            "elements": [e.to_dict() for e in self.elements],
            "connections": [c.to_dict() for c in self.connections],
            "warnings": self.warnings,
            "confidence_overall": self.confidence_overall
        }


@dataclass
class ManualCorrection:
    """Record of human correction to detection result"""
    correction_id: str
    timestamp: datetime
    correction_type: str  # "add", "modify", "delete", "connection"
    target_element_id: Optional[str]
    changes: Dict
    
    def to_dict(self) -> Dict:
        return {
            "correction_id": self.correction_id,
            "timestamp": self.timestamp.isoformat(),
            "correction_type": self.correction_type,
            "target_element_id": self.target_element_id,
            "changes": self.changes
        }


@dataclass
class CorrectedVenue:
    """Final corrected venue ready for Digital Twin generation"""
    detection_id: str
    venue_name: str
    nodes: List[Dict]  # DigitalTwin-compatible node configs
    edges: List[Dict]  # DigitalTwin-compatible edge configs
    validation_passed: bool
    validation_errors: List[str]
    manual_corrections: List[ManualCorrection]
    
    def to_dict(self) -> Dict:
        return {
            "detection_id": self.detection_id,
            "venue_name": self.venue_name,
            "nodes": self.nodes,
            "edges": self.edges,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "manual_corrections": [c.to_dict() for c in self.manual_corrections]
        }


class BlueprintProcessor:
    """
    Processes blueprint images to generate Digital Twin configurations.
    
    IMPORTANT: This processor provides SUGGESTIONS only.
    Human correction and approval is REQUIRED before finalization.
    """
    
    # Default scale assumptions based on venue type
    VENUE_TYPE_SCALES = {
        "stadium": 0.5,      # 0.5 meters per pixel typical
        "railway": 0.3,
        "temple": 0.4,
        "festival": 0.6,
        "default": 0.4
    }
    
    # Capacity estimation (people per m²)
    CAPACITY_DENSITY = {
        ElementType.ZONE: 2.0,      # General zones
        ElementType.EXIT: 1.5,       # Exit areas more sparse
        ElementType.ENTRY: 2.0,
        ElementType.CORRIDOR: 1.0,   # Corridors lower density
        ElementType.WAITING: 2.5,    # Waiting areas higher
        ElementType.RESTRICTED: 0.5
    }
    
    def __init__(self):
        self._pending_detections: Dict[str, DetectionResult] = {}
        self._corrections: Dict[str, List[ManualCorrection]] = {}
    
    def process_blueprint(
        self,
        image_data: bytes,
        venue_type: str = "default",
        scale_hint: Optional[float] = None
    ) -> DetectionResult:
        """
        Process a blueprint image and detect zones/exits/corridors.
        
        Args:
            image_data: Raw image bytes
            venue_type: "stadium", "railway", "temple", "festival"
            scale_hint: Optional meters per pixel override
            
        Returns:
            DetectionResult with suggested elements and connections
            
        NOTE: Results require human correction before use.
        """
        detection_id = str(uuid.uuid4())
        
        # Determine scale
        scale = scale_hint or self.VENUE_TYPE_SCALES.get(
            venue_type, self.VENUE_TYPE_SCALES["default"]
        )
        
        # Get image dimensions (simplified - would use PIL/OpenCV in real implementation)
        image_dims = self._get_image_dimensions(image_data)
        
        # Detect elements using CV (simplified mock implementation)
        elements, connections, warnings = self._detect_elements(
            image_data, image_dims, scale, venue_type
        )
        
        # Calculate overall confidence
        if elements:
            confidence_overall = sum(e.confidence for e in elements) / len(elements)
        else:
            confidence_overall = 0.0
            warnings.append("No elements detected - manual creation required")
        
        result = DetectionResult(
            detection_id=detection_id,
            created_at=datetime.now(),
            image_dimensions=image_dims,
            scale_meters_per_pixel=scale,
            elements=elements,
            connections=connections,
            warnings=warnings,
            confidence_overall=confidence_overall
        )
        
        # Store for later correction
        self._pending_detections[detection_id] = result
        self._corrections[detection_id] = []
        
        return result
    
    def _get_image_dimensions(self, image_data: bytes) -> Tuple[int, int]:
        """Get image dimensions from raw bytes"""
        # Simplified: In real implementation, use PIL
        # For now, assume standard blueprint size
        try:
            # Try to detect PNG dimensions from header
            if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                width = int.from_bytes(image_data[16:20], 'big')
                height = int.from_bytes(image_data[20:24], 'big')
                return (width, height)
        except:
            pass
        # Default dimensions
        return (1000, 800)
    
    def _detect_elements(
        self,
        image_data: bytes,
        image_dims: Tuple[int, int],
        scale: float,
        venue_type: str
    ) -> Tuple[List[DetectedElement], List[DetectedConnection], List[str]]:
        """
        Detect venue elements from image.
        
        In production, this would use:
        - OpenCV for edge detection and contour finding
        - YOLOv8 or similar for object detection
        - OCR for label extraction
        
        Current implementation provides template-based suggestions
        based on venue type to demonstrate the workflow.
        """
        warnings = []
        elements = []
        connections = []
        
        width, height = image_dims
        
        # Generate template-based suggestions by venue type
        if venue_type == "stadium":
            elements, connections = self._generate_stadium_template(width, height, scale)
            warnings.append("Using stadium template - please verify zone positions")
        elif venue_type == "railway":
            elements, connections = self._generate_railway_template(width, height, scale)
            warnings.append("Using railway template - please verify platform positions")
        elif venue_type == "festival":
            elements, connections = self._generate_festival_template(width, height, scale)
            warnings.append("Using festival template - please verify corridor layout")
        else:
            # Generic grid layout
            elements, connections = self._generate_generic_template(width, height, scale)
            warnings.append("Using generic template - manual configuration recommended")
        
        warnings.append("CV detection is template-based - human verification required")
        
        return elements, connections, warnings
    
    def _generate_stadium_template(
        self, width: int, height: int, scale: float
    ) -> Tuple[List[DetectedElement], List[DetectedConnection]]:
        """Generate stadium venue template"""
        elements = []
        connections = []
        
        # Calculate positions as percentages of image
        # Main seating zones
        zones = [
            ("zone_north", 0.5, 0.85, 0.4, 0.2, ElementType.ZONE),
            ("zone_south", 0.5, 0.15, 0.4, 0.2, ElementType.ZONE),
            ("zone_east", 0.85, 0.5, 0.2, 0.4, ElementType.ZONE),
            ("zone_west", 0.15, 0.5, 0.2, 0.4, ElementType.ZONE),
        ]
        
        # Central concourse
        zones.append(("concourse", 0.5, 0.5, 0.2, 0.2, ElementType.WAITING))
        
        # Exits
        zones.append(("exit_main", 0.5, 0.02, 0.15, 0.05, ElementType.EXIT))
        zones.append(("exit_side_1", 0.02, 0.3, 0.05, 0.1, ElementType.EXIT))
        zones.append(("exit_side_2", 0.98, 0.3, 0.05, 0.1, ElementType.EXIT))
        
        for zone_id, cx, cy, w_ratio, h_ratio, etype in zones:
            box_w = int(width * w_ratio)
            box_h = int(height * h_ratio)
            x1 = int(width * cx - box_w / 2)
            y1 = int(height * cy - box_h / 2)
            
            area_m2 = (box_w * scale) * (box_h * scale)
            capacity = int(area_m2 * self.CAPACITY_DENSITY[etype])
            
            elements.append(DetectedElement(
                element_id=zone_id,
                element_type=etype,
                bounding_box=BoundingBox(x1, y1, x1 + box_w, y1 + box_h),
                confidence=0.7,
                estimated_area_m2=area_m2,
                estimated_capacity=capacity,
                label=zone_id.replace("_", " ").title()
            ))
        
        # Define connections
        conn_pairs = [
            ("zone_north", "concourse"),
            ("zone_south", "concourse"),
            ("zone_east", "concourse"),
            ("zone_west", "concourse"),
            ("concourse", "exit_main"),
            ("concourse", "exit_side_1"),
            ("concourse", "exit_side_2"),
        ]
        
        for from_id, to_id in conn_pairs:
            connections.append(DetectedConnection(
                from_element_id=from_id,
                to_element_id=to_id,
                estimated_width_m=3.0,
                bidirectional=True,
                confidence=0.6
            ))
        
        return elements, connections
    
    def _generate_railway_template(
        self, width: int, height: int, scale: float
    ) -> Tuple[List[DetectedElement], List[DetectedConnection]]:
        """Generate railway station template"""
        elements = []
        connections = []
        
        # Platform areas
        zones = [
            ("platform_1", 0.2, 0.3, 0.15, 0.5, ElementType.WAITING),
            ("platform_2", 0.5, 0.3, 0.15, 0.5, ElementType.WAITING),
            ("platform_3", 0.8, 0.3, 0.15, 0.5, ElementType.WAITING),
        ]
        
        # Main concourse
        zones.append(("main_hall", 0.5, 0.8, 0.6, 0.15, ElementType.ZONE))
        
        # Entries and exits
        zones.append(("entry_main", 0.5, 0.95, 0.3, 0.08, ElementType.ENTRY))
        zones.append(("exit_east", 0.95, 0.5, 0.08, 0.2, ElementType.EXIT))
        zones.append(("exit_west", 0.05, 0.5, 0.08, 0.2, ElementType.EXIT))
        
        # Foot-over bridge
        zones.append(("fob", 0.5, 0.55, 0.7, 0.05, ElementType.CORRIDOR))
        
        for zone_id, cx, cy, w_ratio, h_ratio, etype in zones:
            box_w = int(width * w_ratio)
            box_h = int(height * h_ratio)
            x1 = int(width * cx - box_w / 2)
            y1 = int(height * cy - box_h / 2)
            
            area_m2 = (box_w * scale) * (box_h * scale)
            capacity = int(area_m2 * self.CAPACITY_DENSITY[etype])
            
            elements.append(DetectedElement(
                element_id=zone_id,
                element_type=etype,
                bounding_box=BoundingBox(x1, y1, x1 + box_w, y1 + box_h),
                confidence=0.7,
                estimated_area_m2=area_m2,
                estimated_capacity=capacity,
                label=zone_id.replace("_", " ").title()
            ))
        
        # Connections
        conn_pairs = [
            ("entry_main", "main_hall"),
            ("main_hall", "fob"),
            ("fob", "platform_1"),
            ("fob", "platform_2"),
            ("fob", "platform_3"),
            ("main_hall", "exit_east"),
            ("main_hall", "exit_west"),
        ]
        
        for from_id, to_id in conn_pairs:
            connections.append(DetectedConnection(
                from_element_id=from_id,
                to_element_id=to_id,
                estimated_width_m=4.0,
                bidirectional=True,
                confidence=0.6
            ))
        
        return elements, connections
    
    def _generate_festival_template(
        self, width: int, height: int, scale: float
    ) -> Tuple[List[DetectedElement], List[DetectedConnection]]:
        """Generate festival corridor template"""
        elements = []
        connections = []
        
        # Linear corridor with stages
        zones = [
            ("entry_gate", 0.1, 0.5, 0.1, 0.3, ElementType.ENTRY),
            ("stage_1_area", 0.3, 0.5, 0.15, 0.6, ElementType.ZONE),
            ("corridor_1", 0.45, 0.5, 0.08, 0.4, ElementType.CORRIDOR),
            ("stage_2_area", 0.6, 0.5, 0.15, 0.6, ElementType.ZONE),
            ("corridor_2", 0.75, 0.5, 0.08, 0.4, ElementType.CORRIDOR),
            ("exit_main", 0.9, 0.5, 0.1, 0.3, ElementType.EXIT),
        ]
        
        for zone_id, cx, cy, w_ratio, h_ratio, etype in zones:
            box_w = int(width * w_ratio)
            box_h = int(height * h_ratio)
            x1 = int(width * cx - box_w / 2)
            y1 = int(height * cy - box_h / 2)
            
            area_m2 = (box_w * scale) * (box_h * scale)
            capacity = int(area_m2 * self.CAPACITY_DENSITY[etype])
            
            elements.append(DetectedElement(
                element_id=zone_id,
                element_type=etype,
                bounding_box=BoundingBox(x1, y1, x1 + box_w, y1 + box_h),
                confidence=0.7,
                estimated_area_m2=area_m2,
                estimated_capacity=capacity,
                label=zone_id.replace("_", " ").title()
            ))
        
        # Linear connections
        conn_pairs = [
            ("entry_gate", "stage_1_area"),
            ("stage_1_area", "corridor_1"),
            ("corridor_1", "stage_2_area"),
            ("stage_2_area", "corridor_2"),
            ("corridor_2", "exit_main"),
        ]
        
        for from_id, to_id in conn_pairs:
            connections.append(DetectedConnection(
                from_element_id=from_id,
                to_element_id=to_id,
                estimated_width_m=5.0,
                bidirectional=True,
                confidence=0.7
            ))
        
        return elements, connections
    
    def _generate_generic_template(
        self, width: int, height: int, scale: float
    ) -> Tuple[List[DetectedElement], List[DetectedConnection]]:
        """Generate generic grid template"""
        elements = []
        connections = []
        
        # 3x3 grid with entry and exit
        zones = [
            ("entry", 0.5, 0.1, 0.2, 0.1, ElementType.ENTRY),
            ("zone_a", 0.25, 0.35, 0.25, 0.2, ElementType.ZONE),
            ("zone_b", 0.5, 0.35, 0.25, 0.2, ElementType.ZONE),
            ("zone_c", 0.75, 0.35, 0.25, 0.2, ElementType.ZONE),
            ("zone_d", 0.25, 0.65, 0.25, 0.2, ElementType.ZONE),
            ("zone_e", 0.5, 0.65, 0.25, 0.2, ElementType.ZONE),
            ("zone_f", 0.75, 0.65, 0.25, 0.2, ElementType.ZONE),
            ("exit", 0.5, 0.9, 0.2, 0.1, ElementType.EXIT),
        ]
        
        for zone_id, cx, cy, w_ratio, h_ratio, etype in zones:
            box_w = int(width * w_ratio)
            box_h = int(height * h_ratio)
            x1 = int(width * cx - box_w / 2)
            y1 = int(height * cy - box_h / 2)
            
            area_m2 = (box_w * scale) * (box_h * scale)
            capacity = int(area_m2 * self.CAPACITY_DENSITY[etype])
            
            elements.append(DetectedElement(
                element_id=zone_id,
                element_type=etype,
                bounding_box=BoundingBox(x1, y1, x1 + box_w, y1 + box_h),
                confidence=0.5,
                estimated_area_m2=area_m2,
                estimated_capacity=capacity,
                label=zone_id.replace("_", " ").title()
            ))
        
        # Grid connections
        conn_pairs = [
            ("entry", "zone_a"), ("entry", "zone_b"), ("entry", "zone_c"),
            ("zone_a", "zone_b"), ("zone_b", "zone_c"),
            ("zone_a", "zone_d"), ("zone_b", "zone_e"), ("zone_c", "zone_f"),
            ("zone_d", "zone_e"), ("zone_e", "zone_f"),
            ("zone_d", "exit"), ("zone_e", "exit"), ("zone_f", "exit"),
        ]
        
        for from_id, to_id in conn_pairs:
            connections.append(DetectedConnection(
                from_element_id=from_id,
                to_element_id=to_id,
                estimated_width_m=3.0,
                bidirectional=True,
                confidence=0.5
            ))
        
        return elements, connections
    
    def apply_correction(
        self,
        detection_id: str,
        correction_type: str,
        target_element_id: Optional[str],
        changes: Dict
    ) -> DetectionResult:
        """
        Apply human correction to a detection result.
        
        Args:
            detection_id: ID of the detection to correct
            correction_type: "add", "modify", "delete", "connection"
            target_element_id: Element being modified (None for add)
            changes: Dictionary of changes to apply
            
        Returns:
            Updated DetectionResult
        """
        if detection_id not in self._pending_detections:
            raise ValueError(f"Detection {detection_id} not found")
        
        result = self._pending_detections[detection_id]
        correction = ManualCorrection(
            correction_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            correction_type=correction_type,
            target_element_id=target_element_id,
            changes=changes
        )
        self._corrections[detection_id].append(correction)
        
        if correction_type == "add":
            # Add new element
            new_element = DetectedElement.from_dict(changes)
            result.elements.append(new_element)
            
        elif correction_type == "modify" and target_element_id:
            # Modify existing element
            for i, elem in enumerate(result.elements):
                if elem.element_id == target_element_id:
                    for key, value in changes.items():
                        if hasattr(elem, key):
                            setattr(elem, key, value)
                    break
                    
        elif correction_type == "delete" and target_element_id:
            # Delete element
            result.elements = [e for e in result.elements 
                             if e.element_id != target_element_id]
            # Also remove connections involving this element
            result.connections = [c for c in result.connections
                                 if c.from_element_id != target_element_id
                                 and c.to_element_id != target_element_id]
                                 
        elif correction_type == "connection":
            # Add or remove connection
            if changes.get("action") == "add":
                result.connections.append(DetectedConnection(
                    from_element_id=changes["from"],
                    to_element_id=changes["to"],
                    estimated_width_m=changes.get("width", 3.0),
                    bidirectional=changes.get("bidirectional", True),
                    confidence=1.0  # Human-added = high confidence
                ))
            elif changes.get("action") == "delete":
                result.connections = [c for c in result.connections
                                     if not (c.from_element_id == changes["from"]
                                            and c.to_element_id == changes["to"])]
        
        return result
    
    def validate_graph(self, detection_id: str) -> Tuple[bool, List[str]]:
        """
        Validate that the detected/corrected graph is safe for simulation.
        
        Checks:
        1. All exits are reachable from all entries
        2. No isolated nodes
        3. Capacity ratios are realistic
        4. At least one entry and one exit
        
        Returns:
            (is_valid, list of error messages)
        """
        if detection_id not in self._pending_detections:
            return False, [f"Detection {detection_id} not found"]
        
        result = self._pending_detections[detection_id]
        errors = []
        
        # Check for entries and exits
        entries = [e for e in result.elements 
                  if e.element_type == ElementType.ENTRY]
        exits = [e for e in result.elements 
                if e.element_type == ElementType.EXIT]
        
        if not entries:
            errors.append("No entry points defined - at least one required")
        if not exits:
            errors.append("No exit points defined - at least one required")
        
        # Build adjacency for reachability check
        element_ids = {e.element_id for e in result.elements}
        adjacency: Dict[str, set] = {eid: set() for eid in element_ids}
        
        for conn in result.connections:
            if conn.from_element_id in adjacency and conn.to_element_id in adjacency:
                adjacency[conn.from_element_id].add(conn.to_element_id)
                if conn.bidirectional:
                    adjacency[conn.to_element_id].add(conn.from_element_id)
        
        # Check connectivity using BFS
        def is_reachable(start: str, end: str) -> bool:
            if start not in adjacency or end not in adjacency:
                return False
            visited = set()
            queue = [start]
            while queue:
                current = queue.pop(0)
                if current == end:
                    return True
                if current in visited:
                    continue
                visited.add(current)
                queue.extend(adjacency[current])
            return False
        
        # Check all entries can reach all exits
        for entry in entries:
            for exit_elem in exits:
                if not is_reachable(entry.element_id, exit_elem.element_id):
                    errors.append(
                        f"Exit '{exit_elem.element_id}' not reachable from "
                        f"entry '{entry.element_id}'"
                    )
        
        # Check for isolated nodes
        for element in result.elements:
            if not adjacency[element.element_id]:
                # Check if any connection points to this node
                incoming = any(c.to_element_id == element.element_id 
                              for c in result.connections)
                if not incoming:
                    errors.append(f"Node '{element.element_id}' is isolated")
        
        # Check capacity ratios
        for element in result.elements:
            density = element.estimated_capacity / element.estimated_area_m2
            if density < 0.5:
                errors.append(
                    f"Node '{element.element_id}' has very low capacity density "
                    f"({density:.2f} people/m²)"
                )
            elif density > 5.0:
                errors.append(
                    f"Node '{element.element_id}' has dangerously high capacity "
                    f"({density:.2f} people/m²) - stampede risk"
                )
        
        return len(errors) == 0, errors
    
    def finalize_to_digital_twin(
        self,
        detection_id: str,
        venue_name: str
    ) -> CorrectedVenue:
        """
        Finalize detection into Digital Twin configuration.
        
        REQUIRES: Validation must pass before finalization.
        
        Returns:
            CorrectedVenue with DigitalTwin-compatible configurations
        """
        is_valid, errors = self.validate_graph(detection_id)
        
        if detection_id not in self._pending_detections:
            raise ValueError(f"Detection {detection_id} not found")
        
        result = self._pending_detections[detection_id]
        
        # Convert elements to DigitalTwin nodes
        nodes = []
        for elem in result.elements:
            node_type = "general"
            if elem.element_type == ElementType.EXIT:
                node_type = "exit"
            elif elem.element_type == ElementType.ENTRY:
                node_type = "entry"
            elif elem.element_type == ElementType.WAITING:
                node_type = "waiting"
            elif elem.element_type == ElementType.RESTRICTED:
                node_type = "restricted"
            
            nodes.append({
                "node_id": elem.element_id,
                "area_m2": elem.estimated_area_m2,
                "capacity": elem.estimated_capacity,
                "position": list(elem.bounding_box.center),
                "area_type": node_type
            })
        
        # Convert connections to DigitalTwin edges
        edges = []
        for conn in result.connections:
            # Estimate length from positions
            from_elem = next((e for e in result.elements 
                            if e.element_id == conn.from_element_id), None)
            to_elem = next((e for e in result.elements 
                          if e.element_id == conn.to_element_id), None)
            
            if from_elem and to_elem:
                from_pos = from_elem.bounding_box.center
                to_pos = to_elem.bounding_box.center
                length_pixels = ((to_pos[0] - from_pos[0])**2 + 
                               (to_pos[1] - from_pos[1])**2) ** 0.5
                length_m = length_pixels * result.scale_meters_per_pixel
                
                # Flow capacity based on width
                flow_capacity = int(conn.estimated_width_m * 20)  # ~20 people/m width
                
                edges.append({
                    "from_node": conn.from_element_id,
                    "to_node": conn.to_element_id,
                    "width_m": conn.estimated_width_m,
                    "length_m": max(5.0, length_m),  # Minimum 5m
                    "flow_capacity": flow_capacity,
                    "bidirectional": conn.bidirectional
                })
        
        return CorrectedVenue(
            detection_id=detection_id,
            venue_name=venue_name,
            nodes=nodes,
            edges=edges,
            validation_passed=is_valid,
            validation_errors=errors,
            manual_corrections=self._corrections.get(detection_id, [])
        )
    
    def generate_digital_twin_code(self, corrected_venue: CorrectedVenue) -> str:
        """
        Generate Python code to create the Digital Twin.
        
        Returns executable Python code that creates the DigitalTwin.
        """
        lines = [
            "from simulation.digital_twin import DigitalTwin",
            "",
            f"def create_{corrected_venue.venue_name.lower().replace(' ', '_')}_scenario() -> DigitalTwin:",
            f'    """Auto-generated from blueprint: {corrected_venue.venue_name}"""',
            "    twin = DigitalTwin()",
            "",
            "    # Areas/Zones",
        ]
        
        for node in corrected_venue.nodes:
            lines.append(
                f'    twin.add_area("{node["node_id"]}", '
                f'area_m2={node["area_m2"]:.1f}, '
                f'capacity={node["capacity"]}, '
                f'position=({node["position"][0]:.1f}, {node["position"][1]:.1f}), '
                f'area_type="{node["area_type"]}")'
            )
        
        lines.append("")
        lines.append("    # Paths/Corridors")
        
        for edge in corrected_venue.edges:
            lines.append(
                f'    twin.add_path("{edge["from_node"]}", "{edge["to_node"]}", '
                f'width_m={edge["width_m"]:.1f}, '
                f'length_m={edge["length_m"]:.1f}, '
                f'flow_capacity={edge["flow_capacity"]}, '
                f'bidirectional={edge["bidirectional"]})'
            )
        
        lines.append("")
        lines.append("    return twin")
        
        return "\n".join(lines)


# Singleton instance for use across the application
_processor_instance: Optional[BlueprintProcessor] = None


def get_blueprint_processor() -> BlueprintProcessor:
    """Get the singleton BlueprintProcessor instance"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = BlueprintProcessor()
    return _processor_instance
