import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.core.logging_config import logger, setup_logging
from backend.app.ml.predictor import SafetyPredictor

# Import API Routers
from backend.app.api.health import router as health_router
from backend.app.api.routes import router as routes_router, set_predictor as set_routes_predictor
from backend.app.api.safety import router as safety_router, set_predictor as set_safety_predictor
from backend.app.api.reports import router as reports_router

setup_logging()

app = FastAPI(
    title="SafeWalk A Safety-Aware Route Recommendation",
    description="AI-Powered Machine Learning Safety-Aware Urban Route Recommendation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing DB tables on startup if not present...")
    Base.metadata.create_all(bind=engine)

    models_dir = os.path.join(os.path.dirname(__file__), "ml", "models")
    if not os.path.exists(os.path.join(models_dir, "safety_model.joblib")):
        logger.info("Model artifacts not found in backend. Training default model...")
        from ml.train import train_safety_model
        train_safety_model()

    logger.info("Loading Random Forest safety predictor into memory...")
    predictor = SafetyPredictor(models_dir=models_dir)
    set_routes_predictor(predictor)
    set_safety_predictor(predictor)
    logger.info("SafetyPredictor loaded successfully!")

# Include Routers with Prefix
app.include_router(health_router)
app.include_router(routes_router, prefix=settings.API_V1_PREFIX)
app.include_router(safety_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.BACKEND_HOST, port=settings.BACKEND_PORT)
