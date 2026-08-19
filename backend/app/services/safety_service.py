from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.database_models import CrimeIncident, LightingPoint, CrowdData, WeatherData, UserReport
from backend.app.services.providers import WeatherProvider, OpenWeatherProvider, MockWeatherProvider
from backend.app.core.config import settings

class CrimeService:
    def get_crime_incidents(self, db: Session) -> List[Dict[str, Any]]:
        incidents = db.query(CrimeIncident).all()
        return [
            {
                "latitude": c.latitude,
                "longitude": c.longitude,
                "crime_type": c.crime_type,
                "severity": c.severity,
                "description": c.description
            }
            for c in incidents
        ]

class LightingService:
    def get_lighting_points(self, db: Session) -> List[Dict[str, Any]]:
        lights = db.query(LightingPoint).all()
        return [
            {
                "latitude": l.latitude,
                "longitude": l.longitude,
                "lighting_score": l.lighting_score,
                "light_type": l.light_type,
                "is_functional": l.is_functional
            }
            for l in lights
        ]

class CrowdService:
    def get_crowd_data(self, db: Session, hour_of_day: int = 12) -> List[Dict[str, Any]]:
        crowds = db.query(CrowdData).all()
        return [
            {
                "latitude": c.latitude,
                "longitude": c.longitude,
                "hour_of_day": c.hour_of_day,
                "density_score": c.density_score,
                "area_type": c.area_type
            }
            for c in crowds
        ]

class WeatherService:
    def __init__(self):
        if settings.OPENWEATHER_API_KEY and not settings.USE_MOCK_DATA:
            self.provider: WeatherProvider = OpenWeatherProvider(settings.OPENWEATHER_API_KEY)
        else:
            self.provider: WeatherProvider = MockWeatherProvider()

    def get_current_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        return self.provider.get_weather(lat, lng)

class ReportService:
    def get_user_reports(self, db: Session) -> List[Dict[str, Any]]:
        reports = db.query(UserReport).filter(UserReport.status == "ACTIVE").all()
        return [
            {
                "id": r.id,
                "category": r.category,
                "severity": r.severity,
                "description": r.description,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in reports
        ]

    def create_user_report(self, db: Session, report_data: Dict[str, Any]) -> UserReport:
        report = UserReport(
            category=report_data["category"],
            severity=report_data.get("severity", 1),
            description=report_data.get("description", ""),
            latitude=report_data["latitude"],
            longitude=report_data["longitude"],
            user_id=report_data.get("user_id", None)
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
