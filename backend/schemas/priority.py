from typing import List, Dict
from pydantic import BaseModel, Field, validator


class ContextualFactors(BaseModel):
    """
    Input schema for the 5 external RoadAI contextual factors.
    All scores are normalized from 0.0 to 100.0.
    """
    location_risk: float = Field(0.0, ge=0.0, le=100.0, description="Location / hazard risk score (0-100)")
    road_importance: float = Field(0.0, ge=0.0, le=100.0, description="Road classification & importance score (0-100)")
    traffic: float = Field(0.0, ge=0.0, le=100.0, description="Traffic volume / vehicle density score (0-100)")
    complaints: float = Field(0.0, ge=0.0, le=100.0, description="Citizen complaints / reports score (0-100)")
    historical_recurrence: float = Field(0.0, ge=0.0, le=100.0, description="Historical damage recurrence frequency score (0-100)")


class DetectionSeverityItem(BaseModel):
    """
    Severity analysis breakdown for an individual detection bounding box.
    """
    class_id: int = Field(..., description="YOLO class index")
    class_name: str = Field(..., description="Damage type label")
    confidence: float = Field(..., description="YOLO detection confidence score (0.0-1.0)")
    box_area_ratio: float = Field(..., description="Relative bounding box area to image area (%)")
    base_severity: float = Field(..., description="Class baseline severity weight (0-100)")
    calculated_severity: float = Field(..., description="Computed item severity score (0-100)")
    explanation: str = Field(..., description="Step-by-step calculation breakdown for this detection")


class SeverityResult(BaseModel):
    """
    Aggregated damage severity analysis result.
    """
    aggregated_severity: float = Field(..., ge=0.0, le=100.0, description="Overall normalized damage severity score (0-100)")
    detections_severity: List[DetectionSeverityItem] = Field(default_factory=list, description="Per-detection severity breakdowns")
    explanation: str = Field(..., description="Human-readable explanation of severity aggregation")


class FactorContribution(BaseModel):
    """
    Breakdown of an individual factor's contribution to the final priority score.
    """
    factor_name: str = Field(..., description="Name of the contextual or damage factor")
    score: float = Field(..., description="Normalized factor score (0-100)")
    weight: float = Field(..., description="Configured factor weight multiplier (0.0-1.0)")
    contribution: float = Field(..., description="Calculated contribution (score * weight)")


class PriorityResult(BaseModel):
    """
    Final explainable 0-100 Repair Priority calculation result.
    """
    final_priority_score: float = Field(..., ge=0.0, le=100.0, description="Final repair priority score (0-100)")
    priority_level: str = Field(..., description="Priority classification (Low, Moderate, High, Critical)")
    factor_scores: Dict[str, float] = Field(..., description="Map of normalized scores for all 6 factors")
    factor_contributions: List[FactorContribution] = Field(..., description="Detailed contribution of each factor")
    recommendations: List[str] = Field(..., description="Deterministic repair recommendations")
    explanation: str = Field(..., description="Comprehensive step-by-step calculation breakdown")
