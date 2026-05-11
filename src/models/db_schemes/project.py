from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson import ObjectId

class ProjectUpdate(BaseModel):
    # project_id: Optional[str] = Field(..., min_length=1)
    project_name: Optional[str] = Field(..., min_length=1)

class ProjectId(BaseModel):
    project_id: Optional[str] = Field(..., min_length=1)

class Project(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id')
    project_id: str = Field(..., min_length=1)
    project_name: str = Field(..., min_length=1)

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, value: str):
        if not value.isalnum():
            raise ValueError('Project ID Must Be Alpha Numeric')
        return value

    @field_validator('id')
    @classmethod
    def validate_object_id(cls, value: str):
        if not ObjectId.is_valid(value):
            raise ValueError('Object ID Is Not Valid!')

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("project_id", 1)
                ],
                "name": "project_id_index1",
                "unique": True
            }
        ]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        populate_by_name=True
    )
