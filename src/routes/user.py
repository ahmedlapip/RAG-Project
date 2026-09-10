import json
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from .. controllers.ProjectController import ProjectController
from ..models.db_schemes.project import Project
from ..controllers.UserController import UserController
from ..models.db_schemes import db_connection
from pydantic import BaseModel,Field

class Araf(BaseModel):
    project_id: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1)

router = APIRouter()
user_controller = UserController()


@router.post("/users/{user_name}/projects")
async def update_related_projects(req:Request,user_name: str,body:Araf):
    try:
        result = await user_controller.update_related_projects(req.app.db_client, user_name, body.project_id)
        prj=Project(project_id=body.project_id,project_name= body.file_name)
        prj_cnt=ProjectController()
        await prj_cnt.create_project(req, prj)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or project already related")
        return {
            "message": "Related projects updated successfully"
        }
    except Exception as e :
        print(e)

@router.post("/user/specific", status_code=status.HTTP_200_OK)
async def find_all_projects(req: Request,prj_ids:list[str]):
    try:
        result = await user_controller.find_all_projects_user(req, prj_ids)
        if result is None or len(result) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "No Projects Found!"},
            )

        return {
            "message": "Projects Found!",
            "Projects": result
        }

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"Message": "Internal Server Error"},
        )
    
@router.post("/login")
async def login(user_name: str, password: str, db = Depends(db_connection)):
    user = await user_controller.login_user(db, user_name, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Wrong credentials")
    projects = await user_controller.get_related_projects(db, user_name)
    user.pop("_id", None)
    return {
        "message": "Login Success",
        "user": user
    }



@router.post("/register")
async def register(user_name: str, password: str, db = Depends(db_connection)):
    existing_user = await user_controller.get_user_by_name(db, user_name)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user_model = {
        "user_name": user_name,
        "password": password,
        "related_projects": []
    }
    user_id = await user_controller.create_user(db, user_model)
    user_model.pop("_id", None)
    return {
        "message": "User created successfully",
        "user": user_model
    }