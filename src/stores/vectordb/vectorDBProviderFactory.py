from .provider.QdrantDB_provider import QDrantProvider
from .vectorDBEnum import VectorDBEnums
from ...helpers.config import settings
from ...controllers.BaseController import BaseController

class VectorDBProviderFactory:
    def __init__(self):
        self.base_controller = BaseController()

    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(settings.VECTOR_DB_NAME)
            return QDrantProvider(
                db_path=db_path,
                distance_method=settings.VECTOR_DISTANCE_METRIC
            )
        return None