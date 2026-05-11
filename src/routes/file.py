from fastapi import FastAPI,APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging
from src.helpers.config import get_settings,Settings
from src.controllers import DataController,ProjectController,ProcessController
from src.models import ResponseSignal
from .schema.file import ProccessRequest
from fastapi import Request 
from ..models.repos.data_chunk_repo import DataChunkRepository, DataChunk
from ..models.repos.project_repo import ProjectRepository, Project
base_router=APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)
logger=logging.getLogger('uvicorn.error')
@base_router.post("/upload/{Proj_ID}")
async def Upload(request: Request, proj_ID:str,file:UploadFile,sett: Settings =Depends(get_settings)):
    controllerUp=DataController()
    res,message=controllerUp.Validate_File(file=file)
    if not res:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST
            ,content=message
        )
    else :
        try:
            project_dir=ProjectController().get_proj_dir(proj_ID)
            file_path=os.path.join(project_dir,file.filename)
            async with aiofiles.open(file_path,"wb") as f:
                while chunk:= await file.read(get_settings().FILE_CHUNK_SIZE):
                    await f.write(chunk)
            hash_name=await controllerUp.get_truncated_hash_filename(file_path)
            final_path = os.path.join(project_dir, hash_name)
            os.rename(file_path, final_path)

            project_repo = await ProjectRepository.create_instance(request.app.db_client)
            await project_repo.create_one(Project(project_id=proj_ID, project_name="No_Name"))
            return JSONResponse(
                status_code=status.HTTP_200_OK
                ,content={"Signal":message,"File Name":hash_name}
            )
        except Exception as e:
            logger.error(f"error in file {file.filename}:{e}") 
            JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ResponseSignal.ERROR_UPLOADING.value
            )

@base_router.post("/process/{project_id}")
async def process_file(request:Request,project_id:str,process_request:ProccessRequest):
    project_repo = await ProjectRepository.create_instance(request.app.db_client)
    project = await project_repo.find_or_create_project(project_id=project_id)

    d_cont=DataController()
    p_cont=ProcessController(proj_id=project_id)
    prj_cont = ProjectController()
    file_name=process_request.file_name
    chunk=process_request.chunk_size
    overlap=process_request.overlap_size
    project_dir=prj_cont.get_proj_dir(proj_id=project_id)


    file_path=os.path.join(project_dir,file_name)
    file_content=p_cont.get_file_content(file_path=file_path)
    file_chunks= p_cont.process_file_content(chunk_size=chunk,overlap=overlap,file_content=file_content)
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )

    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order= i + 1,
            chunk_project_id=project_id
        )
        for i, chunk in enumerate(file_chunks)
    ]
    records_length = await p_cont.insert_chunks(request, file_chunks_records, project_id)
    return file_chunks