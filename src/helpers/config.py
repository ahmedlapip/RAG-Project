from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    class config :
        env_file=".env"
    # App Details
    APP_NAME:str
    APP_VERSION:str

    # Files Details
    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE_MB:int
    FILE_CHUNK_SIZE:int
    # Mongo Configurations
    MONGODB_URI_LOCAL: str
    MONGODB_DB_NAME: str
    MONGODB_DB_PASSWORD: str
    MONGODB_URI_DOCKER_IMAGE: str

    # VectorDB Configurations
    QDRANT_API_URL: str
    QDRANT_API_KEY: str
    VECTOR_DB_NAME: str
    VECTOR_DB_PATH: str
    VECTOR_DISTANCE_METRIC: str

    # OpenAI API configuration
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str#https://160a-3.ngrok-free.app/v1/
    GENERATE_RESPONSE_MODEL: str
    EMBEDDINGS_MODEL: str
    EMBEDDING_DIMENSION: str
    MAX_INPUT_TOKENS: str
    MAX_RESPONSE_TOKENS: str
    TEMPERATURE: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )
settings = Settings()
def get_settings():
    return settings()
