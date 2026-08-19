from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import math
import random
import requests
from backend.app.core.config import settings

class RoutingProvider(ABC):
    @abstractmethod
    def get_routes(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        pass

class WeatherProvider(ABC):
    @abstractmethod
    def get_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        pass

class MockRoutingProvider(RoutingProvider):
    """
    Simulates alternative routes between origin and destination coordinates.
    Generates realistic geometric polylines, distances, and travel durations.
    """
    def get_routes(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        orig_lat, orig_lng = self._parse_or_geocode(origin, is_dest=False)
        dest_lat, dest_lng = self._parse_or_geocode(destination, is_dest=True)

        # Base straight distance
        base_dist_m = self._haversine(orig_lat, orig_lng, dest_lat, dest_lng)
        base_dist_km = max(base_dist_m / 1000.0, 0.5)
        base_duration_min = (base_dist_km / 25.0) * 60.0 # ~25 km/h urban speed

        routes = []
        # Generate 3 alternative routes: Direct/Main Street, Park Way, Commercial Avenue
        variations = [
            {"name": "Main Highway Route", "dist_mult": 1.0, "time_mult": 1.0, "curve": 0.002},
            {"name": "Park Boulevard Route", "dist_mult": 1.08, "time_mult": 1.12, "curve": -0.005},
            {"name": "Commercial District Route", "dist_mult": 1.15, "time_mult": 1.25, "curve": 0.007}
        ]

        for idx, var in enumerate(variations):
            route_id = f"route_{idx + 1}"
            dist_km = round(base_dist_km * var["dist_mult"], 2)
            duration_min = round(base_duration_min * var["time_mult"], 1)

            # Generate realistic interpolated polyline points with slight offset curve
            geometry = self._generate_polyline(orig_lat, orig_lng, dest_lat, dest_lng, curve_factor=var["curve"])

            routes.append({
                "route_id": route_id,
                "name": var["name"],
                "origin_address": origin,
                "destination_address": destination,
                "origin_lat": orig_lat,
                "origin_lng": orig_lng,
                "dest_lat": dest_lat,
                "dest_lng": dest_lng,
                "distance_km": dist_km,
                "duration_minutes": duration_min,
                "geometry": geometry,
                "steps": [
                    {"instruction": f"Start on {origin}", "distance_km": round(dist_km * 0.3, 2)},
                    {"instruction": f"Continue along {var['name']}", "distance_km": round(dist_km * 0.5, 2)},
                    {"instruction": f"Arrive at {destination}", "distance_km": round(dist_km * 0.2, 2)}
                ]
            })

        return routes

    def _parse_or_geocode(self, location: str, is_dest: bool) -> Tuple[float, float]:
        try:
            parts = location.split(",")
            if len(parts) == 2:
                return float(parts[0].strip()), float(parts[1].strip())
        except ValueError:
            pass

        # Demo City Base: San Francisco (37.7749, -122.4194)
        if not is_dest:
            return 37.7749, -122.4194
        else:
            return 37.7925, -122.4012

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        R = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0)**2
        return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def _generate_polyline(self, lat1, lng1, lat2, lng2, curve_factor=0.003, num_points=25) -> List[Tuple[float, float]]:
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            lat = lat1 + t * (lat2 - lat1) + math.sin(t * math.pi) * curve_factor
            lng = lng1 + t * (lng2 - lng1) + math.cos(t * math.pi) * curve_factor * 0.5
            points.append((round(lat, 6), round(lng, 6)))
        return points

class GoogleRoutingProvider(RoutingProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_routes(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "alternatives": "true",
            "key": self.api_key
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "OK":
            raise ValueError(f"Google Maps API error: {data.get('error_message', data.get('status'))}")

        routes = []
        for idx, r in enumerate(data.get("routes", [])):
            leg = r["legs"][0]
            # Decode polyline or extract points
            points = self._decode_polyline(r["overview_polyline"]["points"])
            routes.append({
                "route_id": f"route_{idx + 1}",
                "name": r.get("summary", f"Route {idx + 1}"),
                "origin_address": leg["start_address"],
                "destination_address": leg["end_address"],
                "origin_lat": leg["start_location"]["lat"],
                "origin_lng": leg["start_location"]["lng"],
                "dest_lat": leg["end_location"]["lat"],
                "dest_lng": leg["end_location"]["lng"],
                "distance_km": round(leg["distance"]["value"] / 1000.0, 2),
                "duration_minutes": round(leg["duration"]["value"] / 60.0, 1),
                "geometry": points,
                "steps": [
                    {"instruction": s["html_instructions"], "distance_km": round(s["distance"]["value"] / 1000.0, 2)}
                    for s in leg.get("steps", [])
                ]
            })
        return routes

    def _decode_polyline(self, polyline_str: str) -> List[Tuple[float, float]]:
        index, lat, lng = 0, 0, 0
        coordinates = []
        changes = {'latitude': 0, 'longitude': 0}
        while index < len(polyline_str):
            for unit in ['latitude', 'longitude']:
                shift, result = 0, 0
                while True:
                    byte = ord(polyline_str[index]) - 63
                    index += 1
                    result |= (byte & 0x1f) << shift
                    shift += 5
                    if not byte >= 0x20:
                        break
                if result & 1:
                    changes[unit] = ~(result >> 1)
                else:
                    changes[unit] = (result >> 1)

            lat += changes['latitude']
            lng += changes['longitude']
            coordinates.append((lat / 100000.0, lng / 100000.0))
        return coordinates

class MockWeatherProvider(WeatherProvider):
    def get_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        return {
            "temperature": 18.5,
            "condition_name": "Clear",
            "visibility": 10.0,
            "precipitation": 0.0
        }

class OpenWeatherProvider(WeatherProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={self.api_key}&units=metric"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if resp.status_code != 200:
            return MockWeatherProvider().get_weather(lat, lng)
        return {
            "temperature": data.get("main", {}).get("temp", 20.0),
            "condition_name": data.get("weather", [{}])[0].get("main", "Clear"),
            "visibility": data.get("visibility", 10000) / 1000.0,
            "precipitation": data.get("rain", {}).get("1h", 0.0)
        }
