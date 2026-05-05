from src.helpers.config import get_settings,settings
import os
class BaseController():
    def __init__(self):
        self.app_settings=get_settings()
        self.path_dir=os.path.dirname(os.path.dirname(__file__))
        self.files_dir=os.path.join(self.path_dir,"assets/files")
        
