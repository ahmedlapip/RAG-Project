from .base_data_repo import BaseDataRepository
from ..enums.db_enums import DatabaseEnum
from ..db_schemes import Project
from bson import ObjectId

class ProjectRepository(BaseDataRepository):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.PROJECT_COLLETION_NAME.value]

    async def init_collections(self):
        all_collections = await self.db_client.list_collection_names()

        if DatabaseEnum.PROJECT_COLLETION_NAME.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.PROJECT_COLLETION_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collections()
        return instance

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

    async def find_one_by_project_id(self, project_id: str):
        result = await self.collection.find_one(
            { "project_id": project_id }
        )

        if result is None:
            return None

        result["_id"] = str(result["_id"])
        id = result["_id"]
        project = Project(**result)
        project.id = id
        return project.model_dump(by_alias=True)

    async def find_or_create_project(self, project_id: str):
        record = await self.collection.find_one({
            "project_id": project_id
        })

        if record is None:
            project = Project(project_id=project_id, project_name="No_Name_Provided!")
            project = await self.create_one(project=project)
            return project

        record["_id"] = str(record["_id"])
        id = record["_id"]
        project = Project(**record)
        project.id = id
        return project.model_dump(by_alias=True)

    async def delete_one_by_id(self, project_id: str):
        return await self.collection.delete_one(
            { "_id": ObjectId(project_id) }
        )

    async def find_all_pagination(self, page: int=1, page_size: int=5):
        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []

        async for document in cursor:
            document["_id"] = str(document["_id"])
            id = document["_id"]
            project = Project(**document)
            project.id = id
            projects.append(project.model_dump(by_alias=True))

        return projects, total_pages

    async def delete_many(self, data):
        pass

    async def update_one_by_id(self, project_id: str, update_data: dict):
        return await self.collection.update_one(
            { "_id": ObjectId(project_id) },
            { "$set": update_data }
        )

    async def update_many(self, data):
        pass