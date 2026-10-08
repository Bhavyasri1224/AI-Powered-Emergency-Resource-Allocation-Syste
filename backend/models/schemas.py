from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

EmergencyType = Literal["Road Accident", "Heart Emergency", "Stroke", "Fire/Disaster", "Other"]
Severity = Literal["Critical", "High", "Medium"]


class EmergencyRequest(BaseModel):
    emergency_type: EmergencyType
    age: int = Field(ge=0, le=120)
    patient_count: int = Field(ge=1, le=100)
    unconscious: bool = False
    severe_bleeding: bool = False
    difficulty_breathing: bool = False
    chest_pain: bool = False
    stroke_signs: bool = False
    burns: bool = False
    fracture: bool = False
    conscious_stable: bool = False
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    emergency_time: datetime | None = None
    notes: str = Field(default="", max_length=1000)


class SeverityResponse(BaseModel):
    severity: Severity
    confidence: float = Field(ge=0, le=1)
    severity_reasons: list[str]
    disclaimer: str


class ScoreBreakdown(BaseModel):
    distance: float
    icu_availability: float
    bed_availability: float
    specialization_match: float
    patient_load: float
    emergency_support: float


class HospitalRecommendation(BaseModel):
    name: str
    latitude: float
    longitude: float
    distance_km: float
    icu_available: bool
    icu_beds: int
    available_beds: int
    current_patient_load: int
    specializations: list[str]
    score: float
    score_breakdown: ScoreBreakdown
    reasons: list[str]


class HospitalResponse(BaseModel):
    hospitals: list[HospitalRecommendation]
    recommended_hospital: HospitalRecommendation | None
    message: str | None = None


class RouteRequest(BaseModel):
    origin_latitude: float = Field(ge=-90, le=90)
    origin_longitude: float = Field(ge=-180, le=180)
    destination_latitude: float = Field(ge=-90, le=90)
    destination_longitude: float = Field(ge=-180, le=180)


class RouteResponse(BaseModel):
    geometry: list[list[float]]
    distance_km: float
    duration_min: float
    source: Literal["osrm", "simulated"]
    label: Literal["OSRM route", "Simulated route"]
    traffic: str


class EmergencyResponse(BaseModel):
    emergency_type: EmergencyType
    severity: Severity
    confidence: float
    severity_reasons: list[str]
    recommended_hospital: HospitalRecommendation | None
    alternative_hospitals: list[HospitalRecommendation]
    route: RouteResponse | None
    estimated_travel_time: str | None
    disclaimer: str
    data_label: str = "Simulated/sample data"
    message: str | None = None
