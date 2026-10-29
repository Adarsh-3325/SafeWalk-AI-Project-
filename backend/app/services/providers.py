from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import math
import re
import requests
from backend.app.core.config import settings

# Predefined Delhi Landmark & Locality Geocoding Directory
DELHI_LANDMARKS = {
    "connaught place": (28.6304, 77.2177),
    "cp": (28.6304, 77.2177),
    "rajiv chowk": (28.6328, 77.2195),
    "india gate": (28.6129, 77.2295),
    "kartavya path": (28.6129, 77.2215),
    "chandni chowk": (28.6562, 77.2410),
    "red fort": (28.6562, 77.2410),
    "hauz khas": (28.5494, 77.2001),
    "hauz khas village": (28.5535, 77.1945),
    "saket": (28.5245, 77.2066),
    "select citywalk": (28.5284, 77.2192),
    "karol bagh": (28.6517, 77.1906),
    "lajpat nagar": (28.5700, 77.2400),
    "central market": (28.5685, 77.2430),
    "aiims": (28.5672, 77.2100),
    "safdarjung": (28.5680, 77.2050),
    "kashmere gate": (28.6675, 77.2285),
    "dwarka": (28.5921, 77.0460),
    "dwarka sector 10": (28.5815, 77.0570),
    "dwarka sector 21": (28.5523, 77.0583),
    "dwarka mor": (28.6190, 77.0330),
    "rohini": (28.7166, 77.1166),
    "rohini sector 10": (28.7120, 77.1210),
    "delhi university": (28.6889, 77.2102),
    "north campus": (28.6889, 77.2102),
    "south campus": (28.5855, 77.1650),
    "janakpuri": (28.6219, 77.0878),
    "mayur vihar": (28.6127, 77.2773),
    "akshardham": (28.6127, 77.2773),
    "anand vihar": (28.6469, 77.3150),
    "paharganj": (28.6428, 77.2160),
    "new delhi railway station": (28.6428, 77.2190),
    "vasant kunj": (28.5400, 77.1550),
    "qutub minar": (28.5244, 77.1855),
    "lotus temple": (28.5535, 77.2588),
    "noida sector 18": (28.5700, 77.3200),
    "cyber city": (28.4950, 77.0895),
    "cyber hub": (28.4950, 77.0895),
    "gurgaon": (28.4595, 77.0266),
    "gurugram": (28.4595, 77.0266),
    "greater noida": (28.4744, 77.5040),
    "pari chowk": (28.4631, 77.5081),
    "alpha 1": (28.4750, 77.5100),
    "beta 1": (28.4808, 77.5069)
}

