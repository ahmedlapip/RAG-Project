from abc import ABC, abstractmethod
from pydantic import BaseModel

class BaseDataRepository(ABC):
    def __init__(self, db_client: object):
        self.db_client = db_client

    @abstractmethod
    async def create_one(self, project: BaseModel):
        pass

    @abstractmethod
    async def create_many(self, data: list[BaseModel]):
        pass

    @abstractmethod
    async def find_one_by_id(self, id: str):
        pass

    @abstractmethod
    async def delete_one_by_id(self, id: str):
        pass

    @abstractmethod
    async def delete_many(self, data):
        pass

    @abstractmethod
    async def update_one_by_id(self, id: str, update_data: dict):
        pass

    @abstractmethod
    async def update_many(self, data):
        pass