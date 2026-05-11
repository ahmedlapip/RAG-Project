import json
import bson
from fastapi import APIRouter, Depends, HTTPException
from ..controllers.UserController import UserController
from ..models.db_schemes import db_connection


router = APIRouter()
user_controller = UserController()

@router.post("/login")
async def login(user_name: str, password: str, db = Depends(db_connection)):
    user = await user_controller.login_user(db, user_name, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Wrong credentials")
    projects = await user_controller.get_related_projects(db, user_name)
    user.pop("_id", None)
    return {
        "message": "Login Success",
        "user": user,
        "projects": projects
    }

@router.post("/register")
async def register(user_name: str, password: str, db = Depends(db_connection)):
    existing_user = await user_controller.get_user_by_name(db, user_name)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user_model = {
        "user_name": user_name,
        "password": password,
        "related_projects": []
    }
    user_id = await user_controller.create_user(db, user_model)
    user_model.pop("_id", None)
    return {
        "message": "User created successfully",
        "user": user_model
    }