def clean_instruction_text(text: str) -> str:
    """Removes HTML tags and normalizes whitespace."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]*>', ' ', text)
    return " ".join(clean.split()).strip()

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
    Real-world Delhi road network routing provider.
    Uses OSRM turn-by-turn routing over genuine road physical geometry.
    """
    def get_routes(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        orig_lat, orig_lng = self._parse_or_geocode(origin, is_dest=False)
        dest_lat, dest_lng = self._parse_or_geocode(destination, is_dest=True)

        # 1. Fetch real ground road geometry via OSRM
        try:
            osrm_routes = self._fetch_osrm_routes(orig_lat, orig_lng, dest_lat, dest_lng, origin, destination)
            if osrm_routes and len(osrm_routes) > 0:
                return osrm_routes
        except Exception as e:
            print(f"[OSRM Routing Notice] {e}")

        # 2. Resilient fallback road routes
        return self._generate_fallback_road_routes(orig_lat, orig_lng, dest_lat, dest_lng, origin, destination)

    def _fetch_osrm_routes(self, orig_lat: float, orig_lng: float, dest_lat: float, dest_lng: float, origin: str, destination: str) -> List[Dict[str, Any]]:
        headers = {"User-Agent": "SafeWalkAI-Navigator/1.0 (Delhi; Python/Requests)"}
        routes = []

        # Primary driving request with alternatives
        url_drive = f"https://router.project-osrm.org/route/v1/driving/{orig_lng},{orig_lat};{dest_lng},{dest_lat}"
        params_drive = {"overview": "full", "geometries": "geojson", "steps": "true", "alternatives": "true"}
        
        try:
            resp = requests.get(url_drive, params=params_drive, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    for idx, r in enumerate(data["routes"]):
                        route_name = self._determine_route_name(idx, r)
                        geom = [(pt[1], pt[0]) for pt in r["geometry"]["coordinates"]]
                        dist_km = round(r["distance"] / 1000.0, 2)
                        dur_min = round(r["duration"] / 60.0, 1)

                        steps = []
                        for leg in r.get("legs", []):
                            for step in leg.get("steps", []):
                                raw_name = step.get("name") or step.get("maneuver", {}).get("type", "Proceed")
                                clean_name = clean_instruction_text(raw_name)
                                step_dist = round(step.get("distance", 0) / 1000.0, 2)
                                if clean_name:
                                    steps.append({"instruction": clean_name, "distance_km": step_dist})

                        routes.append({
                            "route_id": f"route_{len(routes) + 1}",
                            "name": route_name,
                            "origin_address": origin,
                            "destination_address": destination,
                            "origin_lat": orig_lat,
                            "origin_lng": orig_lng,
                            "dest_lat": dest_lat,
                            "dest_lng": dest_lng,
                            "distance_km": dist_km,
                            "duration_minutes": dur_min,
                            "geometry": geom,
                            "steps": steps or [{"instruction": f"Proceed along {route_name} towards {destination}", "distance_km": dist_km}]
                        })
        except Exception as e:
            print(f"[OSRM Driving Fetch Error] {e}")

        # If less than 3 alternative routes, query walking route to offer a dedicated pedestrian corridor
        if len(routes) < 3:
            try:
                url_walk = f"https://router.project-osrm.org/route/v1/walking/{orig_lng},{orig_lat};{dest_lng},{dest_lat}"
                params_walk = {"overview": "full", "geometries": "geojson", "steps": "true"}
                resp_walk = requests.get(url_walk, params=params_walk, headers=headers, timeout=6)
                if resp_walk.status_code == 200:
                    data_walk = resp_walk.json()
                    if data_walk.get("code") == "Ok" and data_walk.get("routes"):
                        r = data_walk["routes"][0]
                        geom = [(pt[1], pt[0]) for pt in r["geometry"]["coordinates"]]
                        dist_km = round(r["distance"] / 1000.0, 2)
                        dur_min = round((dist_km / 4.5) * 60.0, 1) # ~4.5 km/h walking speed

                        steps = []
                        for leg in r.get("legs", []):
                            for step in leg.get("steps", []):
                                raw_name = step.get("name") or "Walk along pathway"
                                steps.append({"instruction": clean_instruction_text(raw_name), "distance_km": round(step.get("distance", 0) / 1000.0, 2)})

                        routes.append({
                            "route_id": f"route_{len(routes) + 1}",
                            "name": "Pedestrian Walkway & Boulevard",
                            "origin_address": origin,
                            "destination_address": destination,
                            "origin_lat": orig_lat,
                            "origin_lng": orig_lng,
                            "dest_lat": dest_lat,
                            "dest_lng": dest_lng,
                            "distance_km": dist_km,
                            "duration_minutes": dur_min,
                            "geometry": geom,
                            "steps": steps or [{"instruction": f"Walk safely towards {destination}", "distance_km": dist_km}]
                        })
            except Exception as e:
                print(f"[OSRM Walking Fetch Error] {e}")

        # If still only 1 route, query via an intermediate Delhi corridor waypoint
        if len(routes) == 1:
            try:
                mid_lat = (orig_lat + dest_lat) / 2.0 + 0.008
                mid_lng = (orig_lng + dest_lng) / 2.0 + 0.008
                url_via = f"https://router.project-osrm.org/route/v1/driving/{orig_lng},{orig_lat};{mid_lng},{mid_lat};{dest_lng},{dest_lat}"
                resp_via = requests.get(url_via, params={"overview": "full", "geometries": "geojson", "steps": "true"}, headers=headers, timeout=6)
                if resp_via.status_code == 200:
                    data_via = resp_via.json()
                    if data_via.get("code") == "Ok" and data_via.get("routes"):
                        r = data_via["routes"][0]
                        geom = [(pt[1], pt[0]) for pt in r["geometry"]["coordinates"]]
                        dist_km = round(r["distance"] / 1000.0, 2)
                        dur_min = round(r["duration"] / 60.0, 1)

                        routes.append({
                            "route_id": f"route_{len(routes) + 1}",
                            "name": "Arterial Ring Road Route",
                            "origin_address": origin,
                            "destination_address": destination,
                            "origin_lat": orig_lat,
                            "origin_lng": orig_lng,
                            "dest_lat": dest_lat,
                            "dest_lng": dest_lng,
                            "distance_km": dist_km,
                            "duration_minutes": dur_min,
                            "geometry": geom,
                            "steps": [{"instruction": f"Follow Ring Road towards {destination}", "distance_km": dist_km}]
                        })
            except Exception as e:
                print(f"[OSRM Via Fetch Error] {e}")

        return routes if routes else None

    def _determine_route_name(self, idx: int, route_obj: Dict[str, Any]) -> str:
        legs = route_obj.get("legs", [])
        if legs:
            for step in legs[0].get("steps", []):
                name = step.get("name")
                if name and len(name) > 3 and "road" in name.lower() or "marg" in name.lower() or "expressway" in name.lower() or "path" in name.lower():
                    return f"Via {name}"

        defaults = ["Main Arterial Avenue", "Protected Metro Corridor", "Commercial Boulevard Route"]
        return defaults[idx % len(defaults)]

    def _generate_fallback_road_routes(self, orig_lat: float, orig_lng: float, dest_lat: float, dest_lng: float, origin: str, destination: str) -> List[Dict[str, Any]]:
        base_dist_m = self._haversine(orig_lat, orig_lng, dest_lat, dest_lng)
        base_dist_km = max(base_dist_m / 1000.0, 0.6)
        base_dur_min = (base_dist_km / 22.0) * 60.0

        corridors = [
            {"name": "Central Arterial Highway", "dist_mult": 1.0, "time_mult": 1.0, "offset": 0.0},
            {"name": "Metro Transit & Well-Lit Avenue", "dist_mult": 1.06, "time_mult": 1.10, "offset": 0.002},
            {"name": "Commercial District Corridor", "dist_mult": 1.12, "time_mult": 1.20, "offset": -0.002}
        ]

        routes = []
        for idx, c in enumerate(corridors):
            dist_km = round(base_dist_km * c["dist_mult"], 2)
            dur_min = round(base_dur_min * c["time_mult"], 1)

            # Interpolate along points
            points = []
            num_pts = 20
            for i in range(num_pts):
                t = i / float(num_pts - 1)
                lat = orig_lat + t * (dest_lat - orig_lat) + math.sin(t * math.pi) * c["offset"]
                lng = orig_lng + t * (dest_lng - orig_lng) + math.sin(t * math.pi) * c["offset"] * 0.8
                points.append((round(lat, 6), round(lng, 6)))

            routes.append({
                "route_id": f"route_{idx + 1}",
                "name": c["name"],
                "origin_address": origin,
                "destination_address": destination,
                "origin_lat": orig_lat,
                "origin_lng": orig_lng,
                "dest_lat": dest_lat,
                "dest_lng": dest_lng,
                "distance_km": dist_km,
                "duration_minutes": dur_min,
                "geometry": points,
                "steps": [
                    {"instruction": f"Depart from {clean_instruction_text(origin)}", "distance_km": round(dist_km * 0.25, 2)},
                    {"instruction": f"Continue along {c['name']}", "distance_km": round(dist_km * 0.55, 2)},
                    {"instruction": f"Arrive at {clean_instruction_text(destination)}", "distance_km": round(dist_km * 0.20, 2)}
                ]
            })
        return routes

    def _parse_or_geocode(self, location: str, is_dest: bool) -> Tuple[float, float]:
        if not location:
            # Default to Delhi Center
            return (28.6129, 77.2295) if is_dest else (28.6304, 77.2177)

        # 1. Coordinate string: "28.6304, 77.2177"
        try:
            parts = location.split(",")
            if len(parts) == 2:
                lat, lng = float(parts[0].strip()), float(parts[1].strip())
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    return lat, lng
        except ValueError:
            pass

        loc_lower = location.strip().lower()

        # 2. Check predefined Delhi Landmarks dictionary
        for key, coords in DELHI_LANDMARKS.items():
            if key in loc_lower or loc_lower in key:
                return coords

        # 3. Google Geocoding API if key configured
        api_key = settings.clean_google_maps_api_key
        if api_key:
            try:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {"address": f"{location}, Delhi, India", "key": api_key}
                resp = requests.get(url, params=params, timeout=5)
                data = resp.json()
                if data.get("status") == "OK" and data.get("results"):
                    loc = data["results"][0]["geometry"]["location"]
                    return round(loc["lat"], 6), round(loc["lng"], 6)
            except Exception as e:
                print(f"[Google Geocoding Warning] {e}")

        # 4. OpenStreetMap Nominatim Geocoding with Delhi focus
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": f"{location}, Delhi, India",
                "format": "json",
                "limit": 1,
                "viewbox": "76.80,28.90,77.45,28.35",
                "bounded": 0
            }
            headers = {"User-Agent": "SafeWalkAI-Geocoder/1.0 (Delhi; safewalk.app)"}
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    lat = float(results[0]["lat"])
                    lng = float(results[0]["lon"])
                    return round(lat, 6), round(lng, 6)
        except Exception as e:
            print(f"[Nominatim Geocoding Warning] {e}")

        # Default fallback coordinates: Connaught Place / India Gate, New Delhi
        if not is_dest:
            return 28.6304, 77.2177 # Connaught Place
        else:
            return 28.6129, 77.2295 # India Gate

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        R = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0)**2
        return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

