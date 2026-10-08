from backend.services.ranking import rank_hospitals


def hospital(name, lat, lon, icu, beds, specialties, load=40, support=1):
    return {"hospital_name": name, "latitude": lat, "longitude": lon,
            "available_beds": beds, "icu_beds": icu, "specializations": specialties,
            "current_patient_load": load, "emergency_support": support}


def test_critical_ranks_capability_over_nearest_and_excludes_no_icu():
    candidates = [
        hospital("Nearest general", 40.001, -74, 0, 20, "general"),
        hospital("Trauma centre", 40.04, -74, 6, 20, "trauma"),
    ]
    result = rank_hospitals(candidates, 40, -74, "Road Accident", "Critical", 2)
    assert result["recommended_hospital"]["name"] == "Trauma centre"
    assert all(entry["name"] != "Nearest general" for entry in result["hospitals"])
    assert result["recommended_hospital"]["score_breakdown"]["specialization_match"] == 100


def test_multiple_patients_requires_enough_beds():
    result = rank_hospitals([hospital("Too small", 40, -74, 4, 1, "trauma")],
                            40, -74, "Road Accident", "Critical", 2)
    assert result["recommended_hospital"] is None
    assert "No suitable hospital" in result["message"]


def test_emergency_type_changes_specialty_ranking():
    candidates = [hospital("Trauma", 40.01, -74, 3, 10, "trauma"),
                  hospital("Cardiac", 40.01, -74, 3, 10, "cardiac")]
    road = rank_hospitals(candidates, 40, -74, "Road Accident", "High", 1)
    heart = rank_hospitals(candidates, 40, -74, "Heart Emergency", "High", 1)
    assert road["recommended_hospital"]["name"] == "Trauma"
    assert heart["recommended_hospital"]["name"] == "Cardiac"
