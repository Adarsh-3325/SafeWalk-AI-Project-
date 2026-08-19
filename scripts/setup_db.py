import os
import sys

# Ensure root folder is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import engine, Base
from backend.app.models.database_models import (
    User, RouteModel, RoutePrediction, CrimeIncident, LightingPoint,
    CrowdData, WeatherData, UserReport, SearchHistory, ModelPredictionLog
)
from backend.app.core.logging_config import logger, setup_logging

def init_db():
    setup_logging()
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e

if __name__ == "__main__":
    init_db()
