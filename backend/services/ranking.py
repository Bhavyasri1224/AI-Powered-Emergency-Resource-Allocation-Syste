from __future__ import annotations

import math

SPECIALIZATION_MAP = {
    "Road Accident": "trauma",
    "Heart Emergency": "cardiac",
    "Stroke": "stroke",
    "Fire/Disaster": "burns",
    "Other": "general",
}
WEIGHTS = {
    "Critical": {"distance": 0.12, "icu_availability": 0.28, "bed_availability": 0.12, "specialization_match": 0.23, "patient_load": 0.10, "emergency_support": 0.15},
    "High": {"distance": 0.20, "icu_availability": 0.20, "bed_availability": 0.17, "specialization_match": 0.18, "patient_load": 0.12, "emergency_support": 0.13},
    "Medium": {"distance": 0.30, "icu_availability": 0.08, "bed_availability": 0.20, "specialization_match": 0.14, "patient_load": 0.15, "emergency_support": 0.13},
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi, delta_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    value = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def normalize(values: list[float], higher_is_better: bool = True) -> list[float]:
    low, high = min(values), max(values)
    if math.isclose(low, high):
        return [1.0] * len(values)
    scores = [(value - low) / (high - low) for value in values]
    return scores if higher_is_better else [1 - score for score in scores]


def rank_hospitals(hospitals: list[dict], latitude: float, longitude: float, emergency_type: str,
                   severity: str, patient_count: int) -> dict:
    suitable = [hospital for hospital in hospitals
                if hospital["available_beds"] >= patient_count
                and not (severity == "Critical" and hospital["icu_beds"] <= 0)]
    if not suitable:
        return {"hospitals": [], "recommended_hospital": None,
                "message": "No suitable hospital has enough beds and required critical-care capacity. Trained dispatch personnel must choose an alternative."}

    distances = [haversine_km(latitude, longitude, h["latitude"], h["longitude"]) for h in suitable]
    weights = WEIGHTS[severity]
    distance_scores = normalize(distances, higher_is_better=False)
    icu_scores = normalize([h["icu_beds"] for h in suitable])
    bed_scores = normalize([h["available_beds"] for h in suitable])
    specialization = SPECIALIZATION_MAP[emergency_type]
    specialization_scores = [1.0 if specialization in h["specializations"].split("|") else 0.0 for h in suitable]
    load_scores = normalize([h["current_patient_load"] for h in suitable], higher_is_better=False)
    support_scores = [float(h["emergency_support"]) for h in suitable]
    factors = [distance_scores, icu_scores, bed_scores, specialization_scores, load_scores, support_scores]
    factor_names = list(weights)
    ranked = []
    for index, hospital in enumerate(suitable):
        breakdown = {name: round(factors[position][index] * 100, 1) for position, name in enumerate(factor_names)}
        score = round(sum(factors[position][index] * weights[name] for position, name in enumerate(factor_names)) * 100, 1)
        reasons = []
        if hospital["icu_beds"] > 0:
            reasons.append(f"{hospital['icu_beds']} ICU beds available")
        if specialization in hospital["specializations"].split("|"):
            reasons.append(f"{specialization.title()} specialization match")
        if hospital["current_patient_load"] <= 45:
            reasons.append("Relatively low current patient load")
        reasons.append(f"{distances[index]:.1f} km estimated straight-line distance")
        if hospital["available_beds"] >= patient_count:
            reasons.append(f"Capacity for {patient_count} patient{'s' if patient_count != 1 else ''}")
        ranked.append({
            "name": hospital["hospital_name"], "latitude": hospital["latitude"], "longitude": hospital["longitude"],
            "distance_km": round(distances[index], 1), "icu_available": hospital["icu_beds"] > 0,
            "icu_beds": hospital["icu_beds"], "available_beds": hospital["available_beds"],
            "current_patient_load": hospital["current_patient_load"],
            "specializations": hospital["specializations"].split("|"), "score": score,
            "score_breakdown": breakdown, "reasons": reasons[:4],
        })
    ranked.sort(key=lambda entry: entry["score"], reverse=True)
    return {"hospitals": ranked[:3], "recommended_hospital": ranked[0]}
