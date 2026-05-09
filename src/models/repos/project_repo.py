from .base_data_repo import BaseDataRepository
from ..enums.db_enums import DatabaseEnum
from ..db_schemes import Project
from bson import ObjectId

class ProjectRepository(BaseDataRepository):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.PROJECT_COLLETION_NAME.value]

    async def create_one(self, project: Project):
        return await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))

    async def create_many(self, projects: list[Project]):
        pass

    async def find_one_by_id(self, project_id: str):
        result = await self.collection.find_one(
            { "_id": ObjectId(project_id) }
        )
        if result is None:
            return None

        result["_id"] = str(result["_id"])
        id = result["_id"]
        project = Project(**result)
        project.id = id
        return project.model_dump(by_alias=True)

    async def delete_one_by_id(self, project_id: str):
        return await self.collection.delete_one(
            { "_id": ObjectId(project_id) }
        )

    async def delete_many(self, data):
        pass

    async def update_one_by_id(self, project_id: str, update_data: dict):
        return await self.collection.update_one(
            { "_id": ObjectId(project_id) },
            { "$set": update_data }
        )

    async def update_many(self, data):
        pass