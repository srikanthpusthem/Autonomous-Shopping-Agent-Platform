from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.feedback import router as feedback_router
from app.api.health import router as health_router
from app.api.profiles import router as profiles_router
from app.api.runs import router as runs_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profiles_router)
api_router.include_router(runs_router)
api_router.include_router(feedback_router)
