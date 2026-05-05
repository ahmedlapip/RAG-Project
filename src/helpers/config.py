from pydantic_settings import BaseSettings ,SettingsConfigDict
class settings(BaseSettings):
    APP_NAME:str
    APP_VERSION:str
    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE_MB:int
    class config :
        env_file=".env"
def get_settings():
    return settings()
