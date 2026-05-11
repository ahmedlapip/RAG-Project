from .base_data_repo import BaseDataRepository
from ..enums.db_enums import DatabaseEnum
from ..db_schemes import DataChunk
from pymongo import InsertOne

class DataChunkRepository(BaseDataRepository):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.CHUNK_COLLECTION_NAME.value]

    async def create_one(self, data_chunk: DataChunk):
        return await self.collection.insert_one(data_chunk.model_dump(by_alias=True))

    async def create_many(self, chunks: list[DataChunk], batch_size: int=10000):
        for i in range(0, len(chunks), batch_size):
            batch_end = i + batch_size
            batch = chunks[i:batch_end]
            operations = [
                InsertOne(chunk.model_dump())
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)
        return len(chunks)

    async def find_one_by_id(self, chunk_id: str):
        result = await self.collection.find_one(
            { "_id": ObjectId(chunk_id) }
        )
        if result is None:
            return None

        result["_id"] = str(result["_id"])
        id = result["_id"]
        project = Project(**result)
        project.id = id
        return project.model_dump(by_alias=True)

    async def delete_one_by_id(self, chunk_id: str):
        return await self.collection.delete_one(
            { "_id": ObjectId(chunk_id) }
        )

    async def delete_many(self, data):
        pass

    async def update_one_by_id(self, chunk_id: str, update_data: dict):
        return await self.collection.update_one(
            {
                "_id": ObjectId(chunk_id),
                "$set": update_data
            }
        )

    async def update_many(self, data):
        pass