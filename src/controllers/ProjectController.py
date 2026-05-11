from .BaseController import BaseController
import os
from fastapi import UploadFile, Request
from ..models.db_schemes import Project
from ..models.repos.project_repo import ProjectRepository

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    def get_proj_dir(self,proj_id:str):
        proj_dir=os.path.join(self.files_dir,proj_id)
        if not os.path.exists(proj_dir):
            os.makedirs(proj_dir)
        return proj_dir

    async def create_project(self, req: Request, project: Project):
        project_repo = await ProjectRepository.create_instance(req.app.db_client)
        return await project_repo.create_one(project)

    async def find_project(self, req: Request, project_id: str):
        project_repo = await ProjectRepository.create_instance(req.app.db_client)
        #return await project_repo.find_one_by_id(project_id)
        return await project_repo.find_one_by_project_id(project_id)
    
    async def find_all_projects(self, req: Request, page=1, page_size: int=5):
        project_repo = await ProjectRepository.create_instance(req.app.db_client)
        return await project_repo.find_all_pagination(page, page_size)
    
    async def update_project(self, req: Request, project_id: str, update_data: Project):
        project_repo = await ProjectRepository.create_instance(req.app.db_client)
        return await project_repo.update_one_by_id(project_id, update_data)

    async def delete_project(self, req: Request, project_id: str):
        project_repo = await ProjectRepository.create_instance(req.app.db_client)
        return await project_repo.delete_one_by_id(project_id)
