from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson import ObjectId

class DataChunk(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id')
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId

    @field_validator('id')
    @classmethod
    def validate_object_id(cls, value: str):
        if not ObjectId.is_valid(value):
            raise ValueError('Object ID Is Not Valid!')

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )