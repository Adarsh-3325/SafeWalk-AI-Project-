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

# Demo City Center: San Francisco
CENTER_LAT = 37.7749
CENTER_LNG = -122.4194
LAT_DELTA = 0.08
LNG_DELTA = 0.08

CRIME_TYPES = ["Theft", "Harassment", "Vandalism", "Robbery", "Suspicious Activity", "Vehicle Break-in"]
LIGHT_TYPES = ["LED Street Light", "High-Pressure Sodium", "Solar Pole Light", "Decorative Lamp"]
REPORT_CATEGORIES = ["Poor Lighting", "Harassment", "Suspicious Activity", "Accident", "Theft", "Unsafe Area", "Road Block"]

def generate_spatial_demo_data(num_crimes=300, num_lights=500, num_crowds=200, num_reports=100):
    os.makedirs("data", exist_ok=True)
    random.seed(42)
    np.random.seed(42)

    # 1. Crime Incidents
    crimes = []
    for i in range(num_crimes):
        lat = CENTER_LAT + np.random.uniform(-LAT_DELTA, LAT_DELTA)
        lng = CENTER_LNG + np.random.uniform(-LNG_DELTA, LNG_DELTA)
        crime_type = random.choice(CRIME_TYPES)
        severity = random.randint(1, 5)
        days_ago = random.randint(0, 90)
        ts = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
        crimes.append({
            "id": i + 1,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "crime_type": crime_type,
            "severity": severity,
            "description": f"Reported {crime_type} incident",
            "incident_timestamp": ts.isoformat()
        })
    df_crimes = pd.DataFrame(crimes)
    df_crimes.to_csv(os.path.join("data", "crime_data.csv"), index=False)

    # 2. Lighting Points
    lights = []
    for i in range(num_lights):
        lat = CENTER_LAT + np.random.uniform(-LAT_DELTA, LAT_DELTA)
        lng = CENTER_LNG + np.random.uniform(-LNG_DELTA, LNG_DELTA)
        # Cluster some dark spots
        if random.random() < 0.25:
            score = float(random.randint(10, 45))
            is_func = False
        else:
            score = float(random.randint(65, 100))
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

    # 3. Crowd Data
    crowds = []
    for i in range(num_crowds):
        lat = CENTER_LAT + np.random.uniform(-LAT_DELTA, LAT_DELTA)
        lng = CENTER_LNG + np.random.uniform(-LNG_DELTA, LNG_DELTA)
        hour = random.randint(0, 23)
        # Peak hours have higher density
        if 8 <= hour <= 20:
            density = float(random.randint(40, 95))
        else:
            density = float(random.randint(5, 50))
        crowds.append({
            "id": i + 1,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "hour_of_day": hour,
            "density_score": density,
            "area_type": random.choice(["commercial", "residential", "park", "transit_hub"])
        })
    df_crowds = pd.DataFrame(crowds)
    df_crowds.to_csv(os.path.join("data", "crowd_data.csv"), index=False)

    # 4. Weather Data
    weather = [{
        "id": 1,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": 18.5,
        "condition_name": "Clear",
        "visibility": 10.0,
        "precipitation": 0.0
    }]
    df_weather = pd.DataFrame(weather)
    df_weather.to_csv(os.path.join("data", "weather_data.csv"), index=False)

    # 5. User Reports
    reports = []
    for i in range(num_reports):
        lat = CENTER_LAT + np.random.uniform(-LAT_DELTA, LAT_DELTA)
        lng = CENTER_LNG + np.random.uniform(-LNG_DELTA, LNG_DELTA)
        cat = random.choice(REPORT_CATEGORIES)
        reports.append({
            "id": i + 1,
            "category": cat,
            "severity": random.randint(1, 5),
            "description": f"Community report: {cat} near street segment",
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "user_id": None,
            "status": "ACTIVE",
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 14))).isoformat()
        })
    df_reports = pd.DataFrame(reports)
    df_reports.to_csv(os.path.join("data", "reports.csv"), index=False)

    print("Sample spatial datasets successfully generated in data/ directory!")

def seed_database():
    print("Seeding database with sample spatial records...")
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(CrimeIncident).count() > 0:
            print("Database already contains records. Skipping seed.")
            return

        # Seed Crimes
        df_crimes = pd.read_csv(os.path.join("data", "crime_data.csv"))
        for _, row in df_crimes.iterrows():
            db.add(CrimeIncident(
                latitude=row["latitude"],
                longitude=row["longitude"],
                crime_type=row["crime_type"],
                severity=row["severity"],
                description=row["description"],
                incident_timestamp=datetime.fromisoformat(row["incident_timestamp"])
            ))

        # Seed Lighting
        df_lights = pd.read_csv(os.path.join("data", "lighting_data.csv"))
        for _, row in df_lights.iterrows():
            db.add(LightingPoint(
                latitude=row["latitude"],
                longitude=row["longitude"],
                lighting_score=row["lighting_score"],
                light_type=row["light_type"],
                is_functional=row["is_functional"]
            ))

        # Seed Crowd
        df_crowds = pd.read_csv(os.path.join("data", "crowd_data.csv"))
        for _, row in df_crowds.iterrows():
            db.add(CrowdData(
                latitude=row["latitude"],
                longitude=row["longitude"],
                hour_of_day=row["hour_of_day"],
                density_score=row["density_score"],
                area_type=row["area_type"]
            ))

        # Seed Weather
        df_weather = pd.read_csv(os.path.join("data", "weather_data.csv"))
        for _, row in df_weather.iterrows():
            db.add(WeatherData(
                temperature=row["temperature"],
                condition_name=row["condition_name"],
                visibility=row["visibility"],
                precipitation=row["precipitation"]
            ))

        # Seed User Reports
        df_reports = pd.read_csv(os.path.join("data", "reports.csv"))
        for _, row in df_reports.iterrows():
            db.add(UserReport(
                category=row["category"],
                severity=row["severity"],
                description=row["description"],
                latitude=row["latitude"],
                longitude=row["longitude"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"])
            ))

        db.commit()
        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_spatial_demo_data()
    Base.metadata.create_all(bind=engine)
    seed_database()
