import json
from typing import List
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import AnalysisRecord, DetectionRecord
from backend.schemas.analysis import AnalysisResponse
from backend.schemas.detection import DetectionItem, BoundingBox
from backend.schemas.priority import (
    ContextualFactors,
    DetectionSeverityItem,
    SeverityResult,
)
from backend.utils.image_utils import load_image_from_bytes
from backend.services.yolo_service import run_yolo_inference
from backend.services.priority_service import (
    calculate_damage_severity,
    calculate_repair_priority,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Analysis"]
)

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _format_db_record(record: AnalysisRecord) -> AnalysisResponse:
    """
    Helper function to convert an AnalysisRecord database ORM model
    to the Pydantic AnalysisResponse schema.
    """
    recs = json.loads(record.recommendations) if record.recommendations else []

    det_items = []
    det_severity_items = []

    for d in record.detections:
        det_items.append(
            DetectionItem(
                class_id=d.class_id,
                class_name=d.class_name,
                confidence=d.confidence,
                box=BoundingBox(
                    x_min=d.x_min,
                    y_min=d.y_min,
                    x_max=d.x_max,
                    y_max=d.y_max
                )
            )
        )
        det_severity_items.append(
            DetectionSeverityItem(
                class_id=d.class_id,
                class_name=d.class_name,
                confidence=d.confidence,
                box_area_ratio=d.box_area_ratio,
                base_severity=d.base_severity,
                calculated_severity=d.calculated_severity,
                explanation=d.explanation
            )
        )

    sev_result = SeverityResult(
        aggregated_severity=record.aggregated_severity,
        detections_severity=det_severity_items,
        explanation=f"Aggregated Damage Severity: {record.aggregated_severity:.2f}/100."
    )

    contextual = ContextualFactors(
        location_risk=record.location_risk,
        road_importance=record.road_importance,
        traffic=record.traffic,
        complaints=record.complaints,
        historical_recurrence=record.historical_recurrence
    )

    prio_result = calculate_repair_priority(
        severity_score=record.aggregated_severity,
        contextual=contextual,
        detections=det_items
    )

    return AnalysisResponse(
        id=record.id,
        created_at=record.created_at.isoformat() if record.created_at else None,
        filename=record.filename,
        image_width=record.image_width,
        image_height=record.image_height,
        detections=det_items,
        severity=sev_result,
        contextual_factors=contextual,
        priority=prio_result,
        recommendations=recs,
        explanation=record.explanation
    )


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Road AI Damage Detection & Repair Prioritization Analysis",
    description="Accepts a road image and 5 contextual factors (0-100), runs YOLO damage detection, computes damage severity, calculates weighted repair priority, persists the analysis to SQLite, and returns explainable repair recommendations."
)
async def analyze_road_damage(
    file: UploadFile = File(...),
    location_risk: float = Form(0.0, description="Location / hazard risk score (0.0 - 100.0)"),
    road_importance: float = Form(0.0, description="Road importance score (0.0 - 100.0)"),
    traffic: float = Form(0.0, description="Traffic volume score (0.0 - 100.0)"),
    complaints: float = Form(0.0, description="Citizen complaints score (0.0 - 100.0)"),
    historical_recurrence: float = Form(0.0, description="Historical recurrence score (0.0 - 100.0)"),
    db: Session = Depends(get_db)
):
    # 1. Validate Contextual Factor Ranges (0 - 100)
    contextual_inputs = {
        "location_risk": location_risk,
        "road_importance": road_importance,
        "traffic": traffic,
        "complaints": complaints,
        "historical_recurrence": historical_recurrence,
    }

    for name, val in contextual_inputs.items():
        if val < 0.0 or val > 100.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value for '{name}': {val}. Contextual factors must be normalized between 0.0 and 100.0."
            )

    # 2. Validate Uploaded File & Extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename missing in upload request."
        )

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 3. Read and Validate Image Bytes
    try:
        contents = await file.read()
        if len(contents) > MAX_UPLOAD_SIZE_BYTES:
            raise ValueError("Uploaded file exceeds the maximum allowed size of 10 MB.")
        image = load_image_from_bytes(contents)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process image file: {str(e)}"
        )

    # 4. Pipeline Step 1: YOLO Detection
    try:
        det_response = run_yolo_inference(image=image, filename=file.filename)
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(fnfe)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"YOLO inference failed: {str(e)}"
        )

    # 5. Pipeline Step 2: Damage Severity Calculation
    sev_result = calculate_damage_severity(
        detections=det_response.detections,
        image_width=det_response.image_width,
        image_height=det_response.image_height
    )

    # 6. Pipeline Step 3: Contextual Factors & Weighted Priority Calculation
    contextual_factors = ContextualFactors(
        location_risk=location_risk,
        road_importance=road_importance,
        traffic=traffic,
        complaints=complaints,
        historical_recurrence=historical_recurrence
    )

    priority_result = calculate_repair_priority(
        severity_score=sev_result.aggregated_severity,
        contextual=contextual_factors,
        detections=det_response.detections
    )

    full_explanation = (
        f"RoadAI Pipeline Execution Complete. {sev_result.explanation} | {priority_result.explanation}"
    )

    # 7. Database Persistence Layer Integration
    db_analysis = AnalysisRecord(
        filename=det_response.filename,
        image_width=det_response.image_width,
        image_height=det_response.image_height,
        location_risk=location_risk,
        road_importance=road_importance,
        traffic=traffic,
        complaints=complaints,
        historical_recurrence=historical_recurrence,
        aggregated_severity=sev_result.aggregated_severity,
        final_priority_score=priority_result.final_priority_score,
        priority_level=priority_result.priority_level,
        recommendations=json.dumps(priority_result.recommendations),
        explanation=full_explanation
    )

    db.add(db_analysis)
    db.flush()  # Flush to generate db_analysis.id for foreign keys

    # Add detection records
    for item, sev_item in zip(det_response.detections, sev_result.detections_severity):
        db_det = DetectionRecord(
            analysis_id=db_analysis.id,
            class_id=item.class_id,
            class_name=item.class_name,
            confidence=item.confidence,
            x_min=item.box.x_min,
            y_min=item.box.y_min,
            x_max=item.box.x_max,
            y_max=item.box.y_max,
            box_area_ratio=sev_item.box_area_ratio,
            base_severity=sev_item.base_severity,
            calculated_severity=sev_item.calculated_severity,
            explanation=sev_item.explanation
        )
        db.add(db_det)

    db.commit()
    db.refresh(db_analysis)

    return AnalysisResponse(
        id=db_analysis.id,
        created_at=db_analysis.created_at.isoformat() if db_analysis.created_at else None,
        filename=det_response.filename,
        image_width=det_response.image_width,
        image_height=det_response.image_height,
        detections=det_response.detections,
        severity=sev_result,
        contextual_factors=contextual_factors,
        priority=priority_result,
        recommendations=priority_result.recommendations,
        explanation=full_explanation
    )


@router.get(
    "/analyses",
    response_model=List[AnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve List of Stored Analysis Records",
    description="Retrieves all historical RoadAI analysis records stored in the SQLite database."
)
def get_all_analyses(db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).all()
    return [_format_db_record(rec) for rec in records]


@router.get(
    "/analyses/{analysis_id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Single Analysis Record by ID",
    description="Retrieves a specific historical RoadAI analysis record including its detected road damages."
)
def get_analysis_by_id(analysis_id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID {analysis_id} not found."
        )
    return _format_db_record(record)




