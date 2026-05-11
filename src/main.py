from dotenv import load_dotenv

load_dotenv(".env")
from pathlib import Path
from src.models.db_schemes import db_connection, close_db_connection
from src.stores.vectordb.provider.QdrantDB_provider import QDrantProvider
from src.stores.vectordb.vectorDBProviderFactory import VectorDBProviderFactory
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.routes import file, project, user

app = FastAPI(
    title="RAG API", description="Retrieval-Augmented Generation API", version="1.0.0"
)
app.include_router(project.project_router)
app.include_router(file.base_router)
app.include_router(user.router)

@app.on_event("startup")
async def start_server():
    print("Server Is Running On localhost:8000 🚀🚀")
    app.db_client = await db_connection()
    vectorDBProviderFactory = VectorDBProviderFactory()
    await vectorDBProviderFactory.create("QDrant").vectorDB_connection()


@app.get("/")
async def root():
    return {"message": "RAG API", "docs": "/docs", "redoc": "/redoc"}


@app.on_event("shutdown")
async def close_server():
    print("Server Is Closed Successfully ☠️ ☠️")
    print("QDrant Is Closed Successfully ☠️ ☠️")
    await close_db_connection()
