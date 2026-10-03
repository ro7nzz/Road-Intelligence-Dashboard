from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.database import Base


class AnalysisRecord(Base):
    """
    SQLAlchemy ORM model for storing RoadAI analysis records.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # 5 Locked Contextual Factors (0.0 - 100.0)
    location_risk = Column(Float, nullable=False, default=0.0)
    road_importance = Column(Float, nullable=False, default=0.0)
    traffic = Column(Float, nullable=False, default=0.0)
    complaints = Column(Float, nullable=False, default=0.0)
    historical_recurrence = Column(Float, nullable=False, default=0.0)

    # Severity & Priority Analysis Outcomes
    aggregated_severity = Column(Float, nullable=False)
    final_priority_score = Column(Float, nullable=False)
    priority_level = Column(String(50), nullable=False)
    recommendations = Column(Text, nullable=False)  # JSON-encoded list of recommendation strings
    explanation = Column(Text, nullable=False)

    # Relationship to detected damages
    detections = relationship("DetectionRecord", back_populates="analysis", cascade="all, delete-orphan")


class DetectionRecord(Base):
    """
    SQLAlchemy ORM model for storing individual bounding box damage detections.
    """
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)

    class_id = Column(Integer, nullable=False)
    class_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)

    # Bounding Box Coordinates (pixels)
    x_min = Column(Float, nullable=False)
    y_min = Column(Float, nullable=False)
    x_max = Column(Float, nullable=False)
    y_max = Column(Float, nullable=False)

    # Damage Severity Analysis
    box_area_ratio = Column(Float, nullable=False)
    base_severity = Column(Float, nullable=False)
    calculated_severity = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)

    # Parent Relationship
    analysis = relationship("AnalysisRecord", back_populates="detections")
