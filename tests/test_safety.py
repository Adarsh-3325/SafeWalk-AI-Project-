import pytest
from ml.feature_engineering import haversine_distance_m, sample_polyline_points, extract_route_safety_features

def test_haversine_distance():
    # Distance between SF Ferry Building and Coit Tower ~1.2 km
    dist = haversine_distance_m(37.7955, -122.3937, 37.8024, -122.4058)
    assert 1000.0 <= dist <= 1600.0

def test_sample_polyline_points():
    geometry = [(37.7749, -122.4194), (37.7849, -122.4094), (37.7949, -122.3994)]
    sampled = sample_polyline_points(geometry, step_meters=100.0)
    assert len(sampled) >= len(geometry)

def test_extract_route_safety_features():
    geometry = [(37.7749, -122.4194), (37.7849, -122.4094)]
    crimes = [{"latitude": 37.7750, "longitude": -122.4190, "crime_type": "Theft", "severity": 3}]
    lights = [{"latitude": 37.7749, "longitude": -122.4194, "lighting_score": 90.0}]
    crowds = [{"latitude": 37.7749, "longitude": -122.4194, "density_score": 80.0}]
    weather = {"temperature": 18.0, "visibility": 10.0, "precipitation": 0.0}
    reports = []

    features = extract_route_safety_features(
        geometry=geometry,
        distance_km=1.5,
        crimes=crimes,
        lights=lights,
        crowd_points=crowds,
        weather_info=weather,
        user_reports=reports,
        hour_of_day=14
    )

    assert features["crime_incident_count"] == 1
    assert features["lighting_score_avg"] >= 50.0
    assert features["is_night"] == 0
