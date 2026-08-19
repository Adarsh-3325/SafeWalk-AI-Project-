import math
from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great circle distance between two points on the earth in meters.
    """
    R = 6371000.0 # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c

def sample_polyline_points(geometry: List[Tuple[float, float]], step_meters: float = 100.0) -> List[Tuple[float, float]]:
    """
    Samples points along a route geometry polyline roughly every step_meters.
    """
    if not geometry or len(geometry) < 2:
        return geometry or []

    sampled_points = [geometry[0]]
    accumulated = 0.0

    for i in range(len(geometry) - 1):
        p1 = geometry[i]
        p2 = geometry[i + 1]
        dist = haversine_distance_m(p1[0], p1[1], p2[0], p2[1])

        if dist == 0:
            continue

        if accumulated + dist < step_meters:
            accumulated += dist
        else:
            # Interpolate
            fraction = (step_meters - accumulated) / dist
            interp_lat = p1[0] + fraction * (p2[0] - p1[0])
            interp_lng = p1[1] + fraction * (p2[1] - p1[1])
            sampled_points.append((interp_lat, interp_lng))
            accumulated = 0.0

    if geometry[-1] not in sampled_points:
        sampled_points.append(geometry[-1])

    return sampled_points

def extract_route_safety_features(
    geometry: List[Tuple[float, float]],
    distance_km: float,
    crimes: List[Dict[str, Any]],
    lights: List[Dict[str, Any]],
    crowd_points: List[Dict[str, Any]],
    weather_info: Dict[str, Any],
    user_reports: List[Dict[str, Any]],
    hour_of_day: int = 14,
    is_weekend: int = 0,
    search_radius_m: float = 250.0
) -> Dict[str, Any]:
    """
    Calculates safety features along a route geometry given nearby environmental data.
    """
    sampled = sample_polyline_points(geometry, step_meters=100.0)
    num_samples = max(len(sampled), 1)

    # 1. Crime Feature Aggregation
    nearby_crimes = []
    min_crime_dist = 99999.0
    total_crime_severity = 0.0

    for crime in crimes:
        c_lat = crime["latitude"]
        c_lng = crime["longitude"]
        # Find min distance to any sampled point along the route
        dists = [haversine_distance_m(p[0], p[p_idx], c_lat, c_lng) for p in sampled for p_idx in [1]]
        min_d = min(dists) if dists else 99999.0

        if min_d <= search_radius_m:
            nearby_crimes.append(crime)
            total_crime_severity += crime.get("severity", 1) * (1.0 - min_d / (search_radius_m + 1.0))
        if min_d < min_crime_dist:
            min_crime_dist = min_d

    crime_incident_count = len(nearby_crimes)
    crime_density = crime_incident_count / max(distance_km, 0.1)
    weighted_crime_severity = min(total_crime_severity * 10.0, 100.0)
    min_dist_recent_crime_m = min_crime_dist if min_crime_dist < 99999.0 else 2000.0

    # 2. Lighting Feature Aggregation
    sample_lighting_scores = []
    dark_count = 0
    for p in sampled:
        # Average lighting score within 150m of sample point
        nearby_lights = [l for l in lights if haversine_distance_m(p[0], p[1], l["latitude"], l["longitude"]) <= 150.0]
        if nearby_lights:
            avg_light = np.mean([l["lighting_score"] for l in nearby_lights])
        else:
            avg_light = 70.0 # baseline
        sample_lighting_scores.append(avg_light)
        if avg_light < 40.0:
            dark_count += 1

    lighting_score_avg = float(np.mean(sample_lighting_scores)) if sample_lighting_scores else 70.0
    dark_segment_pct = (dark_count / num_samples) * 100.0

    # 3. Crowd Density Aggregation
    sample_crowd_scores = []
    isolated_count = 0
    for p in sampled:
        nearby_c = [c for c in crowd_points if haversine_distance_m(p[0], p[1], c["latitude"], c["longitude"]) <= 200.0]
        if nearby_c:
            avg_c = np.mean([c["density_score"] for c in nearby_c])
        else:
            avg_c = 50.0
        sample_crowd_scores.append(avg_c)
        if avg_c < 30.0:
            isolated_count += 1

    crowd_density_avg = float(np.mean(sample_crowd_scores)) if sample_crowd_scores else 50.0
    isolated_segment_pct = (isolated_count / num_samples) * 100.0

    # 4. Weather
    temp_celsius = weather_info.get("temperature", 20.0)
    visibility_km = weather_info.get("visibility", 10.0)
    precipitation_mm = weather_info.get("precipitation", 0.0)
    weather_severity = min(precipitation_mm * 1.5 + (15.0 - visibility_km) * 0.5, 10.0)

    # 5. Time Features
    is_night = 1 if (hour_of_day >= 21 or hour_of_day < 6) else 0
    is_peak_hour = 1 if ((7 <= hour_of_day <= 9) or (17 <= hour_of_day <= 19)) else 0

    # 6. User Reports Aggregation
    nearby_reports = []
    total_report_severity = 0.0
    for r in user_reports:
        r_lat = r["latitude"]
        r_lng = r["longitude"]
        dists = [haversine_distance_m(p[0], p[1], r_lat, r_lng) for p in sampled]
        min_d = min(dists) if dists else 99999.0

        if min_d <= search_radius_m:
            nearby_reports.append(r)
            total_report_severity += r.get("severity", 1)

    user_report_count = len(nearby_reports)
    weighted_user_reports = min(total_report_severity * 5.0, 50.0)
    report_density = user_report_count / max(distance_km, 0.1)

    return {
        "crime_incident_count": crime_incident_count,
        "crime_density": crime_density,
        "weighted_crime_severity": weighted_crime_severity,
        "min_dist_recent_crime_m": min_dist_recent_crime_m,
        "lighting_score_avg": lighting_score_avg,
        "dark_segment_pct": dark_segment_pct,
        "crowd_density_avg": crowd_density_avg,
        "isolated_segment_pct": isolated_segment_pct,
        "temp_celsius": temp_celsius,
        "visibility_km": visibility_km,
        "precipitation_mm": precipitation_mm,
        "weather_severity": weather_severity,
        "hour_of_day": hour_of_day,
        "is_weekend": is_weekend,
        "is_night": is_night,
        "is_peak_hour": is_peak_hour,
        "user_report_count": user_report_count,
        "weighted_user_reports": weighted_user_reports,
        "report_density": report_density
    }
