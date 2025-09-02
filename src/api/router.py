from fastapi import APIRouter
from src.api import auth


api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth/api", tags=["API Authentication"])
