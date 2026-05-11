from .base_data_repo import BaseDataRepository
from ..enums.db_enums import DatabaseEnum
from ..db_schemes import DataChunk
from pymongo import InsertOne
import json

class DataChunkRepository(BaseDataRepository):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.CHUNK_COLLECTION_NAME.value]

    async def init_collections(self):
        all_collections = await self.db_client.list_collection_names()

        if DatabaseEnum.CHUNK_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.CHUNK_COLLECTION_NAME.value]
            indexes = DataChunk.get_indexes()

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

    async def create_one(self, data_chunk: DataChunk):
        return await self.collection.insert_one(data_chunk.model_dump(by_alias=True))

    async def create_many(self, chunks: list[DataChunk], project_id: str, batch_size: int=10000):
        total_inserted = 0
        for i in range(0, len(chunks), batch_size):
            batch_end = i + batch_size
            batch = chunks[i:batch_end]
            operations = [
                InsertOne(chunk.model_dump())
                for chunk in batch
            ]
            try:
                result = await self.collection.bulk_write(
                    operations,
                    ordered=True
                )
                total_inserted += result.inserted_count

            except Exception as e:
                print(f"Batch insert failed at {i}: {e}")
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

    async def find_chunks_by_id_pagination(self, project_id: str, page: int, page_size: int):
        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find({
            "chunk_project_id": project_id
        }).skip((page - 1) * page_size).limit(page_size)
        chunks = []

        async for document in cursor:
            document["_id"] = str(document["_id"])
            id = document["_id"]
            chunk = DataChunk(**document)
            chunk.id = id
            chunks.append(chunk.model_dump(by_alias=True))

        return chunks, total_pages

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