import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data

def test_route_search_endpoint(client):
    payload = {
        "origin": "37.7749, -122.4194",
        "destination": "37.7925, -122.4012",
        "hour_of_day": 21,
        "is_weekend": 0
    }
    response = client.post("/api/routes/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_route_id" in data
    assert len(data["routes"]) >= 1
    assert data["routes"][0]["safety_score"] >= 0

def test_safety_predict_endpoint(client):
    payload = {
        "crime_incident_count": 2,
        "crime_density": 1.0,
        "weighted_crime_severity": 15.0,
        "min_dist_recent_crime_m": 500.0,
        "lighting_score_avg": 80.0,
        "dark_segment_pct": 10.0,
        "crowd_density_avg": 60.0,
        "isolated_segment_pct": 10.0,
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
    response = client.post("/api/safety/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "safety_score" in data
    assert "predicted_risk" in data

def test_reports_endpoints(client):
    report_payload = {
        "category": "Poor Lighting",
        "severity": 2,
        "description": "Dim street light near bus stop",
        "latitude": 37.7750,
        "longitude": -122.4195
    }
    post_res = client.post("/api/reports", json=report_payload)
    assert post_res.status_code == 201
    post_data = post_res.json()
    assert post_data["category"] == "Poor Lighting"

    get_res = client.get("/api/reports")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert len(get_data) >= 1
