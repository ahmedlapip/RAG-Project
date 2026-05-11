from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    class config:
        env_file = ".env"

    # App Details
    APP_NAME: str
    APP_VERSION: str

    # Files Details
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE_MB: int
    FILE_CHUNK_SIZE: int
    # Mongo Configurations
    MONGODB_URI_LOCAL: str
    MONGODB_DB_NAME: str
    MONGODB_DB_PASSWORD: str
    MONGODB_URI_DOCKER_IMAGE: str

    # VectorDB Configurations
    QDRANT_API_URL: str = ""
    QDRANT_API_KEY: str = ""
    VECTOR_DB_NAME: str = "QDrant"
    VECTOR_DB_PATH: str = "./src/assets/qdrant_data"
    VECTOR_DISTANCE_METRIC: str = "cosine"

    # OpenAI API configuration
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""
    GENERATION_BACKEND: str = "Cohere"
    EMBEDDINGS_BACKEND: str = "Cohere"
    GENERATION_MODEL: str = "command-r"
    EMBEDDING_MODEL: str = "embed-multilingual-v3.0"
    EMBEDDING_MODEL_SIZE: int = 1024

    # Cohere API configuration
    COHERE_API_KEY: str = ""

    MAX_CHARACTERS: int = 2048
    MAX_TOKENS: int = 250
    TEMPERATURE: float = 0.1

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()


def get_settings():
    return settings
