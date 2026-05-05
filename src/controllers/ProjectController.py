from .BaseController import BaseController
import os
from fastapi import UploadFile
class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    def get_proj_dir(self,prog_id:str):
        proj_dir=os.path.join(self.files_dir,prog_id)
        if not os.path.exists(proj_dir):
            os.makedirs(proj_dir)
        return proj_dir