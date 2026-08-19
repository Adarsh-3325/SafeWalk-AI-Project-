import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from ml.preprocessing import SafetyFeaturePreprocessor, FEATURE_COLUMNS

class SafetyPredictor:
    """
    Backend ML predictor loading saved model artifacts for zero-latency inference.
    Provides safety score calculation and explainable risk breakdown.
    """
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(__file__), "models")

        model_path = os.path.join(models_dir, "safety_model.joblib")
        prep_path = os.path.join(models_dir, "preprocessor.joblib")
        meta_path = os.path.join(models_dir, "feature_metadata.json")

        if not os.path.exists(model_path) or not os.path.exists(prep_path):
            raise FileNotFoundError(f"Model artifacts not found in {models_dir}. Please run ml/train.py first.")

        self.model = joblib.load(model_path)
        self.preprocessor: SafetyFeaturePreprocessor = joblib.load(prep_path)

        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

    def predict_safety(self, features: Dict[str, Any]) -> Dict[str, Any]:
        df_sample = pd.DataFrame([features])
        scaled_sample = self.preprocessor.transform(df_sample)
        predicted_risk = float(self.model.predict(scaled_sample)[0])

        # Clip predicted risk to 0-100 range
        predicted_risk = max(0.0, min(100.0, predicted_risk))
        safety_score = round(100.0 - predicted_risk, 1)

        risk_level, risk_category = self._get_risk_category(safety_score)
        top_risk_factors, positive_factors = self._generate_explainability(features)

        # Calculate individual feature risk breakdowns (0 to 100)
        crime_risk = round(min(features.get("weighted_crime_severity", 0.0) * 0.7 + features.get("crime_density", 0.0) * 5.0, 100.0), 1)
        lighting_score = round(features.get("lighting_score_avg", 70.0), 1)
        crowd_score = round(features.get("crowd_density_avg", 50.0), 1)
        weather_risk = round(features.get("weather_severity", 0.0) * 10.0, 1)
        time_risk = round(50.0 if features.get("is_night", 0) else 15.0, 1)
        report_risk = round(min(features.get("weighted_user_reports", 0.0) * 2.0, 100.0), 1)

        return {
            "predicted_risk": round(predicted_risk, 1),
            "safety_score": safety_score,
            "risk_level": risk_level,
            "risk_category": risk_category,
            "crime_risk": crime_risk,
            "lighting_score": lighting_score,
            "crowd_score": crowd_score,
            "weather_risk": weather_risk,
            "time_risk": time_risk,
            "report_risk": report_risk,
            "top_risk_factors": top_risk_factors,
            "positive_factors": positive_factors
        }

    def _get_risk_category(self, safety_score: float) -> Tuple[str, str]:
        if safety_score >= 80.0:
            return "Very Safe", "Low Risk"
        elif safety_score >= 60.0:
            return "Safe", "Moderate Risk"
        elif safety_score >= 40.0:
            return "Moderate", "Medium Risk"
        elif safety_score >= 20.0:
            return "Risky", "High Risk"
        else:
            return "High Risk", "Severe Risk"

    def _generate_explainability(self, features: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        top_risk_factors = []
        positive_factors = []

        # Crime
        if features.get("weighted_crime_severity", 0) > 40:
            top_risk_factors.append(f"High crime incident severity in nearby segments ({features.get('crime_incident_count', 0)} incidents)")
        elif features.get("crime_incident_count", 0) == 0:
            positive_factors.append("No recent crime incidents reported along this route")

        # Lighting
        if features.get("lighting_score_avg", 100) < 55:
            top_risk_factors.append(f"Poor street lighting coverage ({features.get('dark_segment_pct', 0):.0f}% poorly lit segments)")
        else:
            positive_factors.append(f"Well-lit street coverage ({features.get('lighting_score_avg', 0):.0f}% average score)")

        # Crowd Density
        if features.get("crowd_density_avg", 100) < 35:
            top_risk_factors.append(f"Low foot traffic / isolated segments ({features.get('isolated_segment_pct', 0):.0f}% isolated)")
        else:
            positive_factors.append(f"Active crowd density and pedestrian presence ({features.get('crowd_density_avg', 0):.0f} density score)")

        # Night factor
        if features.get("is_night", 0) == 1:
            top_risk_factors.append("Nighttime travel period (increased baseline risk)")
        else:
            positive_factors.append("Daylight travel conditions")

        # User reports
        if features.get("user_report_count", 0) > 0:
            top_risk_factors.append(f"{features.get('user_report_count', 0)} community safety reports along route")
        else:
            positive_factors.append("Zero negative community safety reports")

        return top_risk_factors[:3], positive_factors[:3]
