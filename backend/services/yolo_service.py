import logging
from PIL import Image
from ultralytics import YOLO
from backend.config import settings
from backend.schemas.detection import DetectionResponse, DetectionItem, BoundingBox

logger = logging.getLogger("roadai.yolo_service")

# Global singleton instance for YOLO model
_yolo_model = None


def get_model() -> YOLO:
    """
    Loads and returns the finalized YOLO model instance (cached singleton).
    """
    global _yolo_model
    if _yolo_model is None:
        model_path = settings.model_path
        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLO model weights file not found at '{model_path}'. "
                "Ensure final candidate weights best.pt exist."
            )
        logger.info(f"Loading YOLO model from: {model_path}")
        _yolo_model = YOLO(str(model_path))
    return _yolo_model


def run_yolo_inference(
    image: Image.Image,
    filename: str,
    confidence_threshold: float = None
) -> DetectionResponse:
    """
    Runs YOLO object detection on the provided PIL image.
    Returns structured DetectionResponse schema.
    """
    model = get_model()
    conf = confidence_threshold if confidence_threshold is not None else settings.confidence_threshold

    width, height = image.size

    # Run YOLO prediction
    results = model.predict(source=image, conf=conf, verbose=False)

    detections = []
    if results and len(results) > 0:
        boxes = results[0].boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf_val = round(float(box.conf[0].item()), 4)
                xyxy = box.xyxy[0].tolist()

                x_min, y_min, x_max, y_max = (
                    round(float(xyxy[0]), 2),
                    round(float(xyxy[1]), 2),
                    round(float(xyxy[2]), 2),
                    round(float(xyxy[3]), 2),
                )

                class_name = settings.class_names.get(cls_id, f"Unknown_Class_{cls_id}")

                detections.append(
                    DetectionItem(
                        class_id=cls_id,
                        class_name=class_name,
                        confidence=conf_val,
                        box=BoundingBox(
                            x_min=x_min,
                            y_min=y_min,
                            x_max=x_max,
                            y_max=y_max
                        )
                    )
                )

    return DetectionResponse(
        filename=filename,
        image_width=width,
        image_height=height,
        detections_count=len(detections),
        detections=detections
    )
