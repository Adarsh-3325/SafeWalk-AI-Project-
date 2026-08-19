import json
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.schemas.route_schema import RouteSearchRequest, SearchResponseSchema, RouteResponseSchema
from backend.app.services.routing_service import RoutingService
from backend.app.services.safety_service import (
    CrimeService, LightingService, CrowdService, WeatherService, ReportService
)
from ml.feature_engineering import extract_route_safety_features
from backend.app.ml.predictor import SafetyPredictor
from backend.app.services.ranking_service import RouteRankingService
from backend.app.models.database_models import RouteModel, RoutePrediction, SearchHistory, ModelPredictionLog

router = APIRouter(prefix="/routes", tags=["Routes"])

routing_service = RoutingService()
crime_service = CrimeService()
lighting_service = LightingService()
crowd_service = CrowdService()
weather_service = WeatherService()
report_service = ReportService()
ranking_service = RouteRankingService()

# Global predictor instance populated on startup
predictor: SafetyPredictor = None

def set_predictor(p: SafetyPredictor):
    global predictor
    predictor = p

@router.post("/search", response_model=SearchResponseSchema)
def search_routes(request: RouteSearchRequest, db: Session = Depends(get_db)):
    if not request.origin or not request.destination:
        raise HTTPException(status_code=400, detail="Origin and Destination addresses are required.")

    # 1. Obtain Route Alternatives
    raw_routes = routing_service.get_route_alternatives(request.origin, request.destination)
    if not raw_routes:
        raise HTTPException(status_code=404, detail="No viable routes found between specified points.")

    # 2. Extract Safety Data from DB/Services
    crimes = crime_service.get_crime_incidents(db)
    lights = lighting_service.get_lighting_points(db)
    crowds = crowd_service.get_crowd_data(db, hour_of_day=request.hour_of_day)
    reports = report_service.get_user_reports(db)
    
    sample_lat = raw_routes[0]["origin_lat"]
    sample_lng = raw_routes[0]["origin_lng"]
    weather = weather_service.get_current_weather(sample_lat, sample_lng)

    # 3. Process Each Route with ML Model
    routes_with_predictions = []
    for r in raw_routes:
        # Extract features along route geometry
        features = extract_route_safety_features(
            geometry=r["geometry"],
            distance_km=r["distance_km"],
            crimes=crimes,
            lights=lights,
            crowd_points=crowds,
            weather_info=weather,
            user_reports=reports,
            hour_of_day=request.hour_of_day,
            is_weekend=request.is_weekend
        )

        # ML Risk Prediction
        if predictor is None:
            raise HTTPException(status_code=500, detail="ML Predictor not initialized.")

        pred = predictor.predict_safety(features)
        r["pred"] = pred
        routes_with_predictions.append(r)

        # Store in DB for historical persistence
        try:
            db_route = db.query(RouteModel).filter(RouteModel.id == r["route_id"]).first()
            if not db_route:
                db_route = RouteModel(
                    id=r["route_id"],
                    origin_address=r["origin_address"],
                    destination_address=r["destination_address"],
                    origin_lat=r["origin_lat"],
                    origin_lng=r["origin_lng"],
                    dest_lat=r["dest_lat"],
                    dest_lng=r["dest_lng"],
                    distance_km=r["distance_km"],
                    duration_minutes=r["duration_minutes"],
                    geometry_json=json.dumps(r["geometry"])
                )
                db.add(db_route)
                db.commit()

            # Save prediction
            db_pred = RoutePrediction(
                route_id=r["route_id"],
                ml_safety_score=pred["safety_score"],
                risk_level=pred["risk_level"],
                final_score=0.0, # Will update after ranking
                crime_risk=pred["crime_risk"],
                lighting_score=pred["lighting_score"],
                crowd_score=pred["crowd_score"],
                weather_risk=pred["weather_risk"],
                time_risk=pred["time_risk"],
                report_risk=pred["report_risk"]
            )
            db.add(db_pred)

            # Log prediction
            db.add(ModelPredictionLog(
                route_id=r["route_id"],
                raw_features_json=json.dumps(features),
                predicted_risk=pred["predicted_risk"],
                top_risk_factors_json=json.dumps(pred["top_risk_factors"])
            ))
            db.commit()
        except Exception:
            db.rollback()

    # 4. Rank Routes
    ranked_routes = ranking_service.rank_routes(routes_with_predictions)
    recommended_id = ranked_routes[0]["route_id"] if ranked_routes else ""

    # Log Search History
    try:
        search_log = SearchHistory(
            origin=request.origin,
            destination=request.destination,
            selected_route_id=recommended_id
        )
        db.add(search_log)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "recommended_route_id": recommended_id,
        "search_timestamp": datetime.utcnow().isoformat(),
        "demo_mode": settings.USE_MOCK_DATA or not bool(settings.GOOGLE_MAPS_API_KEY),
        "routes": ranked_routes
    }

@router.get("/history")
def get_search_history(db: Session = Depends(get_db)):
    history = db.query(SearchHistory).order_by(SearchHistory.search_time.desc()).limit(20).all()
    return [
        {
            "id": h.id,
            "origin": h.origin,
            "destination": h.destination,
            "selected_route_id": h.selected_route_id,
            "search_time": h.search_time.isoformat() if h.search_time else None
        }
        for h in history
    ]
