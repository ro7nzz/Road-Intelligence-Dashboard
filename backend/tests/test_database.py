import sys
import io
from pathlib import Path
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.main import app
from backend.database.database import Base, get_db
from backend.database.models import AnalysisRecord, DetectionRecord

# Isolated temporary test database engine
TEST_DATABASE_URL = "sqlite:///./backend/tests/test_roadai.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_module(module):
    """Create fresh test tables before running database tests."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def teardown_module(module):
    """Clean up test database file after running tests."""
    Base.metadata.drop_all(bind=test_engine)
    test_db_file = root_dir / "backend" / "tests" / "test_roadai.db"
    if test_db_file.exists():
        try:
            test_db_file.unlink()
        except Exception:
            pass


def test_1_tables_creation_and_persistence():
    """
    Test 1: Table creation and analysis persistence via POST /api/v1/analyze.
    """
    image_path = root_dir / "ml" / "datasets" / "roadai_yolo" / "images" / "val" / "India_000052.jpg"

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

    assert res.status_code == 200
    body = res.json()
    assert body["id"] is not None
    assert body["id"] > 0
    assert body["created_at"] is not None

    print(f"[PASS] Test 1: Analysis persisted with Database ID = {body['id']}.")


def test_2_retrieval_all_analyses():
    """
    Test 2: Retrieve all stored analyses via GET /api/v1/analyses.
    """
    res = client.get("/api/v1/analyses")
    assert res.status_code == 200
    records = res.json()
    assert len(records) >= 1
    assert records[0]["id"] is not None
    assert records[0]["filename"] == "India_000052.jpg"
    print(f"[PASS] Test 2: GET /api/v1/analyses retrieved {len(records)} record(s).")


def test_3_retrieval_by_id_and_detections_integrity():
    """
    Test 3: Retrieve single analysis record by ID via GET /api/v1/analyses/{id}
    and verify detection records & contextual factor integrity.
    """
    res_list = client.get("/api/v1/analyses")
    analysis_id = res_list.json()[0]["id"]

    res_single = client.get(f"/api/v1/analyses/{analysis_id}")
    assert res_single.status_code == 200
    single = res_single.json()

    assert single["id"] == analysis_id
    assert single["contextual_factors"]["location_risk"] == 75.0
    assert single["contextual_factors"]["road_importance"] == 80.0
    assert single["contextual_factors"]["traffic"] == 65.0
    assert single["contextual_factors"]["complaints"] == 60.0
    assert single["contextual_factors"]["historical_recurrence"] == 40.0

    assert single["priority"]["final_priority_score"] == 80.25
    assert single["priority"]["priority_level"] == "Critical"
    assert len(single["detections"]) == 3

    print(f"[PASS] Test 3: GET /api/v1/analyses/{analysis_id} detail & detection integrity verified.")


def test_4_zero_detections_persistence():
    """
    Test 4: Zero-detection image persistence and retrieval.
    """
    img = Image.new("RGB", (500, 500), color=(200, 200, 200))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')

    files = {"file": ("zero_damage.jpg", img_bytes.getvalue(), "image/jpeg")}
    data = {
        "location_risk": "20.0",
        "road_importance": "30.0",
        "traffic": "10.0",
        "complaints": "0.0",
        "historical_recurrence": "0.0"
    }

    res_post = client.post("/api/v1/analyze", files=files, data=data)
    assert res_post.status_code == 200
    zero_id = res_post.json()["id"]

    res_get = client.get(f"/api/v1/analyses/{zero_id}")
    assert res_get.status_code == 200
    body = res_get.json()
    assert body["detections"] == []
    assert body["severity"]["aggregated_severity"] == 0.0

    print(f"[PASS] Test 4: Zero-detection analysis persisted and retrieved with ID = {zero_id}.")


def test_5_not_found_analysis_id():
    """
    Test 5: GET /api/v1/analyses/99999 Returns HTTP 404 Not Found.
    """
    res = client.get("/api/v1/analyses/99999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"]

    print("[PASS] Test 5: Non-existent ID returns HTTP 404 Not Found.")


def run_all_db_tests():
    print("==================================================")
    print("   RUNNING ROADAI PHASE 4 DATABASE TESTS          ")
    print("==================================================")
    setup_module(None)
    try:
        test_1_tables_creation_and_persistence()
        test_2_retrieval_all_analyses()
        test_3_retrieval_by_id_and_detections_integrity()
        test_4_zero_detections_persistence()
        test_5_not_found_analysis_id()
    finally:
        teardown_module(None)
    print("==================================================")
    print("   ALL PHASE 4 DATABASE TESTS PASSED!             ")
    print("==================================================")


if __name__ == "__main__":
    run_all_db_tests()
