from dotenv import load_dotenv

from src.routes import file
load_dotenv('.env')
from pathlib import Path
from src.models.db_schemes import db_connection, close_db_connection
from src.stores.vectordb.provider.QdrantDB_provider import QDrantProvider
from src.stores.vectordb.vectorDBProviderFactory import VectorDBProviderFactory
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.routes import base, File, project

app = FastAPI()
app.include_router(project.project_router)
app.include_router(base.base_router)
app.include_router(File.base_router)

@app.on_event("startup")
async def start_server():
    print('Server Is Running On localhost:8000 🚀🚀')
    app.db_client = await db_connection()
    vectorDBProviderFactory = VectorDBProviderFactory()
    await vectorDBProviderFactory.create("QDrant").vectorDB_connection()


@app.get('/')
async def main():
    return {
        'message': 'Home Page!'
    }

@app.on_event("shutdown")
async def close_server():
    print('Server Is Closed Successfully ☠️ ☠️')
    print('QDrant Is Closed Successfully ☠️ ☠️')
    await close_db_connection()


