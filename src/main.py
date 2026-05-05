from dotenv import load_dotenv
load_dotenv('.env')
from fastapi import FastAPI
from src.routes import base ,File
app =FastAPI()
app.include_router(base.base_router)
app.include_router(File.base_router)