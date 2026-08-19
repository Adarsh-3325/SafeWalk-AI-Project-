import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "SafeWalk-AI"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # API Keys & Mock Mode
    GOOGLE_MAPS_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    USE_MOCK_DATA: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./safewalk.db"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "safewalk_db"
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    API_V1_PREFIX: str = "/api"
    
    # Frontend & Services
    BACKEND_URL: str = "http://localhost:8000"
    
    # Scoring Weights
    SAFETY_WEIGHT: float = 0.70
    TIME_WEIGHT: float = 0.20
    DISTANCE_WEIGHT: float = 0.10
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
