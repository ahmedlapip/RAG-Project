from dotenv import load_dotenv
load_dotenv('.env')
from pathlib import Path
from src.models.db_schemes import db_connection, close_db_connection
from fastapi import FastAPI
from src.routes import base ,File

app = FastAPI()

@app.on_event("startup")
async def startup():
    await db_connection()


@app.get('/')
async def root():
    return {'message': 'Server is up and running!'}

@app.on_event("shutdown")
async def shutdown():
    await close_db_connection()

app.include_router(base.base_router)
app.include_router(File.base_router)