from typing import List, Dict, Any
from backend.app.core.config import settings

class RouteRankingService:
    """
    Ranks alternative routes using configurable multi-attribute scoring.
    Formula:
      FINAL_SCORE = w_safety * safety_score + w_time * normalized_time_score + w_dist * normalized_dist_score
    Higher score indicates a better overall route recommendation.
    """
    def __init__(
        self,
        safety_weight: float = None,
        time_weight: float = None,
        distance_weight: float = None
    ):
        self.w_safety = safety_weight if safety_weight is not None else settings.SAFETY_WEIGHT
        self.w_time = time_weight if time_weight is not None else settings.TIME_WEIGHT
        self.w_dist = distance_weight if distance_weight is not None else settings.DISTANCE_WEIGHT

    def rank_routes(self, routes_with_predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not routes_with_predictions:
            return []

        # Find min time and min distance for normalization
        min_duration = min(r["duration_minutes"] for r in routes_with_predictions)
        min_distance = min(r["distance_km"] for r in routes_with_predictions)

        scored_routes = []
        for r in routes_with_predictions:
            safety_score = r["pred"]["safety_score"]
            duration_minutes = max(r["duration_minutes"], 0.1)
            distance_km = max(r["distance_km"], 0.1)

            # Time and distance scores (100 is best / shortest)
            time_score = 100.0 * (min_duration / duration_minutes)
            dist_score = 100.0 * (min_distance / distance_km)

            final_score = round(
                self.w_safety * safety_score +
                self.w_time * time_score +
                self.w_dist * dist_score,
                1
            )

            route_item = {
                "route_id": r["route_id"],
                "name": r.get("name", r["route_id"]),
                "origin_address": r["origin_address"],
                "destination_address": r["destination_address"],
                "origin_lat": r.get("origin_lat", r["geometry"][0][0] if r.get("geometry") else 0.0),
                "origin_lng": r.get("origin_lng", r["geometry"][0][1] if r.get("geometry") else 0.0),
                "dest_lat": r.get("dest_lat", r["geometry"][-1][0] if r.get("geometry") else 0.0),
                "dest_lng": r.get("dest_lng", r["geometry"][-1][1] if r.get("geometry") else 0.0),
                "distance_km": r["distance_km"],
                "duration_minutes": r["duration_minutes"],
                "geometry": r["geometry"],
                "steps": r.get("steps", []),
                "safety_score": safety_score,
                "risk_level": r["pred"]["risk_level"],
                "risk_category": r["pred"]["risk_category"],
                "crime_risk": r["pred"]["crime_risk"],
                "lighting_score": r["pred"]["lighting_score"],
                "crowd_score": r["pred"]["crowd_score"],
                "weather_risk": r["pred"]["weather_risk"],
                "time_risk": r["pred"]["time_risk"],
                "report_risk": r["pred"]["report_risk"],
                "final_score": final_score,
                "top_risk_factors": r["pred"]["top_risk_factors"],
                "positive_factors": r["pred"]["positive_factors"],
                "is_recommended": False
            }
            scored_routes.append(route_item)

        # Sort routes by final_score descending
        scored_routes.sort(key=lambda x: x["final_score"], reverse=True)
        if scored_routes:
            scored_routes[0]["is_recommended"] = True

        return scored_routes
