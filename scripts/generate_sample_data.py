import os
import sys
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.database_models import (
    CrimeIncident, LightingPoint, CrowdData, WeatherData, UserReport
)

# Delhi Key Hubs & Coordinate Hubs
DELHI_HUBS = [
    {"name": "Connaught Place / Rajiv Chowk", "lat": 28.6304, "lng": 77.2177, "type": "commercial", "base_light": 90, "base_crowd": 85},
    {"name": "India Gate / Kartavya Path", "lat": 28.6129, "lng": 77.2295, "type": "park", "base_light": 95, "base_crowd": 75},
    {"name": "Chandni Chowk / Red Fort", "lat": 28.6562, "lng": 77.2410, "type": "commercial", "base_light": 60, "base_crowd": 90},
    {"name": "Hauz Khas / Green Park", "lat": 28.5494, "lng": 77.2001, "type": "commercial", "base_light": 75, "base_crowd": 65},
    {"name": "Saket / Select Citywalk", "lat": 28.5245, "lng": 77.2066, "type": "commercial", "base_light": 85, "base_crowd": 80},
    {"name": "Karol Bagh / Pusa Road", "lat": 28.6517, "lng": 77.1906, "type": "commercial", "base_light": 70, "base_crowd": 80},
    {"name": "Lajpat Nagar / Central Market", "lat": 28.5700, "lng": 77.2400, "type": "commercial", "base_light": 75, "base_crowd": 85},
    {"name": "AIIMS / Safdarjung", "lat": 28.5672, "lng": 77.2100, "type": "transit_hub", "base_light": 80, "base_crowd": 80},
    {"name": "Kashmere Gate ISBT", "lat": 28.6675, "lng": 77.2285, "type": "transit_hub", "base_light": 65, "base_crowd": 90},
    {"name": "Dwarka Sector 10 & 21", "lat": 28.5921, "lng": 77.0460, "type": "residential", "base_light": 75, "base_crowd": 55},
    {"name": "Rohini Sector 10 / Rithala", "lat": 28.7166, "lng": 77.1166, "type": "residential", "base_light": 65, "base_crowd": 60},
    {"name": "Delhi University North Campus", "lat": 28.6889, "lng": 77.2102, "type": "transit_hub", "base_light": 80, "base_crowd": 70},
    {"name": "Mayur Vihar / Akshardham", "lat": 28.6127, "lng": 77.2773, "type": "residential", "base_light": 70, "base_crowd": 60},
    {"name": "Janakpuri District Centre", "lat": 28.6219, "lng": 77.0878, "type": "commercial", "base_light": 75, "base_crowd": 70},
    {"name": "Cyber City / DLF Phase 2 Gurgaon", "lat": 28.4950, "lng": 77.0895, "type": "commercial", "base_light": 90, "base_crowd": 75},
    {"name": "Sector 18 / Atta Market Noida", "lat": 28.5700, "lng": 77.3200, "type": "commercial", "base_light": 85, "base_crowd": 80},
    {"name": "Paharganj / New Delhi Station", "lat": 28.6428, "lng": 77.2160, "type": "transit_hub", "base_light": 50, "base_crowd": 85},
    {"name": "Vasant Kunj Promenade", "lat": 28.5400, "lng": 77.1550, "type": "commercial", "base_light": 85, "base_crowd": 65},
    {"name": "Seelampur / Shahdara", "lat": 28.6650, "lng": 77.2750, "type": "residential", "base_light": 45, "base_crowd": 75},
    {"name": "Anand Vihar ISBT", "lat": 28.6469, "lng": 77.3150, "type": "transit_hub", "base_light": 60, "base_crowd": 85}
]

CRIME_TYPES = ["Phone Snatching", "Eve-Teasing & Harassment", "Pickpocketing", "Vehicle Theft", "Dark Alley Robbery", "Suspicious Activity"]
LIGHT_TYPES = ["Smart LED Street Light", "High-Mast Floodlight", "Solar Pole Light", "Sodium Vapor Lamp"]
REPORT_CATEGORIES = ["Poor Lighting", "Harassment", "Suspicious Activity", "Deserted Underpass", "Snatching Hotspot", "Active Police PCR Van", "Broken Streetlight"]

