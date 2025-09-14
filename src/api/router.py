from fastapi import APIRouter
from src.api import auth
from src.api import document

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth/api", tags=["API Authentication"])
api_router.include_router(
    document.router, prefix="/documents/api", tags=["Document Management"]
)
