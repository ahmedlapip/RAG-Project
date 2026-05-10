from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from src.helpers.config import settings
from src.controllers import DataController

base_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

dataController = DataController()

@base_router.post("/upload/{Proj_ID}")
async def Upload(Proj_ID:str, file:UploadFile):
    res, message = dataController.Validate_File(file=file)
    if not res:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=message
        )
    else:
        return JSONResponse(
            status_code= status.HTTP_200_OK,
            content= message
        )
