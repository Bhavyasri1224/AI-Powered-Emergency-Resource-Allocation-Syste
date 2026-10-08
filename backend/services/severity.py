from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml"))
from predict import predict_severity

DISCLAIMER = "Decision-support only. Final medical and emergency decisions are made by trained personnel."

SYMPTOM_REASONS = {
    "unconscious": "Unconscious patient",
    "severe_bleeding": "Severe bleeding reported",
    "difficulty_breathing": "Difficulty breathing reported",
    "chest_pain": "Chest pain reported",
    "stroke_signs": "Stroke signs reported",
    "burns": "Burn injury reported",
    "fracture": "Possible fracture reported",
}


def estimate_severity(details: dict) -> dict:
    severity, confidence = predict_severity(details)
    reasons = [reason for key, reason in SYMPTOM_REASONS.items() if details.get(key)]
    if details.get("patient_count", 1) > 1:
        reasons.append(f"Multiple patients ({details['patient_count']})")
    if details.get("emergency_type") in ("Heart Emergency", "Stroke"):
        reasons.append(f"Time-sensitive {details['emergency_type'].lower()} indicators")
    if not reasons:
        reasons.append("No severe injury indicators were selected")
    return {"severity": severity, "confidence": confidence, "severity_reasons": reasons[:4], "disclaimer": DISCLAIMER}