def generate_spatial_demo_data(num_crimes=600, num_lights=1000, num_crowds=400, num_reports=250):
    os.makedirs("data", exist_ok=True)
    random.seed(42)
    np.random.seed(42)

    # 1. Crime Incidents across Delhi
    crimes = []
    for i in range(num_crimes):
        hub = random.choice(DELHI_HUBS)
        # Cluster around hubs with spatial jitter (approx 1-3 km)
        lat = hub["lat"] + np.random.normal(0, 0.015)
        lng = hub["lng"] + np.random.normal(0, 0.015)
        
        crime_type = random.choice(CRIME_TYPES)
        # Higher severity for robbery / harassment
        if crime_type in ["Dark Alley Robbery", "Eve-Teasing & Harassment"]:
            severity = random.randint(3, 5)
        else:
            severity = random.randint(1, 3)
            
        days_ago = random.randint(0, 60)
        ts = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        crimes.append({
            "id": i + 1,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "crime_type": crime_type,
            "severity": severity,
            "description": f"Delhi Police Reported: {crime_type} near {hub['name']}",
            "incident_timestamp": ts.isoformat()
        })
    df_crimes = pd.DataFrame(crimes)
    df_crimes.to_csv(os.path.join("data", "crime_data.csv"), index=False)

    # 2. Lighting Points across Delhi Arteries and Colonies
    lights = []
    for i in range(num_lights):
        hub = random.choice(DELHI_HUBS)
        lat = hub["lat"] + np.random.normal(0, 0.02)
        lng = hub["lng"] + np.random.normal(0, 0.02)
        
        # 15% dark / broken lights
        if random.random() < 0.15:
            score = float(random.randint(15, 40))
            is_func = False
        else:
            score = float(min(100, max(50, hub["base_light"] + random.randint(-15, 15))))
            is_func = True
            
        lights.append({
            "id": i + 1,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "lighting_score": score,
            "light_type": random.choice(LIGHT_TYPES),
            "is_functional": is_func
        })
    df_lights = pd.DataFrame(lights)
    df_lights.to_csv(os.path.join("data", "lighting_data.csv"), index=False)

    # 3. Crowd Data by Hour across Delhi
    crowds = []
    crowd_id = 1
    for hub in DELHI_HUBS:
        for hour in range(24):
            # Peak business / transit hours in Delhi: 8am - 11am and 5pm - 9pm
            if 8 <= hour <= 11 or 17 <= hour <= 21:
                density = float(min(98, max(45, hub["base_crowd"] + random.randint(-10, 15))))
            elif 12 <= hour <= 16:
                density = float(min(85, max(35, hub["base_crowd"] * 0.8 + random.randint(-10, 10))))
            elif 22 <= hour <= 23 or 6 <= hour <= 7:
                density = float(min(60, max(20, hub["base_crowd"] * 0.45 + random.randint(-10, 10))))
            else: # Late night 00:00 - 05:00
                density = float(random.randint(5, 25))

            lat = hub["lat"] + np.random.normal(0, 0.008)
            lng = hub["lng"] + np.random.normal(0, 0.008)

            crowds.append({
                "id": crowd_id,
                "latitude": round(lat, 6),
                "longitude": round(lng, 6),
                "hour_of_day": hour,
                "density_score": density,
                "area_type": hub["type"]
            })
            crowd_id += 1

    df_crowds = pd.DataFrame(crowds)
    df_crowds.to_csv(os.path.join("data", "crowd_data.csv"), index=False)

    # 4. Delhi Weather Data
    weather = [{
        "id": 1,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": 24.5,
        "condition_name": "Clear",
        "visibility": 8.5,
        "precipitation": 0.0
    }]
    df_weather = pd.DataFrame(weather)
    df_weather.to_csv(os.path.join("data", "weather_data.csv"), index=False)

    # 5. User Reports in Delhi
    reports = []
    for i in range(num_reports):
        hub = random.choice(DELHI_HUBS)
        lat = hub["lat"] + np.random.normal(0, 0.015)
        lng = hub["lng"] + np.random.normal(0, 0.015)
        cat = random.choice(REPORT_CATEGORIES)
        
        reports.append({
            "id": i + 1,
            "category": cat,
            "severity": random.randint(1, 5),
            "description": f"Delhi Citizen Alert: {cat} observed near {hub['name']}",
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "user_id": None,
            "status": "ACTIVE",
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))).isoformat()
        })
    df_reports = pd.DataFrame(reports)
    df_reports.to_csv(os.path.join("data", "reports.csv"), index=False)

    print("Delhi spatial datasets successfully generated in data/ directory!")

def seed_database(clear_first=True):
    print("Seeding database with Delhi spatial records...")
    db = SessionLocal()
    try:
        if clear_first:
            db.query(CrimeIncident).delete()
            db.query(LightingPoint).delete()
            db.query(CrowdData).delete()
            db.query(WeatherData).delete()
            db.query(UserReport).delete()
            db.commit()

        # Seed Crimes
        df_crimes = pd.read_csv(os.path.join("data", "crime_data.csv"))
        for _, row in df_crimes.iterrows():
            db.add(CrimeIncident(
                latitude=row["latitude"],
                longitude=row["longitude"],
                crime_type=row["crime_type"],
                severity=int(row["severity"]),
                description=row["description"],
                incident_timestamp=datetime.fromisoformat(row["incident_timestamp"])
            ))

        # Seed Lighting
        df_lights = pd.read_csv(os.path.join("data", "lighting_data.csv"))
        for _, row in df_lights.iterrows():
            db.add(LightingPoint(
                latitude=row["latitude"],
                longitude=row["longitude"],
                lighting_score=float(row["lighting_score"]),
                light_type=row["light_type"],
                is_functional=bool(row["is_functional"])
            ))

        # Seed Crowd
        df_crowds = pd.read_csv(os.path.join("data", "crowd_data.csv"))
        for _, row in df_crowds.iterrows():
            db.add(CrowdData(
                latitude=row["latitude"],
                longitude=row["longitude"],
                hour_of_day=int(row["hour_of_day"]),
                density_score=float(row["density_score"]),
                area_type=row["area_type"]
            ))

        # Seed Weather
        df_weather = pd.read_csv(os.path.join("data", "weather_data.csv"))
        for _, row in df_weather.iterrows():
            db.add(WeatherData(
                temperature=float(row["temperature"]),
                condition_name=row["condition_name"],
                visibility=float(row["visibility"]),
                precipitation=float(row["precipitation"])
            ))

        # Seed User Reports
        df_reports = pd.read_csv(os.path.join("data", "reports.csv"))
        for _, row in df_reports.iterrows():
            db.add(UserReport(
                category=row["category"],
                severity=int(row["severity"]),
                description=row["description"],
                latitude=row["latitude"],
                longitude=row["longitude"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"])
            ))

        db.commit()
        print("Delhi database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_spatial_demo_data()
    Base.metadata.create_all(bind=engine)
    seed_database(clear_first=True)
