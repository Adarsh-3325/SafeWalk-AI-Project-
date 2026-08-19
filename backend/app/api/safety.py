from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.safety_schema import SafetyPredictRequest, SafetyPredictResponse
from backend.app.ml.predictor import SafetyPredictor
from backend.app.models.database_models import RoutePrediction

router = APIRouter(prefix="/safety", tags=["Safety"])

predictor: SafetyPredictor = None

def set_predictor(p: SafetyPredictor):
    global predictor
    predictor = p

@router.post("/predict", response_model=SafetyPredictResponse)
def predict_safety_score(request: SafetyPredictRequest):
    if predictor is None:
        raise HTTPException(status_code=500, detail="Safety predictor not initialized.")

    features = request.dict()
    result = predictor.predict_safety(features)
    return result

@router.get("/{route_id}")
def get_route_safety_details(route_id: str, db: Session = Depends(get_db)):
    pred = db.query(RoutePrediction).filter(RoutePrediction.route_id == route_id).order_by(RoutePrediction.created_at.desc()).first()
    if not pred:
        raise HTTPException(status_code=404, detail=f"No prediction record found for route_id '{route_id}'")

    return {
        "route_id": pred.route_id,
        "ml_safety_score": pred.ml_safety_score,
        "risk_level": pred.risk_level,
        "crime_risk": pred.crime_risk,
        "lighting_score": pred.lighting_score,
        "crowd_score": pred.crowd_score,
        "weather_risk": pred.weather_risk,
        "time_risk": pred.time_risk,
        "report_risk": pred.report_risk,
        "created_at": pred.created_at.isoformat() if pred.created_at else None
    }
