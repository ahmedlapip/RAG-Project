from .provider.QdrantDB_provider import QDrantProvider
from .vectorDBEnum import VectorDBEnums
from ...helpers.config import settings


class VectorDBProviderFactory:
    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value or provider == "QDrant":
            return QDrantProvider(
                db_path=settings.VECTOR_DB_PATH,
                distance_method=settings.VECTOR_DISTANCE_METRIC,
            )
        return None
