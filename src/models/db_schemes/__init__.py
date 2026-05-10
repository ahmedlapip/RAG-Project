from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from src.helpers.config import settings
from .data_chunk import DataChunk
from .project import Project

async def db_connection():
    # MONGO_URL_LOCAL = settings.MONGODB_URI_LOCAL
    MONGODB_URI_DOCKER_IMAGE = settings.MONGODB_URI_DOCKER_IMAGE
    DB_NAME = settings.MONGODB_DB_NAME
    global client, db
    try:
        client = AsyncIOMotorClient(
            # MONGO_URL_LOCAL,
            MONGODB_URI_DOCKER_IMAGE,
            serverSelectionTimeoutMS=5000
        )
        # Force Connection Check
        await client.server_info()

        print("MongoDB Is Connected Successfully ✅✅")
        return client[DB_NAME]

    except ServerSelectionTimeoutError as e:
        print("MongoDB Connection Failed (timeout) ❌❌")

    except Exception as e:
        print("Unexpected MongoDB Error ❌❌")


async def close_db_connection():
    global client
    if client:
        client.close()
        print("MongoDB Connection Is Closed 🔌🔌")
