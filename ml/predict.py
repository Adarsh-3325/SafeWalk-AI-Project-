import os
import sys
import joblib
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import FEATURE_COLUMNS

def predict_route_risk(sample_features: dict, models_dir: str = os.path.join("ml", "models")) -> float:
    model_path = os.path.join(models_dir, "safety_model.joblib")
    prep_path = os.path.join(models_dir, "preprocessor.joblib")

    rf_model = joblib.load(model_path)
    preprocessor = joblib.load(prep_path)

    df_sample = pd.DataFrame([sample_features])
    scaled_sample = preprocessor.transform(df_sample)
    predicted_risk = rf_model.predict(scaled_sample)[0]
    return float(predicted_risk)

if __name__ == "__main__":
    test_features = {
        "crime_incident_count": 12,
        "crime_density": 4.5,
        "weighted_crime_severity": 65.0,
        "min_dist_recent_crime_m": 85.0,
        "lighting_score_avg": 40.0,
        "dark_segment_pct": 45.0,
        "crowd_density_avg": 25.0,
        "isolated_segment_pct": 35.0,
        "temp_celsius": 18.0,
        "visibility_km": 8.0,
        "precipitation_mm": 1.2,
        "weather_severity": 4.0,
        "hour_of_day": 23,
        "is_weekend": 1,
        "is_night": 1,
        "is_peak_hour": 0,
        "user_report_count": 4,
        "weighted_user_reports": 18.0,
        "report_density": 1.2
    }
    risk = predict_route_risk(test_features)
    safety_score = max(0.0, min(100.0, 100.0 - risk))
    print(f"Sample Prediction - Predicted Risk Score: {risk:.2f}/100 | Safety Score: {safety_score:.2f}/100")
