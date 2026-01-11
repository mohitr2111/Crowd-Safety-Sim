from pathlib import Path
import json
from typing import Dict, List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from simulation.scenarios import SCENARIOS
from Components.blueprint_processor import (
    get_blueprint_processor,
    DetectionResult,
    CorrectedVenue
)


router = APIRouter()


# ============================================================
# Blueprint Processing Models (Sub-Phase 2.1)
# ============================================================

class BlueprintUploadResponse(BaseModel):
    detection_id: str
    elements_count: int
    connections_count: int
    warnings: List[str]
    confidence_overall: float
    message: str


class CorrectionRequest(BaseModel):
    detection_id: str
    correction_type: str  # "add", "modify", "delete", "connection"
    target_element_id: Optional[str] = None
    changes: Dict


class ValidationResponse(BaseModel):
    detection_id: str
    is_valid: bool
    errors: List[str]


class FinalizeRequest(BaseModel):
    detection_id: str
    venue_name: str


class FinalizeResponse(BaseModel):
    venue_name: str
    nodes_count: int
    edges_count: int
    validation_passed: bool
    validation_errors: List[str]
    digital_twin_code: str
    scenario_json: Dict


# ============================================================
# Blueprint Processing Endpoints (Sub-Phase 2.1)
# ============================================================

@router.post("/scenarios/from-blueprint", response_model=BlueprintUploadResponse)
async def upload_blueprint(
    file: UploadFile = File(...),
    venue_type: str = Form(default="default"),
    scale_hint: Optional[float] = Form(default=None)
):
    """
    Upload a blueprint image and get initial zone/exit detection.
    
    This provides SUGGESTIONS only. Human correction is REQUIRED
    before the venue can be used in simulation.
    
    Args:
        file: Blueprint image (PNG, JPG, PDF)
        venue_type: "stadium", "railway", "temple", "festival", "default"
        scale_hint: Optional meters per pixel override
        
    Returns:
        Detection result with suggested zones and connections
    """
    # Read image data
    image_data = await file.read()
    
    if len(image_data) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    # Process blueprint
    processor = get_blueprint_processor()
    result = processor.process_blueprint(
        image_data=image_data,
        venue_type=venue_type,
        scale_hint=scale_hint
    )
    
    return BlueprintUploadResponse(
        detection_id=result.detection_id,
        elements_count=len(result.elements),
        connections_count=len(result.connections),
        warnings=result.warnings,
        confidence_overall=result.confidence_overall,
        message="Blueprint processed. Human correction required before use."
    )


@router.get("/scenarios/from-blueprint/{detection_id}")
async def get_detection_result(detection_id: str):
    """
    Get the current state of a blueprint detection including all elements
    and connections. Use this to display the detection for correction.
    """
    processor = get_blueprint_processor()
    
    if detection_id not in processor._pending_detections:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    result = processor._pending_detections[detection_id]
    return result.to_dict()


@router.post("/scenarios/from-blueprint/correct")
async def apply_correction(request: CorrectionRequest):
    """
    Apply a human correction to a detection result.
    
    Correction types:
    - "add": Add new element (changes must include full element data)
    - "modify": Modify existing element (target_element_id required)
    - "delete": Delete element (target_element_id required)
    - "connection": Add/remove connection (changes must include action, from, to)
    
    Returns updated detection result.
    """
    processor = get_blueprint_processor()
    
    try:
        result = processor.apply_correction(
            detection_id=request.detection_id,
            correction_type=request.correction_type,
            target_element_id=request.target_element_id,
            changes=request.changes
        )
        return {
            "success": True,
            "elements_count": len(result.elements),
            "connections_count": len(result.connections),
            "message": f"Correction applied: {request.correction_type}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/scenarios/from-blueprint/{detection_id}/validate", 
            response_model=ValidationResponse)
async def validate_blueprint(detection_id: str):
    """
    Validate the current detection/correction state.
    
    Checks:
    - All exits reachable from all entries
    - No isolated nodes
    - Capacity ratios within realistic bounds
    - At least one entry and one exit
    
    Returns validation result with any errors found.
    """
    processor = get_blueprint_processor()
    
    is_valid, errors = processor.validate_graph(detection_id)
    
    return ValidationResponse(
        detection_id=detection_id,
        is_valid=is_valid,
        errors=errors
    )


@router.post("/scenarios/from-blueprint/finalize", response_model=FinalizeResponse)
async def finalize_blueprint(request: FinalizeRequest):
    """
    Finalize a corrected blueprint into a Digital Twin scenario.
    
    WARNING: Validation errors will be included in response but
    will NOT block finalization. Review errors carefully.
    
    Returns:
        - Digital Twin configuration as JSON
        - Python code to create the scenario
        - Validation status
    """
    processor = get_blueprint_processor()
    
    try:
        corrected = processor.finalize_to_digital_twin(
            detection_id=request.detection_id,
            venue_name=request.venue_name
        )
        
        code = processor.generate_digital_twin_code(corrected)
        
        return FinalizeResponse(
            venue_name=corrected.venue_name,
            nodes_count=len(corrected.nodes),
            edges_count=len(corrected.edges),
            validation_passed=corrected.validation_passed,
            validation_errors=corrected.validation_errors,
            digital_twin_code=code,
            scenario_json=corrected.to_dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/scenarios")
async def get_scenarios():
    """Get available scenarios from both built-in and JSON files"""
    scenarios_dir = Path(__file__).parent.parent / "scenarios"
    scenarios = []

    # Load from JSON files if scenarios folder exists
    if scenarios_dir.exists():
        scenario_files = scenarios_dir.glob("*.json")

        for file in scenario_files:
            try:
                with open(file, "r") as f:
                    config = json.load(f)
                    scenarios.append(
                        {
                            "id": file.stem,
                            "name": config.get("name", file.stem),
                            "description": config.get("description", ""),
                            "source": "file",
                        }
                    )
            except Exception as e:
                print(f"Error loading {file}: {e}")

    # Add built-in scenarios
    for scenario_id in SCENARIOS.keys():
        # Check if not already added from file
        if not any(s["id"] == scenario_id for s in scenarios):
            descriptions = {
                "stadium_exit": "Stadium evacuation after event (600-1200 agents)",
                "railway_station": "Railway station during peak hours (150-400 agents)",
            }
            scenarios.append(
                {
                    "id": scenario_id,
                    "name": scenario_id.replace("_", " ").title(),
                    "description": descriptions.get(scenario_id, "Built-in scenario"),
                    "source": "built-in",
                }
            )

    return {"scenarios": scenarios}
