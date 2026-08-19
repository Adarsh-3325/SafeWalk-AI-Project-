from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SafetyPredictRequest(BaseModel):
    crime_incident_count: int = 0
    crime_density: float = 0.0
    weighted_crime_severity: float = 0.0
    min_dist_recent_crime_m: float = 1000.0
    lighting_score_avg: float = 75.0
    dark_segment_pct: float = 10.0
    crowd_density_avg: float = 50.0
    isolated_segment_pct: float = 10.0
    temp_celsius: float = 20.0
    visibility_km: float = 10.0
    precipitation_mm: float = 0.0
    weather_severity: float = 0.0
    hour_of_day: int = 12
    is_weekend: int = 0
    is_night: int = 0
    is_peak_hour: int = 0
    user_report_count: int = 0
    weighted_user_reports: float = 0.0
    report_density: float = 0.0

class SafetyPredictResponse(BaseModel):
    predicted_risk: float
    safety_score: float
    risk_level: str
    risk_category: str
    crime_risk: float
    lighting_score: float
    crowd_score: float
    weather_risk: float
    time_risk: float
    report_risk: float
    top_risk_factors: List[str]
    positive_factors: List[str]
