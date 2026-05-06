import hashlib
from .BaseController import BaseController
from fastapi import UploadFile
from src.models import ResponseSignal
import os
from src.helpers.config import get_settings
import aiofiles
class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def Validate_File(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False,ResponseSignal.FILE_TYPE_ERROR.value
        if (file.size>>20)>self.app_settings.FILE_MAX_SIZE_MB:
            return False,ResponseSignal.FILE_SIZE_LIMIT.value
        return True,ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value

    async def get_truncated_hash_filename(self,filepath, length=16):
        hasher = hashlib.sha256()
        async with aiofiles.open(filepath, 'rb') as f:
            while chunk := await f.read(get_settings().FILE_CHUNK_SIZE):
                hasher.update(chunk)
        full_hash = hasher.hexdigest()
        short_hash = full_hash[:length]
        ext = os.path.splitext(filepath)[1]
        return f"{short_hash}{ext}"
