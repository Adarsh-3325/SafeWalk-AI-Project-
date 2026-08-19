from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "use_mock_data": settings.USE_MOCK_DATA,
        "database": settings.DATABASE_URL.split(":///")[0]
    }
