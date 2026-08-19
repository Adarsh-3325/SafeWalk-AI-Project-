from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_reports = relationship("UserReport", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")

class RouteModel(Base):
    __tablename__ = "routes"
    
    id = Column(String(64), primary_key=True, index=True)
    origin_address = Column(String(255), nullable=False)
    destination_address = Column(String(255), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    geometry_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    predictions = relationship("RoutePrediction", back_populates="route", cascade="all, delete-orphan")

class RoutePrediction(Base):
    __tablename__ = "route_predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id = Column(String(64), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    ml_safety_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    final_score = Column(Float, nullable=False)
    crime_risk = Column(Float, nullable=False)
    lighting_score = Column(Float, nullable=False)
    crowd_score = Column(Float, nullable=False)
    weather_risk = Column(Float, nullable=False)
    time_risk = Column(Float, nullable=False)
    report_risk = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    route = relationship("RouteModel", back_populates="predictions")

class CrimeIncident(Base):
    __tablename__ = "crime_incidents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    crime_type = Column(String(50), nullable=False)
    severity = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    incident_timestamp = Column(DateTime, default=datetime.utcnow)

class LightingPoint(Base):
    __tablename__ = "lighting_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    lighting_score = Column(Float, nullable=False) # 0 to 100
    light_type = Column(String(50), default="street_lamp")
    is_functional = Column(Boolean, default=True)

class CrowdData(Base):
    __tablename__ = "crowd_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    hour_of_day = Column(Integer, nullable=False)
    density_score = Column(Float, nullable=False) # 0 to 100
    area_type = Column(String(50), default="commercial")

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float, nullable=False)
    condition_name = Column(String(50), nullable=False)
    visibility = Column(Float, nullable=False)
    precipitation = Column(Float, nullable=False)

class UserReport(Base):
    __tablename__ = "user_reports"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    severity = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="user_reports")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    selected_route_id = Column(String(64), nullable=True)
    search_time = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="search_history")

class ModelPredictionLog(Base):
    __tablename__ = "model_predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id = Column(String(64), nullable=False)
    raw_features_json = Column(Text, nullable=False)
    predicted_risk = Column(Float, nullable=False)
    top_risk_factors_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
