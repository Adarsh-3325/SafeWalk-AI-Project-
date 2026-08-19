import pytest
import pandas as pd
import numpy as np
from ml.preprocessing import SafetyFeaturePreprocessor, FEATURE_COLUMNS
from ml.generate_dataset import generate_synthetic_safety_dataset
from backend.app.ml.predictor import SafetyPredictor

def test_dataset_generator():
    df = generate_synthetic_safety_dataset(num_samples=100, random_seed=42)
    assert len(df) == 100
    assert "risk_score" in df.columns
    for col in FEATURE_COLUMNS:
        assert col in df.columns

def test_preprocessor():
    df = generate_synthetic_safety_dataset(num_samples=50, random_seed=42)
    preprocessor = SafetyFeaturePreprocessor()
    transformed = preprocessor.fit_transform(df)
    assert transformed.shape == (50, len(FEATURE_COLUMNS))
    assert preprocessor.is_fitted is True

def test_safety_predictor():
    predictor = SafetyPredictor()
    sample_features = {
        "crime_incident_count": 5,
        "crime_density": 2.0,
        "weighted_crime_severity": 30.0,
        "min_dist_recent_crime_m": 250.0,
        "lighting_score_avg": 85.0,
        "dark_segment_pct": 5.0,
        "crowd_density_avg": 70.0,
        "isolated_segment_pct": 5.0,
        "temp_celsius": 20.0,
        "visibility_km": 10.0,
        "precipitation_mm": 0.0,
        "weather_severity": 0.0,
        "hour_of_day": 14,
        "is_weekend": 0,
        "is_night": 0,
        "is_peak_hour": 0,
        "user_report_count": 0,
        "weighted_user_reports": 0.0,
        "report_density": 0.0
    }
    result = predictor.predict_safety(sample_features)
    assert "safety_score" in result
    assert "risk_level" in result
    assert 0.0 <= result["safety_score"] <= 100.0
    assert isinstance(result["top_risk_factors"], list)
    assert isinstance(result["positive_factors"], list)
