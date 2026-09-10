from ..vectorDBInterface import VectorDBInterface
from ..vectorDBEnum import DistanceMethodEnums
from qdrant_client import QdrantClient, models
from src.helpers.config import settings
import asyncio
import uuid


class QDrantProvider(VectorDBInterface):
    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
        db_path: str = None,
        distance_method: str = None,
    ):
        self.client = None
        self.api_url = api_url
        self.api_key = api_key
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

    async def vectorDB_connection(self):
        try:
            if self.api_url and self.api_key:
                self.client = QdrantClient(url=self.api_url, api_key=self.api_key)
            else:
                self.client = QdrantClient(path=self.db_path)

            await asyncio.to_thread(self.client.get_collections)
            print("QDrant Is Connected Successfully")
        except Exception as e:
            print("QDrant Failed To Connect", e)

    def is_collection_exists(self, collection_name: str):
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self):
        return self.client.get_collections

    def get_collection_info(self, collection_name: str):
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.is_collection_exists(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_method
                ),
            )
            print("Collection Created Successfully!")
            return True
        print("Collection Already Exists!")
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: str = None,
    ):
        if not self.is_collection_exists(collection_name=collection_name):
            print("Collection Does Not Exist!")
            return False

        payload = {"text": text}
        if metadata:
            payload["metadata"] = metadata
        if record_id:
            payload["id"] = record_id

        _ = self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=record_id or str(uuid.uuid4()), vector=vector, payload=payload
                )
            ],
        )

        print("Record Inserted Successfully!")
        return True

    def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        record_ids: list = None,
        batch_size: int = 50,
    ):
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_ids = record_ids[i:batch_end]

            batch_points = [
                models.PointStruct(
                    id=batch_ids[idx] or str(uuid.uuid4()),
                    vector=batch_vectors[idx],
                    payload={"text": batch_texts[idx], "metadata": batch_metadata[idx]},
                )
                for idx in range(len(batch_texts))
            ]

            _ = self.client.upsert(collection_name=collection_name, points=batch_points)

        print(f"Records Inserted Successfully! ({len(texts)} records)")
        return True

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        from qdrant_client.models import Filter, FieldCondition, MatchAny

        results = self.client.query_points(
            collection_name=collection_name, query=vector, limit=limit
        )
        return results.points

    def search_by_text(self, collection_name: str, text: str, limit: int = 5):
        return self.client.query_points(
            collection_name=collection_name, query_text=text, limit=limit
        ).points
