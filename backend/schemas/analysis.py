from typing import List, Optional
from pydantic import BaseModel, Field
from backend.schemas.detection import DetectionItem
from backend.schemas.priority import (
    ContextualFactors,
    SeverityResult,
    PriorityResult,
)


class AnalysisResponse(BaseModel):
    """
    Complete RoadAI damage detection, severity, and repair priority analysis response schema.
    Supports both immediate execution and database persisted records.
    """
    id: Optional[int] = Field(None, description="Database record ID (if persisted)")
    created_at: Optional[str] = Field(None, description="ISO timestamp of analysis creation")
    filename: str = Field(..., description="Uploaded image filename")
    image_width: int = Field(..., description="Image width in pixels")
    image_height: int = Field(..., description="Image height in pixels")
    detections: List[DetectionItem] = Field(default_factory=list, description="List of detected road damages")
    severity: SeverityResult = Field(..., description="Aggregated and per-detection severity analysis")
    contextual_factors: ContextualFactors = Field(..., description="Normalized contextual road factors (0-100)")
    priority: PriorityResult = Field(..., description="Final 0-100 Repair Priority Score, factors, and contributions")
    recommendations: List[str] = Field(default_factory=list, description="Actionable repair and maintenance recommendations")
    explanation: str = Field(..., description="Complete human-readable explainability breakdown")