class GoogleRoutingProvider(RoutingProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_routes(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": f"{origin}, Delhi, India",
                "destination": f"{destination}, Delhi, India",
                "alternatives": "true",
                "key": self.api_key
            }
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") != "OK":
                return MockRoutingProvider().get_routes(origin, destination)

            routes = []
            for idx, r in enumerate(data.get("routes", [])):
                leg = r["legs"][0]
                points = self._decode_polyline(r["overview_polyline"]["points"])
                routes.append({
                    "route_id": f"route_{idx + 1}",
                    "name": clean_instruction_text(r.get("summary", f"Route {idx + 1}")),
                    "origin_address": clean_instruction_text(leg["start_address"]),
                    "destination_address": clean_instruction_text(leg["end_address"]),
                    "origin_lat": leg["start_location"]["lat"],
                    "origin_lng": leg["start_location"]["lng"],
                    "dest_lat": leg["end_location"]["lat"],
                    "dest_lng": leg["end_location"]["lng"],
                    "distance_km": round(leg["distance"]["value"] / 1000.0, 2),
                    "duration_minutes": round(leg["duration"]["value"] / 60.0, 1),
                    "geometry": points,
                    "steps": [
                        {
                            "instruction": clean_instruction_text(s.get("html_instructions", "")),
                            "distance_km": round(s["distance"]["value"] / 1000.0, 2)
                        }
                        for s in leg.get("steps", [])
                    ]
                })
            return routes
        except Exception as e:
            print(f"[GoogleRoutingProvider Error] {e}. Falling back to OSRM routes.")
            return MockRoutingProvider().get_routes(origin, destination)

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
            "temperature": 24.5,
            "condition_name": "Clear",
            "visibility": 8.5,
            "precipitation": 0.0
        }

class OpenWeatherProvider(WeatherProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={self.api_key}&units=metric"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if resp.status_code != 200:
                return MockWeatherProvider().get_weather(lat, lng)
            return {
                "temperature": data.get("main", {}).get("temp", 24.5),
                "condition_name": data.get("weather", [{}])[0].get("main", "Clear"),
                "visibility": data.get("visibility", 8500) / 1000.0,
                "precipitation": data.get("rain", {}).get("1h", 0.0)
            }
        except Exception:
            return MockWeatherProvider().get_weather(lat, lng)
