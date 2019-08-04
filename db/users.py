from models import UserInDB, Token
from pymongo.collection import Collection


def get_user(client: Collection, username: str):
    user_dict = client.find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
