from fastapi import FastAPI,APIRouter,Depends
import os
from src.helpers.config import get_settings,settings
base_router=APIRouter(
    prefix="/api/v1"
)
@base_router.get("/")
async def welcome(sett: settings =Depends(get_settings)):
    app_name=sett.APP_NAME
    app_ver=sett.APP_VERSION
    return{
        "Name":app_name,"ver":app_ver
    }