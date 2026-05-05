from .BaseController import BaseController
from fastapi import UploadFile
from src.models import ResponseSignal
class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def Validate_File(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False,ResponseSignal.FILE_TYPE_ERROR.value
        if (file.size>>20)>self.app_settings.FILE_MAX_SIZE_MB:
            return False,ResponseSignal.FILE_SIZE_LIMIT.value
        return True,ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value