import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.schemas.detection import DetectionItem, BoundingBox
from backend.schemas.priority import ContextualFactors
from backend.services.priority_service import (
    calculate_damage_severity,
    calculate_repair_priority,
    classify_priority_level,
    generate_repair_recommendations,
)


def test_1_severity_calculation():
    """
    Test 1: Damage Severity Calculation with different classes and bounding box areas.
    """
    # Sample detections
    detections = [
        DetectionItem(
            class_id=3,
            class_name="D40_Pothole",
            confidence=0.85,
            box=BoundingBox(x_min=100, y_min=100, x_max=300, y_max=300)  # 200x200 = 40,000 px^2
        ),
        DetectionItem(
            class_id=0,
            class_name="D00_Longitudinal_Crack",
            confidence=0.92,
            box=BoundingBox(x_min=50, y_min=50, x_max=150, y_max=100)   # 100x50 = 5,000 px^2
        )
    ]

    image_width = 1000
    image_height = 1000  # Total image area = 1,000,000 px^2

    sev_result = calculate_damage_severity(detections, image_width, image_height)

    assert sev_result.aggregated_severity > 0.0
    assert len(sev_result.detections_severity) == 2
    # Verify confidence remains separate
    assert sev_result.detections_severity[0].confidence == 0.85
    assert sev_result.detections_severity[0].base_severity == 85.0  # Pothole base
    assert sev_result.detections_severity[1].base_severity == 40.0  # Longitudinal crack base
    print("[PASS] Test 1: Severity calculation & base weight verification passed.")


def test_2_factor_normalization():
    """
    Test 2: Factor Normalization & Schema Validation (0-100 clamping).
    """
    contextual = ContextualFactors(
        location_risk=80.0,
        road_importance=90.0,
        traffic=70.0,
        complaints=50.0,
        historical_recurrence=60.0
    )

    assert contextual.location_risk == 80.0
    assert contextual.road_importance == 90.0
    assert contextual.traffic == 70.0
    assert contextual.complaints == 50.0
    assert contextual.historical_recurrence == 60.0
    print("[PASS] Test 2: Factor normalization passed.")


def test_3_weighted_priority_calculation():
    """
    Test 3: Weighted Priority Score Calculation & Factor Contributions.
    Weights: Severity=40%, Location=10%, Road=20%, Traffic=15%, Complaints=5%, Recurrence=10%
    """
    severity_score = 100.0  # 100 * 0.40 = 40.0
    contextual = ContextualFactors(
        location_risk=50.0,            # 50 * 0.10 = 5.0
        road_importance=50.0,          # 50 * 0.20 = 10.0
        traffic=50.0,                  # 50 * 0.15 = 7.5
        complaints=50.0,               # 50 * 0.05 = 2.5
        historical_recurrence=50.0     # 50 * 0.10 = 5.0
    )
    # Expected Total = 40.0 + 5.0 + 10.0 + 7.5 + 2.5 + 5.0 = 70.0

    priority_result = calculate_repair_priority(severity_score, contextual)

    assert priority_result.final_priority_score == 70.0
    assert priority_result.priority_level == "High"
    assert len(priority_result.factor_contributions) == 6
    print("[PASS] Test 3: Weighted priority score & contributions calculation passed.")


def test_4_priority_level_classification():
    """
    Test 4: Priority Level Classification Thresholds.
    0-24 = Low, 25-49 = Moderate, 50-74 = High, 75-100 = Critical.
    """
    assert classify_priority_level(10.0) == "Low"
    assert classify_priority_level(24.9) == "Low"
    assert classify_priority_level(25.0) == "Moderate"
    assert classify_priority_level(49.9) == "Moderate"
    assert classify_priority_level(50.0) == "High"
    assert classify_priority_level(74.9) == "High"
    assert classify_priority_level(75.0) == "Critical"
    assert classify_priority_level(100.0) == "Critical"
    print("[PASS] Test 4: Priority level classification thresholds passed.")


def test_5_recommendation_generation():
    """
    Test 5: Repair Recommendation Generation based on damage type and priority level.
    """
    pothole_det = [
        DetectionItem(
            class_id=3,
            class_name="D40_Pothole",
            confidence=0.88,
            box=BoundingBox(x_min=100, y_min=100, x_max=200, y_max=200)
        )
    ]

    recs_critical = generate_repair_recommendations(
        detections=pothole_det,
        severity_score=85.0,
        priority_score=88.0,
        priority_level="Critical"
    )

    assert any("Urgent pothole patching" in r for r in recs_critical)
    assert any("Schedule high-priority site inspection" in r for r in recs_critical)
    print("[PASS] Test 5: Recommendation generation passed.")


def test_6_edge_cases():
    """
    Test 6: Edge Cases (Zero Detections & Maximum Inputs 100/100).
    """
    # Edge Case A: Zero Detections & Zero Contextual Factors
    zero_sev = calculate_damage_severity([], 1000, 1000)
    assert zero_sev.aggregated_severity == 0.0
    zero_context = ContextualFactors()
    zero_priority = calculate_repair_priority(zero_sev.aggregated_severity, zero_context)
    assert zero_priority.final_priority_score == 0.0
    assert zero_priority.priority_level == "Low"

    # Edge Case B: Maximum Inputs (100/100 for all factors)
    max_context = ContextualFactors(
        location_risk=100.0,
        road_importance=100.0,
        traffic=100.0,
        complaints=100.0,
        historical_recurrence=100.0
    )
    max_priority = calculate_repair_priority(100.0, max_context)
    assert max_priority.final_priority_score == 100.0
    assert max_priority.priority_level == "Critical"
    print("[PASS] Test 6: Edge cases (zero detections & max inputs) passed.")


def run_all_tests():
    print("==================================================")
    print("   RUNNING ROADAI PHASE 2 PRIORITY ENGINE TESTS   ")
    print("==================================================")
    test_1_severity_calculation()
    test_2_factor_normalization()
    test_3_weighted_priority_calculation()
    test_4_priority_level_classification()
    test_5_recommendation_generation()
    test_6_edge_cases()
    print("==================================================")
    print("   ALL PHASE 2 PRIORITY ENGINE TESTS PASSED!      ")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
