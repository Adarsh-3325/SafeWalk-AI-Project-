from typing import List, Tuple, Optional, Any
from pydantic import BaseModel, Field

class RouteSearchRequest(BaseModel):
    origin: str = Field(..., example="San Francisco Financial District")
    destination: str = Field(..., example="Mission District, San Francisco")
    hour_of_day: Optional[int] = Field(default=14, ge=0, le=23)
    is_weekend: Optional[int] = Field(default=0, ge=0, le=1)

class RouteStepSchema(BaseModel):
    instruction: str
    distance_km: float

class RouteResponseSchema(BaseModel):
    route_id: str
    name: str
    origin_address: str
    destination_address: str
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    distance_km: float
    duration_minutes: float
    geometry: List[Tuple[float, float]]
    steps: List[RouteStepSchema]
    safety_score: float
    risk_level: str
    risk_category: str
    crime_risk: float
    lighting_score: float
    crowd_score: float
    weather_risk: float
    time_risk: float
    report_risk: float
    final_score: float
    top_risk_factors: List[str]
    positive_factors: List[str]
    is_recommended: bool

class SearchResponseSchema(BaseModel):
    recommended_route_id: str
    search_timestamp: str
    demo_mode: bool
    routes: List[RouteResponseSchema]
