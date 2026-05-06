from dotenv import load_dotenv

from src.routes import file
load_dotenv('.env')
from fastapi import FastAPI
from src.routes import base
app =FastAPI()
app.include_router(base.base_router)
app.include_router(file.base_router)