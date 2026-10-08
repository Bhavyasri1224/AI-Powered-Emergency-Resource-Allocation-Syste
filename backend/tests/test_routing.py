from backend.services import routing


def test_osrm_failure_uses_explicit_simulated_route(monkeypatch):
    def fail_request(*args, **kwargs):
        raise routing.requests.Timeout("offline")

    monkeypatch.setattr(routing.requests, "get", fail_request)
    result = routing.calculate_route(40.7128, -74.006, 40.7165, -74.0038)
    assert result["source"] == "simulated"
    assert result["label"] == "Simulated route"
    assert len(result["geometry"]) >= 2
    assert result["distance_km"] > 0
    assert result["traffic"] == "not available (estimate based on distance/average speed)"
