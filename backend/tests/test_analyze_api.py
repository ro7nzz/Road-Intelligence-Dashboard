import sys
import io
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.main import app
from backend.database.database import Base, get_db
from backend.database.database import engine as production_engine

client = TestClient(app)

def setup_module(module):
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.create_all(bind=production_engine)

def teardown_module(module):
    pass


def test_1_valid_image_and_valid_context():
    """
    Test 1: Valid image upload with valid contextual factor inputs.
    Verifies 200 OK, full pipeline execution, and required response keys.
    """
    image_path = root_dir / "ml" / "datasets" / "roadai_yolo" / "images" / "val" / "India_000052.jpg"
    assert image_path.exists(), f"Sample test image missing at {image_path}"

    with open(image_path, "rb") as f:
        files = {"file": ("India_000052.jpg", f, "image/jpeg")}
        data = {
            "location_risk": "75.0",
            "road_importance": "80.0",
            "traffic": "65.0",
            "complaints": "60.0",
            "historical_recurrence": "40.0"
        }
        res = client.post("/api/v1/analyze", files=files, data=data)

    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    body = res.json()

    # Required JSON schema key verification
    required_keys = [
        "filename", "image_width", "image_height", "detections",
        "severity", "contextual_factors", "priority", "recommendations", "explanation"
    ]
    for key in required_keys:
        assert key in body, f"Missing key '{key}' in AnalysisResponse"

    # Priority score range check (0-100)
    prio_score = body["priority"]["final_priority_score"]
    assert 0.0 <= prio_score <= 100.0, f"Priority score out of bounds: {prio_score}"
    assert body["priority"]["priority_level"] in ["Low", "Moderate", "High", "Critical"]
    assert len(body["recommendations"]) > 0

    print("[PASS] Test 1: Valid image + valid context analysis pipeline test passed.")


def test_2_zero_detections_image():
    """
    Test 2: Image with zero road damage detections.
    Verifies graceful handling (0 severity, valid priority score, clear recommendations).
    """
    # Create a synthetic blank gray image with 0 road damages
    img = Image.new("RGB", (640, 640), color=(128, 128, 128))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()

    files = {"file": ("blank_road.jpg", img_bytes, "image/jpeg")}
    data = {
        "location_risk": "30.0",
        "road_importance": "40.0",
        "traffic": "20.0",
        "complaints": "10.0",
        "historical_recurrence": "0.0"
    }

    res = client.post("/api/v1/analyze", files=files, data=data)
    assert res.status_code == 200
    body = res.json()

    assert body["detections"] == []
    assert body["severity"]["aggregated_severity"] == 0.0
    prio_score = body["priority"]["final_priority_score"]
    assert 0.0 <= prio_score <= 100.0
    assert "No immediate repair needed" in body["recommendations"][0]

    print("[PASS] Test 2: Zero detections image test passed.")


def test_3_invalid_contextual_factor_value():
    """
    Test 3: Invalid contextual factor value outside 0-100 range.
    Verifies HTTP 400 Bad Request error.
    """
    image_path = root_dir / "ml" / "datasets" / "roadai_yolo" / "images" / "val" / "India_000052.jpg"

    with open(image_path, "rb") as f:
        files = {"file": ("test.jpg", f, "image/jpeg")}
        # location_risk = 150.0 (Invalid > 100)
        data = {
            "location_risk": "150.0",
            "road_importance": "50.0",
            "traffic": "50.0",
            "complaints": "50.0",
            "historical_recurrence": "50.0"
        }
        res = client.post("/api/v1/analyze", files=files, data=data)

    assert res.status_code == 400
    assert "Contextual factors must be normalized between 0.0 and 100.0" in res.json()["detail"]

    print("[PASS] Test 3: Invalid contextual factor value test passed.")


def test_4_invalid_image_upload():
    """
    Test 4: Invalid image upload (e.g. non-image file / corrupted file).
    Verifies HTTP 400 Bad Request error.
    """
    fake_file = ("invalid_doc.txt", b"This is not an image file content", "text/plain")
    files = {"file": fake_file}
    data = {
        "location_risk": "50.0",
        "road_importance": "50.0",
        "traffic": "50.0",
        "complaints": "50.0",
        "historical_recurrence": "50.0"
    }

    res = client.post("/api/v1/analyze", files=files, data=data)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"] or "Invalid" in res.json()["detail"]

    print("[PASS] Test 4: Invalid image upload test passed.")


def test_5_priority_score_bounds_and_structure():
    """
    Test 5: Verification of 0-100 priority score bounds and complete response structure.
    """
    image_path = root_dir / "ml" / "datasets" / "roadai_yolo" / "images" / "val" / "India_000053.jpg"

    with open(image_path, "rb") as f:
        files = {"file": ("India_000053.jpg", f, "image/jpeg")}
        data = {
            "location_risk": "100.0",
            "road_importance": "100.0",
            "traffic": "100.0",
            "complaints": "100.0",
            "historical_recurrence": "100.0"
        }
        res = client.post("/api/v1/analyze", files=files, data=data)

    assert res.status_code == 200
    body = res.json()

    assert 0.0 <= body["priority"]["final_priority_score"] <= 100.0
    assert body["priority"]["priority_level"] == "Critical"
    assert "factor_contributions" in body["priority"]
    assert len(body["priority"]["factor_contributions"]) == 6

    print("[PASS] Test 5: Priority score bounds & complete structure verification passed.")



def test_6_oversized_file_rejected():
    """
    Test 6: File larger than the 10 MB upload limit.
    Verifies HTTP 400 Bad Request and the expected error message.
    """
    oversized_bytes = b"0" * (10 * 1024 * 1024 + 1)

    files = {
        "file": ("oversized.jpg", oversized_bytes, "image/jpeg")
    }

    data = {
        "location_risk": "50.0",
        "road_importance": "50.0",
        "traffic": "50.0",
        "complaints": "50.0",
        "historical_recurrence": "50.0"
    }

    res = client.post("/api/v1/analyze", files=files, data=data)

    assert res.status_code == 400
    assert "exceeds the maximum allowed size of 10 MB" in res.json()["detail"]

    print("[PASS] Test 6: Oversized file rejection test passed.")


def run_all_analyze_tests():
    print("==================================================")
    print("   RUNNING ROADAI PHASE 3 ANALYZE API TESTS       ")
    print("==================================================")
    test_1_valid_image_and_valid_context()
    test_2_zero_detections_image()
    test_3_invalid_contextual_factor_value()
    test_4_invalid_image_upload()
    test_5_priority_score_bounds_and_structure()
    print("==================================================")
    print("   ALL PHASE 3 ANALYZE API TESTS PASSED!         ")
    print("==================================================")


if __name__ == "__main__":
    run_all_analyze_tests()






