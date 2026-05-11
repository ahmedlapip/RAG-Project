from fastapi import FastAPI, APIRouter
from src.helpers.config import settings

base_router=APIRouter(
    prefix="/api/v1"
)
@base_router.get("/")
async def welcome():
    app_name = settings.APP_NAME | " "
    app_ver = settings.APP_VERSION | " "
    return {
        "Name": app_name,
        "ver": app_ver
    }