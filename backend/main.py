from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.db import initialize_database, list_hospitals
from backend.models.schemas import (EmergencyRequest, EmergencyResponse, HospitalResponse,
                                    RouteRequest, RouteResponse, SeverityResponse)
from backend.services.ranking import rank_hospitals
from backend.services.routing import calculate_route
from backend.services.severity import DISCLAIMER, estimate_severity


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="AI-Powered Emergency Resource Allocation System",
    description="Decision-support prototype using simulated/sample emergency and hospital data.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def request_details(request: EmergencyRequest) -> dict:
    return request.model_dump(exclude={"latitude", "longitude", "emergency_time", "notes"})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "data": "simulated/sample", "model": "Random Forest or best evaluated model"}


@app.get("/hospitals")
def get_hospitals() -> list[dict]:
    return list_hospitals()


@app.post("/predict-severity", response_model=SeverityResponse)
def predict_severity_endpoint(request: EmergencyRequest) -> dict:
    return estimate_severity(request_details(request))


@app.post("/recommend-hospital", response_model=HospitalResponse)
def recommend_hospital_endpoint(request: EmergencyRequest) -> dict:
    severity = estimate_severity(request_details(request))["severity"]
    ranked = rank_hospitals(list_hospitals(), request.latitude, request.longitude,
                            request.emergency_type, severity, request.patient_count)
    return {**ranked, "message": ranked.get("message")}


@app.post("/calculate-route", response_model=RouteResponse)
def calculate_route_endpoint(request: RouteRequest) -> dict:
    return calculate_route(request.origin_latitude, request.origin_longitude,
                           request.destination_latitude, request.destination_longitude)


@app.post("/emergency-response", response_model=EmergencyResponse)
def emergency_response(request: EmergencyRequest) -> dict:
    prediction = estimate_severity(request_details(request))
    hospitals = rank_hospitals(list_hospitals(), request.latitude, request.longitude,
                               request.emergency_type, prediction["severity"], request.patient_count)
    recommended = hospitals["recommended_hospital"]
    route = None
    travel_time = None
    if recommended:
        route = calculate_route(request.latitude, request.longitude,
                                recommended["latitude"], recommended["longitude"])
        travel_time = f"{route['duration_min']} minutes"
    return {
        "emergency_type": request.emergency_type,
        **prediction,
        "recommended_hospital": recommended,
        "alternative_hospitals": hospitals["hospitals"][1:],
        "route": route,
        "estimated_travel_time": travel_time,
        "disclaimer": DISCLAIMER,
        "message": hospitals.get("message"),
    }
