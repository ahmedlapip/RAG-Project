from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController, ProcessController
from src.models import ResponseSignal
from .schema.file import ProccessRequest
from fastapi import Request
from ..models.repos.data_chunk_repo import DataChunkRepository

base_router = APIRouter(prefix="/api/v1/data", tags=["data"])
logger = logging.getLogger("uvicorn.error")


@base_router.post("/upload/{Proj_ID}")
async def Upload(
    proj_ID: str, file: UploadFile, sett: Settings = Depends(get_settings)
):
    controllerUp = DataController()
    res, message = controllerUp.Validate_File(file=file)
    if not res:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=message)
    else:
        try:
            project_dir = ProjectController().get_proj_dir(proj_ID)
            file_path = os.path.join(project_dir, file.filename)
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(get_settings().FILE_CHUNK_SIZE):
                    await f.write(chunk)
            hash_name = await controllerUp.get_truncated_hash_filename(file_path)
            final_path = os.path.join(project_dir, hash_name)
            os.rename(file_path, final_path)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"Signal": message, "File Name": hash_name},
            )
        except Exception as e:
            logger.error(f"error in file {file.filename}:{e}")
            JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ResponseSignal.ERROR_UPLOADING,
            )


@base_router.post("/process/{project_id}")
async def process_file(
    request: Request, project_id: str, process_request: ProccessRequest
):
    p_cont = ProcessController(proj_id=project_id)
    d_cont = DataController()
    prj_cont = ProjectController()

    project_obj = await prj_cont.find_project(request, project_id)
    if not project_obj:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Project not found"},
        )

    mongo_project_id = project_obj["_id"]

    file_name = process_request.file_name
    chunk = process_request.chunk_size
    overlap = process_request.overlap_size
    project_dir = prj_cont.get_proj_dir(proj_id=project_id)

    file_path = os.path.join(project_dir, file_name)
    file_content = p_cont.get_file_content(file_path=file_path)

    if file_content is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "File not found or could not be loaded"},
        )

    file_chunks = p_cont.process_file_content(
        chunk_size=chunk, overlap=overlap, file_content=file_content
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROCESSING_FAILED.value},
        )
    chunks_to_save = p_cont.prepare_chunks_for_db(file_chunks, mongo_project_id)
    inserted_count = await p_cont.insert_chunks(request, chunks_to_save)
    return {"chunks_count": inserted_count, "message": "Chunks saved successfully"}
