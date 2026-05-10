from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from ..models.db_schemes import Project
from ..models.db_schemes.project import ProjectUpdate
from ..models.repos.project_repo import ProjectRepository
from ..controllers.ProjectController import ProjectController

projectController = ProjectController()

project_router = APIRouter(
    prefix='/api/v1/project'
)

@project_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_project(req: Request, project: Project):
    try:
        result = await projectController.create_project(req, project)

        if not result:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "Failed To Create The Project!"
                }
            )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Project Created Successfully!"
            }
        )
        return result
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "Message": "Internal Server Error"
            }
        )

@project_router.get('/{project_id}', status_code=status.HTTP_200_OK)
async def find_project(req: Request, project_id: str):
    try:
        result = await projectController.find_project(req, project_id)
        if not result:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "Project Not Found!"
                }
            )

        # result["_id"] = str(result["_id"])
        return result
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "Message": "Internal Server Error"
            }
        )

@project_router.patch('/{_id}', status_code=status.HTTP_200_OK)
async def update_project(req: Request, _id: str, body: ProjectUpdate):
    try:
        update_data = {
            k: v for k, v in body.dict().items()
            if v is not None
        }

        result = await projectController.update_project(req, _id, update_data)
        if result.modified_count == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "No Projects Founds To Update!"
                }
            )

        return {
            "message": "Project Updated Successfully!"
        }
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "Message": "Internal Server Error"
            }
        )

@project_router.delete('/{project_id}', status_code=status.HTTP_200_OK)
async def delete_project(req: Request, project_id: str):
    try:
        result = await projectController.delete_project(req, project_id)
        if result.deleted_count == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "No Projects Founds To Delete!"
                }
            )

        return {
            "message": "Project Deleted Successfully!"
        }
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "Message": "Internal Server Error"
            }
        )