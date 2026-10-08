"""Small inference entry point for the saved severity pipeline."""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().with_name("model.pkl")
FEATURES = ["emergency_type", "age", "patient_count", "unconscious", "severe_bleeding",
            "difficulty_breathing", "chest_pain", "stroke_signs", "burns", "fracture", "conscious_stable"]


def predict_severity(details: dict) -> tuple[str, float]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Severity model is missing. Run: python ml/train.py")
    row = {feature: details.get(feature, 0) for feature in FEATURES}
    row["emergency_type"] = details.get("emergency_type", "Other")
    model = joblib.load(MODEL_PATH)
    probabilities = model.predict_proba(pd.DataFrame([row], columns=FEATURES))[0]
    class_index = int(probabilities.argmax())
    return str(model.classes_[class_index]), float(probabilities[class_index])


if __name__ == "__main__":
    demo = {"emergency_type": "Road Accident", "age": 34, "patient_count": 2,
            "unconscious": 1, "severe_bleeding": 1, "difficulty_breathing": 0,
            "chest_pain": 0, "stroke_signs": 0, "burns": 0, "fracture": 1, "conscious_stable": 0}
    severity, confidence = predict_severity(demo)
    print(f"Severity: {severity}, Confidence: {confidence:.0%}")
