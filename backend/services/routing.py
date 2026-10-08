from __future__ import annotations

import math

import requests

TRAFFIC_STATUS = "not available (estimate based on distance/average speed)"


def simulated_route(origin_latitude: float, origin_longitude: float,
                    destination_latitude: float, destination_longitude: float) -> dict:
    points = []
    for fraction in (0, 0.25, 0.5, 0.75, 1):
        lat = origin_latitude + (destination_latitude - origin_latitude) * fraction
        lon = origin_longitude + (destination_longitude - origin_longitude) * fraction
        bend = math.sin(math.pi * fraction) * 0.0018
        points.append([lat + bend, lon - bend])
    from .ranking import haversine_km
    distance = haversine_km(origin_latitude, origin_longitude, destination_latitude, destination_longitude) * 1.28
    duration = max(1, distance / 28 * 60)
    return {"geometry": points, "distance_km": round(distance, 1), "duration_min": round(duration),
            "source": "simulated", "label": "Simulated route", "traffic": TRAFFIC_STATUS}


def calculate_route(origin_latitude: float, origin_longitude: float,
                    destination_latitude: float, destination_longitude: float, timeout: float = 2.5) -> dict:
    url = (f"https://router.project-osrm.org/route/v1/driving/{origin_longitude},{origin_latitude};"
           f"{destination_longitude},{destination_latitude}?overview=full&geometries=geojson")
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        route = response.json()["routes"][0]
        geometry = [[latitude, longitude] for longitude, latitude in route["geometry"]["coordinates"]]
        if not geometry:
            raise ValueError("OSRM returned no route geometry")
        return {"geometry": geometry, "distance_km": round(route["distance"] / 1000, 1),
                "duration_min": round(route["duration"] / 60), "source": "osrm", "label": "OSRM route",
                "traffic": TRAFFIC_STATUS}
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return simulated_route(origin_latitude, origin_longitude, destination_latitude, destination_longitude)
