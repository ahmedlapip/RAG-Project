from .base_data_repo import BaseDataRepository
from ..enums.db_enums import DatabaseEnum
from ..db_schemes.asset import Asset
from bson import ObjectId

class AssetRepository(BaseDataRepository):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.ASSET_COLLECTION_NAME.value]

    async def init_collections(self):
        all_collections = await self.db_client.list_collection_names()

        if DatabaseEnum.ASSET_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.ASSET_COLLECTION_NAME.value]
            indexes = Asset.get_indexes()
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

    async def create_one(self, asset: Asset):
        return await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))

    async def find_asset_by_asset_name_project_id(self, asset_project_id: str):
        result = await self.collection.find_one({
            "asset_project_id": asset_project_id,
            "asset_name": asset_name
        })

        if result is None:
            return None

        result["_id"] = str(result["_id"])
        id = result["_id"]
        project = Project(**result)
        project.id = id
        return project.model_dump(by_alias=True)

    async def get_all_project_assets(self, asset_project_id: str):
        records = await self.collection.find({
            "asset_project_id": asset_project_id
        }).to_list(length=None)

        result = []
        for rec in records:
            rec["_id"] = str(rec["_id"])
            id = rec["_id"]
            project = Project(**rec)
            project.id = id
            result.append(project.model_dump(by_alias=True))

        return result