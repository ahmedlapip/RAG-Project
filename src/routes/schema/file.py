from pydantic import BaseModel
from typing import Optional
class ProccessRequest(BaseModel):
    file_name:str
    chunk_size:Optional[int]=512
    overlap_size:Optional[int]=200
    do_reset:bool=0
