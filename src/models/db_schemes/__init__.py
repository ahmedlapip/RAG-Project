from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import os

MONGO_URL_LOCAL = os.getenv('MONGO_URL_LOCAL')
DB_NAME = os.getenv('MONGODB_DB_NAME')
async def db_connection():
    global client, db
    try:
        client = AsyncIOMotorClient(
            MONGO_URL_LOCAL,
            serverSelectionTimeoutMS=5000
        )

        # Force Connection Check
        await client.server_info()

        db = client[DB_NAME]
        print("✅ Connected to MongoDB")

    except ServerSelectionTimeoutError as e:
        print("❌ MongoDB connection failed (timeout):")

    except Exception as e:
        print("❌ Unexpected MongoDB error:")


async def close_db_connection():
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")
