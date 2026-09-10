from dotenv import load_dotenv

load_dotenv(".env")
from src.models.db_schemes import db_connection, close_db_connection
from src.stores.vectordb.vectorDBProviderFactory import VectorDBProviderFactory
from src.stores.llm.LLMProvideFactory import get_llm_provider
from src.helpers.config import get_settings
from fastapi import FastAPI

from src.routes import file, project
from src.routes.NLP import nlp_router

settings = get_settings()
from fastapi.responses import JSONResponse
from src.routes import file, project, user

app = FastAPI(
    title="RAG API", description="Retrieval-Augmented Generation API", version="1.0.0"
)
app.include_router(project.project_router)
app.include_router(file.base_router)

app.include_router(nlp_router)

llm_provider = get_llm_provider()
llm_provider.set_model(settings.GENERATION_MODEL)
llm_provider.set_embedding_model(
    settings.EMBEDDING_MODEL, settings.EMBEDDING_MODEL_SIZE
)

app.llm_provider = llm_provider
app.include_router(user.router)


@app.on_event("startup")
async def start_server():
    print("Server Is Running On localhost:8000")
    app.state.settings = settings
    app.db_client = await db_connection()
    vectorDBProviderFactory = VectorDBProviderFactory()
    await vectorDBProviderFactory.create(settings.VECTOR_DB_NAME).vectorDB_connection()


@app.get("/")
async def root():
    return {"message": "RAG API", "docs": "/docs", "redoc": "/redoc"}


@app.on_event("shutdown")
async def close_server():
    print("Server Is Closed Successfully")
    print("QDrant Is Closed Successfully")
    await close_db_connection()
