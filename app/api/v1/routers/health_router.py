from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Healthcheck"])

@router.get("/health")
def healthcheck():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
