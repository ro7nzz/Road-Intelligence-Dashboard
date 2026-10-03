from typing import List
from backend.config import settings
from backend.schemas.detection import DetectionItem
from backend.schemas.priority import (
    ContextualFactors,
    DetectionSeverityItem,
    SeverityResult,
    FactorContribution,
    PriorityResult,
)


def calculate_damage_severity(
    detections: List[DetectionItem],
    image_width: int,
    image_height: int
) -> SeverityResult:
    """
    Computes deterministic, explainable damage severity from YOLO detections.
    Considers damage class baseline weight and relative bounding-box area ratio.
    """
    if not detections:
        return SeverityResult(
            aggregated_severity=0.0,
            detections_severity=[],
            explanation="No road damage detected in image. Aggregated damage severity score is 0.0."
        )

    image_area = max(1, image_width * image_height)
    detections_severity = []
    explanation_parts = []

    for i, det in enumerate(detections, 1):
        box_width = max(0.0, det.box.x_max - det.box.x_min)
        box_height = max(0.0, det.box.y_max - det.box.y_min)
        box_area = box_width * box_height
        box_area_ratio = (box_area / image_area) * 100.0  # percentage

        base_sev = settings.class_severity_base.get(det.class_id, 40.0)
        # Area multiplier scaling factor (up to 2.0x for large damaged areas)
        area_multiplier = 1.0 + min(1.0, (box_area / image_area) * 5.0)
        calculated_sev = min(100.0, round(base_sev * area_multiplier, 2))

        item_explanation = (
            f"Detection #{i} [{det.class_name}]: Base severity {base_sev:.1f}, "
            f"box area ratio {box_area_ratio:.2f}% (multiplier {area_multiplier:.2f}x) "
            f"-> item severity = {calculated_sev:.2f}. Model confidence = {det.confidence:.4f}."
        )

        detections_severity.append(
            DetectionSeverityItem(
                class_id=det.class_id,
                class_name=det.class_name,
                confidence=det.confidence,
                box_area_ratio=round(box_area_ratio, 4),
                base_severity=base_sev,
                calculated_severity=calculated_sev,
                explanation=item_explanation
            )
        )
        explanation_parts.append(item_explanation)

    # Aggregate overall image severity
    max_severity = max(item.calculated_severity for item in detections_severity)
    count_bonus = min(20.0, (len(detections_severity) - 1) * 5.0)
    aggregated_sev = min(100.0, round(max_severity + count_bonus, 2))

    summary_explanation = (
        f"Aggregated Damage Severity: {aggregated_sev:.2f}/100. "
        f"Based on highest detection severity ({max_severity:.2f}) "
        f"plus multi-damage density adjustment (+{count_bonus:.2f} for {len(detections_severity)} total detections). "
        + " | ".join(explanation_parts)
    )

    return SeverityResult(
        aggregated_severity=aggregated_sev,
        detections_severity=detections_severity,
        explanation=summary_explanation
    )


def classify_priority_level(score: float) -> str:
    """
    Maps 0-100 score to RoadAI priority level.
    """
    if score < 25.0:
        return "Low"
    elif score < 50.0:
        return "Moderate"
    elif score < 75.0:
        return "High"
    else:
        return "Critical"


def generate_repair_recommendations(
    detections: List[DetectionItem],
    severity_score: float,
    priority_score: float,
    priority_level: str
) -> List[str]:
    """
    Generates deterministic, actionable repair recommendations based on
    detected damage types, severity score, and final priority level.
    """
    if not detections or severity_score == 0.0:
        return ["No immediate repair needed. Schedule routine road condition monitoring."]

    recommendations = []
    class_ids = {det.class_id for det in detections}

    # Pothole recommendations (Class 3)
    if 3 in class_ids:
        if priority_level in ["High", "Critical"]:
            recommendations.append("Urgent pothole patching & deep asphalt filling required.")
            recommendations.append("Deploy temporary hazard warning markers immediately.")
        else:
            recommendations.append("Standard pothole cold-mix/hot-mix patching recommended.")

    # Alligator Crack recommendations (Class 2)
    if 2 in class_ids:
        if priority_level in ["High", "Critical"]:
            recommendations.append("Full-depth localized pavement patching or section resurfacing required.")
        else:
            recommendations.append("Localized skin patching or crack sealing recommended.")

    # Longitudinal / Transverse Crack recommendations (Class 0 & 1)
    if 0 in class_ids or 1 in class_ids:
        recommendations.append("Bituminous crack sealing and joint filling recommended to prevent water ingress.")

    # General Priority Level recommendations
    if priority_level == "Critical":
        recommendations.append("Schedule high-priority site inspection within 24-48 hours.")
    elif priority_level == "High":
        recommendations.append("Schedule maintenance crew inspection within 1 week.")

    return list(dict.fromkeys(recommendations))  # Preserve order without duplicates


def calculate_repair_priority(
    severity_score: float,
    contextual: ContextualFactors,
    detections: List[DetectionItem] = None
) -> PriorityResult:
    """
    Computes the deterministic, explainable 0-100 Repair Priority Score.
    Integrates 6 factors with configurable weights from settings.
    """
    weights = settings.priority_weights

    factor_scores = {
        "damage_severity": round(max(0.0, min(100.0, severity_score)), 2),
        "location_risk": round(max(0.0, min(100.0, contextual.location_risk)), 2),
        "road_importance": round(max(0.0, min(100.0, contextual.road_importance)), 2),
        "traffic": round(max(0.0, min(100.0, contextual.traffic)), 2),
        "complaints": round(max(0.0, min(100.0, contextual.complaints)), 2),
        "historical_recurrence": round(max(0.0, min(100.0, contextual.historical_recurrence)), 2),
    }

    contributions = []
    weighted_sum = 0.0
    explanation_parts = []

    for factor_name, score in factor_scores.items():
        weight = weights.get(factor_name, 0.0)
        contrib = round(score * weight, 4)
        weighted_sum += contrib

        contributions.append(
            FactorContribution(
                factor_name=factor_name,
                score=score,
                weight=weight,
                contribution=round(contrib, 2)
            )
        )
        explanation_parts.append(
            f"{factor_name.replace('_', ' ').title()} ({score:.1f} × {weight:.2f} = {contrib:.2f})"
        )

    final_score = min(100.0, max(0.0, round(weighted_sum, 2)))
    level = classify_priority_level(final_score)

    recommendations = generate_repair_recommendations(
        detections=detections or [],
        severity_score=severity_score,
        priority_score=final_score,
        priority_level=level
    )

    explanation = (
        f"Final Repair Priority Score: {final_score:.2f}/100 [{level} Level]. "
        f"Weighted Sum = " + " + ".join(explanation_parts) + f" = {final_score:.2f}."
    )

    return PriorityResult(
        final_priority_score=final_score,
        priority_level=level,
        factor_scores=factor_scores,
        factor_contributions=contributions,
        recommendations=recommendations,
        explanation=explanation
    )
