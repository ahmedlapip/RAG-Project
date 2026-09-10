from fastapi import Request
from ..models.db_schemes import db_connection
from ..models.repos.project_repo import ProjectRepository
class UserController:

    async def create_user(self, db, user_model):
        users_collection = db["users"] 
        if await users_collection.find_one({"user_name": user_model["user_name"]}):
            raise Exception("Choose another username, this one is already taken")
        result = await users_collection.insert_one(user_model)
        return str(result.inserted_id)

    async def get_user_by_name(self, db, user_name: str)-> dict:
        users_collection = db["users"] 
        user = await users_collection.find_one({"user_name": user_name})
        return user

    async def find_all_projects_user(self, req: Request,prj_ids:list[str]):
        project_repo = ProjectRepository(req.app.db_client)
        return await project_repo.find_specific_pagination(prj_ids)


    async def login_user(self, db, user_name: str, password: str)-> dict:
        user = await self.get_user_by_name(db, user_name)
        if user and user.get("password") == password:
            return user 
        return None
    
    async def get_related_projects(self, db, user_name: str):
        user = await self.get_user_by_name(db, user_name)
        if user and "related_projects" in user:
            return user["related_projects"]
        return []
    
    def update_related_projects(self, db, user_name: str, project_id: str):
        users_collection = db["users"] 
        return users_collection.update_one(
            {"user_name": user_name},
            {"$addToSet": {"related_projects": project_id}}
        )