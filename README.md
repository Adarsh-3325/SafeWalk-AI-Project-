# 🛡️ SafeWalk AI - Machine Learning-Based Safety-Aware Route Recommendation System

SafeWalk AI is a complete, production-grade navigation system that evaluates urban routes using real-world safety factors alongside travel distance and time. Instead of recommending purely the shortest or fastest path, it computes a machine-learning-based **Safety Score** for multiple route alternatives and recommends the safest viable route.

---

## 📌 Problem Statement

Traditional GPS navigation systems focus exclusively on distance and travel time. They often direct pedestrians or commuters through poorly lit streets, isolated areas, or high-crime corridors, especially during nighttime hours. SafeWalk AI bridges this gap by incorporating crime history, street lighting quality, crowd density, weather conditions, time of travel, and community safety reports to predict safety risks and recommend safer paths.

---

## ✨ Features

* **Multi-Route Generation**: Fetches route alternatives between source and destination (Google Maps API or OSRM/Mock Provider).
* **Geospatial Feature Sampling**: Samples polylines every $N$ meters to query nearby spatial crime, street lighting, crowd levels, and community safety reports using Haversine distance.
* **Random Forest ML Risk Model**: Predicts continuous route risk (0–100) using a trained `RandomForestRegressor` with $R^2 > 0.86$ and $MAE < 3.2$.
* **Explainable AI Predictions**: Returns top risk factors (e.g. poor lighting, high crime exposure) and positive safety factors for every route prediction.
* **Multi-Attribute Route Ranking**: Combines ML Safety Score ($70\%$), Travel Time ($20\%$), and Distance ($10\%$) with configurable weights.
* **Interactive Folium Map**: Color-coded route polylines (Green=Safest, Blue=Safe, Orange=Moderate, Red=Risky) with markers for incidents and community reports.
* **Safety Dashboard**: Interactive Plotly bar and radar charts comparing multi-factor risk profiles across routes.
* **Community Safety Reports**: User report submission form and persistent database storage for community hazards.
* **Zero-Config Fallback / Demo Mode**: Automatic fallback to simulated spatial providers (`USE_MOCK_DATA=true`) when external API keys are omitted.
* **Dual Database Support**: Direct support for MySQL schema (`database/schema.sql`) and automatic SQLite fallback.

---

## 🛠️ Technology Stack

* **Frontend**: Streamlit, Streamlit-Folium, Plotly, HTML/CSS
* **Backend**: FastAPI, Pydantic V2, Uvicorn, SQLAlchemy, PyMySQL
* **Machine Learning**: scikit-learn (`RandomForestRegressor`), pandas, NumPy, joblib
* **Routing**: Google Maps Directions API & Mock/OSRM Provider
* **Database**: MySQL / SQLite
* **Testing**: Pytest, TestClient, HTTPX
* **Containerization**: Docker, Docker-Compose

---

## 📂 Project Architecture

```
project-root/
│
├── backend/
│   └── app/
│       ├── main.py                     # FastAPI entrypoint
│       ├── api/                        # REST API routes
│       │   ├── health.py               # /health endpoint
│       │   ├── routes.py               # /api/routes/search & history
│       │   ├── safety.py               # /api/safety/predict & details
│       │   └── reports.py              # /api/reports POST/GET
│       ├── core/                       # App settings & DB configuration
│       │   ├── config.py
│       │   ├── database.py
│       │   └── logging_config.py
│       ├── models/                     # SQLAlchemy ORM models
│       │   └── database_models.py
│       ├── schemas/                    # Pydantic request/response schemas
│       │   ├── route_schema.py
│       │   ├── safety_schema.py
│       │   └── report_schema.py
│       ├── services/                   # Provider abstractions & business logic
│       │   ├── providers.py            # Routing & Weather providers
│       │   ├── routing_service.py
│       │   ├── safety_service.py       # Spatial feature aggregators
│       │   └── ranking_service.py      # Multi-attribute route ranking
│       └── ml/                         # ML inference module
│           ├── predictor.py
│           └── models/                 # Saved model joblib artifacts
│
├── frontend/                           # Streamlit dashboard
│   ├── streamlit_app.py
│   └── components/
│       ├── map.py                      # Interactive Folium map
│       ├── route_card.py               # Visual route summary cards
│       ├── safety_dashboard.py        # Plotly analytics charts
│       └── reports_ui.py               # Community report forms
│
├── ml/                                 # Training pipeline
│   ├── generate_dataset.py             # Synthetic data generator
│   ├── preprocessing.py                # Preprocessor & StandardScaler
│   ├── feature_engineering.py          # Geospatial distance & sampling
│   ├── train.py                        # Model trainer & evaluator
│   ├── evaluate.py                     # Evaluation script
│   └── predict.py                      # Offline CLI predictor
│
├── database/                           # DDL Schema
│   └── schema.sql                      # MySQL schema
│
├── data/                               # CSV datasets
│   ├── ml_safety_dataset.csv
│   ├── crime_data.csv
│   ├── lighting_data.csv
│   ├── crowd_data.csv
│   ├── weather_data.csv
│   └── reports.csv
│
├── scripts/                            # DB Setup & Seed scripts
│   ├── setup_db.py
│   └── generate_sample_data.py
│
├── tests/                              # Pytest test suite
│   ├── test_api.py
│   ├── test_ml.py
│   ├── test_routing.py
│   └── test_safety.py
│
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🤖 ML Methodology & Features

### Feature Variables
1. **Crime Factors**: `crime_incident_count`, `crime_density`, `weighted_crime_severity`, `min_dist_recent_crime_m`.
2. **Lighting Factors**: `lighting_score_avg`, `dark_segment_pct`.
3. **Crowd Density**: `crowd_density_avg`, `isolated_segment_pct`.
4. **Weather**: `temp_celsius`, `visibility_km`, `precipitation_mm`, `weather_severity`.
5. **Time**: `hour_of_day`, `is_weekend`, `is_night`, `is_peak_hour`.
6. **Community Reports**: `user_report_count`, `weighted_user_reports`, `report_density`.

### Model Metrics
* **Model Type**: `RandomForestRegressor` ($N=150$, `max_depth=15`)
* **Mean Absolute Error (MAE)**: `3.1895`
* **Root Mean Squared Error (RMSE)**: `4.0336`
* **R-squared ($R^2$)**: `0.8612`

---

## 🚀 Quickstart Guide

### 1. Local Setup

```bash
# Clone the repository
git clone <repository_url>
cd "Safe Walk Project Anti-gravity"

# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database & Data Setup

```bash
# Initialize DB tables (SQLite safewalk.db by default)
python scripts/setup_db.py

# Generate training dataset
python ml/generate_dataset.py

# Seed spatial demo data (SF area)
python scripts/generate_sample_data.py

# Train Random Forest Safety Model
python ml/train.py
```

### 3. Run Backend API

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Access OpenAPI Docs at: `http://localhost:8000/docs`

### 4. Run Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```
Access Frontend Dashboard at: `http://localhost:8501`

---

## 🧪 Running Automated Tests

```bash
python -m pytest tests/
```

---

## 🐳 Docker Setup

Run the entire stack (FastAPI Backend, Streamlit Frontend, and MySQL Database) with a single command:

```bash
docker compose up --build
```

---

## ⚠️ Safety Disclaimer

*Safety scores are predictions based on available data and should not be treated as a guarantee of personal safety.*
