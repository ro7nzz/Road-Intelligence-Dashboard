from typing import List
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x_min: float = Field(..., description="Top-left X coordinate (pixels)")
    y_min: float = Field(..., description="Top-left Y coordinate (pixels)")
    x_max: float = Field(..., description="Bottom-right X coordinate (pixels)")
    y_max: float = Field(..., description="Bottom-right Y coordinate (pixels)")


class DetectionItem(BaseModel):
    class_id: int = Field(..., description="YOLO class index")
    class_name: str = Field(..., description="Damage type name")
    confidence: float = Field(..., description="Detection confidence score (0.0 - 1.0)")
    box: BoundingBox = Field(..., description="Bounding box pixel coordinates")


class DetectionResponse(BaseModel):
    filename: str = Field(..., description="Uploaded image filename")
    image_width: int = Field(..., description="Image width in pixels")
    image_height: int = Field(..., description="Image height in pixels")
    detections_count: int = Field(..., description="Total number of detected road damages")
    detections: List[DetectionItem] = Field(default_factory=list, description="List of detected road damage items")
