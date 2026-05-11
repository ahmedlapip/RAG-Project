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