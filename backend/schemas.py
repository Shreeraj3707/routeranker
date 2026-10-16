"""
Pydantic schemas — request/response shapes for the API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RouteFeatures(BaseModel):
    """Input for /predict — the feature vector for a single route."""
    trip_count: int = Field(..., ge=0)
    unique_stops: int = Field(..., ge=0)
    avg_duration_sec: float = Field(..., ge=0)
    peak_ratio: float = Field(..., ge=0)
    weekday_score: float = Field(..., ge=0)
    route_length_km: float = Field(..., ge=0)
    trips_hour_00: int = 0
    trips_hour_01: int = 0
    trips_hour_02: int = 0
    trips_hour_03: int = 0
    trips_hour_04: int = 0
    trips_hour_05: int = 0
    trips_hour_06: int = 0
    trips_hour_07: int = 0
    trips_hour_08: int = 0
    trips_hour_09: int = 0
    trips_hour_10: int = 0
    trips_hour_11: int = 0
    trips_hour_12: int = 0
    trips_hour_13: int = 0
    trips_hour_14: int = 0
    trips_hour_15: int = 0
    trips_hour_16: int = 0
    trips_hour_17: int = 0
    trips_hour_18: int = 0
    trips_hour_19: int = 0
    trips_hour_20: int = 0
    trips_hour_21: int = 0
    trips_hour_22: int = 0
    trips_hour_23: int = 0
    route_type: int = 3


class PredictionResponse(BaseModel):
    route_id: Optional[str] = None
    performance: str
    cluster: int
    suggestions: List[str] = []


class RouteSummary(BaseModel):
    route_id: str
    performance: str
    cluster: int
    trip_count: Optional[int] = None
    unique_stops: Optional[int] = None
    route_length_km: Optional[float] = None