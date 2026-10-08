"""Generate synthetic triage data, compare models, and save the best pipeline."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib

ROOT = Path(__file__).resolve().parent
DATASET_PATH = ROOT / "dataset.csv"
MODEL_PATH = ROOT / "model.pkl"
METRICS_PATH = ROOT / "metrics.json"
SEVERITIES = ("Medium", "High", "Critical")
EMERGENCY_TYPES = ("Road Accident", "Heart Emergency", "Stroke", "Fire/Disaster", "Other")
SYMPTOMS = ("unconscious", "severe_bleeding", "difficulty_breathing", "chest_pain", "stroke_signs", "burns", "fracture", "conscious_stable")
NUMERIC_FEATURES = ("age", "patient_count", *SYMPTOMS)
FEATURES = ("emergency_type", *NUMERIC_FEATURES)


def risk_score(row: dict) -> float:
    score = sum(row[symptom] * points for symptom, points in {
        "unconscious": 3, "severe_bleeding": 3, "difficulty_breathing": 3,
        "chest_pain": 2, "stroke_signs": 3, "burns": 2, "fracture": 1,
    }.items())
    score += 1 if row["emergency_type"] in ("Heart Emergency", "Stroke") else 0
    score += 1 if row["patient_count"] >= 3 else 0
    score += 0.5 if row["age"] < 5 or row["age"] >= 70 else 0
    score -= 1 if row["conscious_stable"] and score == 0 else 0
    return score


def rule_severity(row: dict) -> str:
    score = risk_score(row)
    return "Critical" if score >= 5 else "High" if score >= 2.5 else "Medium"


def generate_dataset(rows_per_class: int = 600, seed: int = 41) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    attempts = 0
    while min(sum(row["severity"] == severity for row in rows) for severity in SEVERITIES) < rows_per_class:
        attempts += 1
        if attempts > rows_per_class * 200:
            raise RuntimeError("Could not generate balanced synthetic samples")
        row = {
            "emergency_type": str(rng.choice(EMERGENCY_TYPES)),
            "age": int(rng.integers(1, 96)),
            "patient_count": int(rng.choice([1, 1, 1, 2, 2, 3, 4])),
            **{symptom: int(rng.random() < 0.23) for symptom in SYMPTOMS},
        }
        severity = rule_severity(row)
        if sum(item["severity"] == severity for item in rows) >= rows_per_class:
            continue
        row["severity"] = severity
        rows.append(row)

    # A small adjacent-class label perturbation keeps the training task realistic.
    for index in rng.choice(len(rows), size=max(1, int(len(rows) * 0.035)), replace=False):
        current = rows[index]["severity"]
        neighbor = {"Medium": "High", "High": "Critical", "Critical": "High"}[current]
        rows[index]["severity"] = neighbor
    return pd.DataFrame(rows).sample(frac=1, random_state=seed).reset_index(drop=True)


def make_pipeline(estimator) -> Pipeline:
    transformer = ColumnTransformer([
        ("type", OneHotEncoder(handle_unknown="ignore"), ["emergency_type"]),
        ("numeric", StandardScaler(), list(NUMERIC_FEATURES)),
    ])
    return Pipeline([("features", transformer), ("classifier", estimator)])


def main() -> None:
    data = generate_dataset()
    data.to_csv(DATASET_PATH, index=False)
    x_train, x_test, y_train, y_test = train_test_split(
        data[list(FEATURES)], data["severity"], test_size=0.2, random_state=41, stratify=data["severity"]
    )
    candidates = {
        "Random Forest": make_pipeline(RandomForestClassifier(
            n_estimators=260, min_samples_leaf=2, class_weight="balanced", random_state=41
        )),
        "Logistic Regression": make_pipeline(LogisticRegression(
            max_iter=1500, class_weight="balanced", random_state=41
        )),
    }
    reports = {}
    best_name = ""
    best_pipeline = None
    best_f1 = -1.0
    for name, pipeline in candidates.items():
        pipeline.fit(x_train, y_train)
        predicted = pipeline.predict(x_test)
        report = classification_report(y_test, predicted, labels=list(SEVERITIES), output_dict=True, zero_division=0)
        reports[name] = {
            "accuracy": round(float(accuracy_score(y_test, predicted)), 4),
            "precision_macro": round(float(report["macro avg"]["precision"]), 4),
            "recall_macro": round(float(report["macro avg"]["recall"]), 4),
            "f1_macro": round(float(report["macro avg"]["f1-score"]), 4),
            "confusion_matrix_labels": list(SEVERITIES),
            "confusion_matrix": confusion_matrix(y_test, predicted, labels=list(SEVERITIES)).tolist(),
        }
        print(f"{name}: accuracy={reports[name]['accuracy']:.3f}, precision={reports[name]['precision_macro']:.3f}, "
              f"recall={reports[name]['recall_macro']:.3f}, F1={reports[name]['f1_macro']:.3f}")
        print("Confusion matrix (Medium, High, Critical):")
        print(np.array(reports[name]["confusion_matrix"]))
        if reports[name]["f1_macro"] > best_f1:
            best_f1 = reports[name]["f1_macro"]
            best_name = name
            best_pipeline = pipeline
    joblib.dump(best_pipeline, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps({"selected_model": best_name, "rows": len(data), "class_counts": data["severity"].value_counts().to_dict(), "models": reports}, indent=2))
    print(f"Saved {best_name} to {MODEL_PATH.name}; generated {len(data)} synthetic rows.")


if __name__ == "__main__":
    main()
