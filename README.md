<<<<<<< HEAD
# 🛡️ SafeWalk AI - Machine Learning-Based Safety-Aware Route Recommendation System

SafeWalk AI is a complete, production-grade navigation platform that evaluates urban routes using real-world spatial safety factors alongside travel distance and time. Instead of recommending purely the shortest or fastest path, it computes a machine-learning-based **Safety Score** for multiple route alternatives and recommends the safest viable corridor.

---

## 📌 Problem Statement

Traditional GPS navigation systems focus exclusively on distance and travel time. They often direct pedestrians or commuters through poorly lit streets, isolated areas, or high-crime corridors, especially during nighttime hours. SafeWalk AI bridges this gap by incorporating spatial crime history, street lighting lux quality, crowd activity density, weather conditions, time of travel, and citizen safety hazard reports to predict safety risks and recommend safer paths.

---

## ✨ Features & Capabilities

* **Modern Glassmorphic React Frontend**: High-performance UI built with React 18, Vite, Leaflet, Lucide Icons, and Recharts.
* **Interactive Geospatial Map**: Color-coded turn-by-turn road polylines (Emerald=Very Safe, Cyan=Safe, Amber=Moderate, Red=High Risk) with custom pulsing start/destination beacons.
* **Toggleable Spatial Layers**: Live map overlays for Crime Hotspot clusters, Streetlight Lux sensors, Public Crowd activity zones, and Active Citizen hazard alerts.
* **Random Forest ML Risk Model**: Predicts continuous route risk (0–100) using a trained `RandomForestRegressor` with $R^2 > 0.86$ and $MAE < 3.2$.
* **Explainable AI Predictions**: Returns top risk factors (e.g. poor lighting, high crime exposure) and positive safety factors for every route prediction.
* **Multi-Attribute Route Ranking**: Combines ML Safety Score ($70\%$), Travel Time ($20\%$), and Distance ($10\%$) with real-time configurable sliders.
* **Multi-Factor Safety Radar Analytics**: Recharts-powered 6-dimensional radar chart comparing Crime Safety, Lighting Quality, Crowd Footfall, Weather Safety, Daylight Factor, and Citizen Hazard profile.
* **Live Walking Navigation Simulator**: Interactive step-by-step guidance simulator with progress tracking along the route geometry.
* **Emergency SOS Response Hub**: 1-touch GPS distress alert copy, audio siren alarm generator (Web Audio API synth), simulated fake call deterrent, and Delhi helpline speed dials (112, 1091 Women Helpline).
* **Community Safety Reports**: Citizen hazard submission form directly stored in database and live alerts feed.
* **Zero-Config Resilient Fallback**: Automatic mock spatial fallback when external API keys or offline services are used.

---

## 🛠️ Technology Stack

* **Frontend**: React 18, Vite, Leaflet, Lucide React, Recharts, Canvas Confetti, CSS3 Custom Properties
* **Backend**: FastAPI, Pydantic V2, Uvicorn, SQLAlchemy, PyMySQL
* **Machine Learning**: scikit-learn (`RandomForestRegressor`), pandas, NumPy, joblib
* **Routing**: Google Maps Directions API & Mock/OSRM Road Network Provider
* **Database**: MySQL / SQLite
* **Testing**: Pytest, TestClient, HTTPX

---

## 📂 Project Architecture

```
project-root/
│
├── backend/
│   └── app/
│       ├── main.py                     # FastAPI entrypoint
│       ├── api/                        # REST API routes (/routes, /safety, /reports, /health)
│       ├── core/                       # App settings, DB config & logging
│       ├── models/                     # SQLAlchemy ORM models
│       ├── schemas/                    # Pydantic request/response schemas
│       ├── services/                   # Business logic, spatial aggregators & ranking
│       └── ml/                         # ML inference engine & saved models
│
├── frontend/                           # Modern Interactive React Application
│   ├── index.html                      # HTML5 template with custom typography
│   ├── vite.config.js                  # Vite server & API proxy config
│   ├── package.json                    # React dependencies & build scripts
│   └── src/
│       ├── App.jsx                     # Core application orchestrator
│       ├── index.css                   # Glassmorphic cyber-emerald design system
│       ├── api/client.js               # API service layer & resilient mock fallbacks
│       └── components/
│           ├── Header.jsx              # HUD header, status indicators & SOS trigger
│           ├── RouteSearchPanel.jsx    # Origin/Destination, presets & weight sliders
│           ├── MapView.jsx             # Interactive Leaflet map with spatial layers
│           ├── RouteCards.jsx          # Recommended hero card & route explainability
│           ├── SafetyAnalytics.jsx     # Recharts radar & feature importance charts
│           ├── CommunityReports.jsx    # Citizen hazard report modal & live feed
│           ├── EmergencyToolkit.jsx    # SOS distress beacon, siren & fake call
│           ├── SearchHistoryModal.jsx  # Search query history
│           └── TurnByTurnSimulator.jsx # Walking navigation simulator
│
├── ml/                                 # Training pipeline
│   ├── generate_dataset.py             # Synthetic data generator
│   ├── preprocessing.py                # Preprocessor & StandardScaler
│   ├── feature_engineering.py          # Geospatial distance & sampling
│   ├── train.py                        # Model trainer & evaluator
│   └── evaluate.py                     # Evaluation script
│
├── database/                           # DDL Schema
│   └── schema.sql                      # MySQL schema
│
├── data/                               # CSV spatial datasets (crime, lighting, crowd, reports)
└── tests/                              # Pytest test suite
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup & Run

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI Backend Server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup & Run

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite React Development Server
npm run dev
```
Open your browser at: `http://localhost:3000` (or the port shown by Vite).

---

## 🧪 Running Tests

```bash
# Run backend test suite
python -m pytest
```

---

## 📜 License
MIT License. SafeWalk AI Project.
=======
# SafeWalk-AI-Project-
>>>>>>> 9b9fe954b2ca2af9f1b1570943e08735e76b1823
