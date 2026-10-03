from fastapi import APIRouter, File, UploadFile, HTTPException, status
from backend.schemas.detection import DetectionResponse
from backend.utils.image_utils import load_image_from_bytes
from backend.services.yolo_service import run_yolo_inference

router = APIRouter(
    prefix="/api/v1",
    tags=["Detection"]
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@router.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect Road Damage in Uploaded Image",
    description="Accepts an uploaded image file, runs YOLO object detection, and returns detected damage bounding boxes, confidence scores, and class labels."
)
async def detect_road_damage(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename missing in upload request."
        )

    # Extension validation
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        contents = await file.read()
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

    try:
        detection_result = run_yolo_inference(image=image, filename=file.filename)
        return detection_result
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(fnfe)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"YOLO inference error: {str(e)}"
        )
