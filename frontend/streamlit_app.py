import os
import sys
import json
import requests
import streamlit as st

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.components.map import render_route_map
from frontend.components.route_card import render_route_card
from frontend.components.safety_dashboard import render_safety_charts
from frontend.components.reports_ui import render_report_submission_form, render_recent_reports

# Page Configuration
st.set_page_config(
    page_title="SafeWalk AI | Safety-Aware Route Recommendation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 20px;
    }
    .demo-badge {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 12px;
    }
    .stButton>button {
        background-color: #059669;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 48px;
        font-size: 16px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #047857;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-title">🛡️ SafeWalk AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-Powered Machine Learning Safety-Aware Route Recommendation System</p>', unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/security-shield.png", width=64)
    st.markdown("### ⚙️ Navigation Settings")

    hour_of_day = st.slider("🕒 Time of Travel (Hour)", 0, 23, 21, help="Night hours (21:00-06:00) increase lighting & crime risk penalties.")
    is_weekend = st.checkbox("📅 Weekend Travel Mode", value=False)

    st.markdown("---")
    st.markdown("### ⚖️ Route Scoring Weights")
    safety_w = st.slider("Safety Score Weight", 0.0, 1.0, 0.70, 0.05)
    time_w = st.slider("Travel Time Weight", 0.0, 1.0, 0.20, 0.05)
    dist_w = st.slider("Distance Weight", 0.0, 1.0, 0.10, 0.05)

    st.markdown("---")
    st.markdown("### 🤖 ML Model Info")
    st.info("**Model:** Random Forest Regressor\n\n**Features:** Crime Severity, Lighting Score, Crowd Density, Weather, Time, Community Reports.")

# Inputs Form
with st.container():
    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:
        origin = st.text_input("📍 Origin / Start Address", value="37.7749, -122.4194", placeholder="e.g. Financial District, San Francisco")
    with col2:
        destination = st.text_input("🏁 Destination Address", value="37.7925, -122.4012", placeholder="e.g. Mission District, San Francisco")
    with col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_btn = st.button("🔍 FIND SAFEST ROUTE", use_container_width=True)

# Session State Initialization
if "routes_data" not in st.session_state:
    st.session_state["routes_data"] = None

if search_btn or st.session_state["routes_data"] is None:
    if origin and destination:
        with st.spinner("Analyzing routes, sampling geometry, and calculating ML safety scores..."):
            try:
                payload = {
                    "origin": origin,
                    "destination": destination,
                    "hour_of_day": hour_of_day,
                    "is_weekend": 1 if is_weekend else 0
                }
                resp = requests.post(f"{BACKEND_URL}/api/routes/search", json=payload, timeout=4)
                if resp.status_code == 200:
                    st.session_state["routes_data"] = resp.json()
                else:
                    st.error(f"Error fetching routes: {resp.json().get('detail', 'Unknown error')}")
            except Exception:
                # Direct in-process fallback execution if backend HTTP server is offline
                try:
                    from backend.app.services.routing_service import RoutingService
                    from backend.app.ml.predictor import SafetyPredictor
                    from backend.app.services.ranking_service import RouteRankingService
                    from backend.app.services.safety_service import CrimeService, LightingService, CrowdService, WeatherService, ReportService
                    from backend.app.core.database import SessionLocal
                    from ml.feature_engineering import extract_route_safety_features

                    db = SessionLocal()
                    routing_srv = RoutingService()
                    raw_routes = routing_srv.get_route_alternatives(origin, destination)

                    crimes = CrimeService().get_crime_incidents(db)
                    lights = LightingService().get_lighting_points(db)
                    crowds = CrowdService().get_crowd_data(db, hour_of_day=hour_of_day)
                    reports = ReportService().get_user_reports(db)
                    weather = WeatherService().get_current_weather(raw_routes[0]["origin_lat"], raw_routes[0]["origin_lng"])

                    predictor = SafetyPredictor(models_dir=os.path.join("ml", "models"))
                    
                    routes_with_pred = []
                    for r in raw_routes:
                        features = extract_route_safety_features(
                            geometry=r["geometry"],
                            distance_km=r["distance_km"],
                            crimes=crimes,
                            lights=lights,
                            crowd_points=crowds,
                            weather_info=weather,
                            user_reports=reports,
                            hour_of_day=hour_of_day,
                            is_weekend=1 if is_weekend else 0
                        )
                        r["pred"] = predictor.predict_safety(features)
                        routes_with_pred.append(r)

                    ranking_srv = RouteRankingService(safety_weight=safety_w, time_weight=time_w, distance_weight=dist_w)
                    ranked = ranking_srv.rank_routes(routes_with_pred)
                    rec_id = ranked[0]["route_id"] if ranked else ""

                    st.session_state["routes_data"] = {
                        "recommended_route_id": rec_id,
                        "search_timestamp": "Local Execution",
                        "demo_mode": True,
                        "routes": ranked
                    }
                    db.close()
                except Exception as fallback_err:
                    st.error(f"Failed to calculate route safety: {fallback_err}")

data = st.session_state.get("routes_data")

if data:
    demo_mode = data.get("demo_mode", True)
    if demo_mode:
        st.markdown('<div class="demo-badge">⚠️ MOCK DATA DEMO MODE (Missing Google/OpenWeather API keys - using simulated city safety provider)</div>', unsafe_allow_html=True)

    routes = data.get("routes", [])
    recommended_id = data.get("recommended_route_id", "")

    # Application Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Navigation & Map", "📊 Safety Analytics", "📢 Community Reports", "📜 Search History"])

    with tab1:
        map_col, cards_col = st.columns([7, 5])

        with map_col:
            st.markdown("#### Interactive Route Map")
            # Render interactive Folium map
            render_route_map(routes=routes, selected_route_id=recommended_id)

        with cards_col:
            st.markdown("#### Route Alternatives & Safety Scores")
            for r in routes:
                is_rec = (r["route_id"] == recommended_id)
                render_route_card(r, is_recommended=is_rec)

    with tab2:
        # Load ML metadata if available
        meta = None
        meta_file = os.path.join("ml", "models", "feature_metadata.json")
        if os.path.exists(meta_file):
            with open(meta_file, "r") as f:
                meta = json.load(f)

        render_safety_charts(routes=routes, metadata=meta)

    with tab3:
        rep_col1, rep_col2 = st.columns([5, 7])
        with rep_col1:
            render_report_submission_form(BACKEND_URL)
        with rep_col2:
            render_recent_reports(BACKEND_URL)

    with tab4:
        st.markdown("### 📜 Recent Search Queries")
        try:
            h_res = requests.get(f"{BACKEND_URL}/api/routes/history", timeout=5)
            if h_res.status_code == 200:
                history = h_res.json()
                if history:
                    st.dataframe(history, use_container_width=True)
                else:
                    st.info("No search history recorded yet.")
        except Exception:
            st.warning("Could not load history.")

# Safety Disclaimer
st.markdown("---")
st.caption("⚠️ **Safety Disclaimer:** Safety scores are predictive estimations generated by machine learning models based on available historical data (crime, lighting, crowd density, weather, and user reports). They should not be treated as a absolute guarantee of personal safety. Always remain vigilant and aware of your surroundings.")
