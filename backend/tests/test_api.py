from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def sample_request():
    return {"emergency_type": "Road Accident", "age": 34, "patient_count": 2,
            "unconscious": True, "severe_bleeding": True, "difficulty_breathing": False,
            "chest_pain": False, "stroke_signs": False, "burns": False, "fracture": True,
            "conscious_stable": False, "latitude": 40.7128, "longitude": -74.0060,
            "notes": "Demo"}


def test_demo_emergency_full_flow():
    response = client.post("/emergency-response", json=sample_request())
    assert response.status_code == 200
    body = response.json()
    assert body["severity"] == "Critical"
    assert body["recommended_hospital"]
    assert len(body["alternative_hospitals"]) == 2
    assert body["route"]["source"] in ("osrm", "simulated")
    assert body["estimated_travel_time"].endswith("minutes")
    assert "Decision-support only" in body["disclaimer"]


def test_request_validation_rejects_invalid_age():
    payload = sample_request()
    payload["age"] = 200
    assert client.post("/emergency-response", json=payload).status_code == 422
