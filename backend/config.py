from pathlib import Path
from pydantic import BaseModel

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to finalized YOLO candidate weights
DEFAULT_MODEL_PATH = BASE_DIR / "runs" / "detect" / "ml" / "runs" / "roadai_yolo11n_320_d10_balanced" / "weights" / "best.pt"

# YOLO Class Mappings
CLASS_NAMES = {
    0: "D00_Longitudinal_Crack",
    1: "D10_Transverse_Crack",
    2: "D20_Alligator_Crack",
    3: "D40_Pothole"
}

# Inference Defaults
DEFAULT_CONFIDENCE_THRESHOLD = 0.25

# Class-Specific Severity Base Weights (0 - 100)
CLASS_SEVERITY_BASE = {
    0: 40.0,  # D00_Longitudinal_Crack
    1: 45.0,  # D10_Transverse_Crack
    2: 70.0,  # D20_Alligator_Crack
    3: 85.0,  # D40_Pothole
}

# Configurable Priority Factor Weights (Must sum to 1.0 / 100%)
PRIORITY_WEIGHTS = {
    "damage_severity": 0.40,
    "location_risk": 0.10,
    "road_importance": 0.20,
    "traffic": 0.15,
    "complaints": 0.05,
    "historical_recurrence": 0.10,
}


# SQLite Database Configuration
DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'backend' / 'roadai.db'}"


class Settings(BaseModel):
    model_path: Path = DEFAULT_MODEL_PATH
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    class_names: dict = CLASS_NAMES
    class_severity_base: dict = CLASS_SEVERITY_BASE
    priority_weights: dict = PRIORITY_WEIGHTS
    database_url: str = DEFAULT_DATABASE_URL


settings = Settings()


