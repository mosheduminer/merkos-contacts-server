from db.users import get_user
from security import get_current_user

from models import Token
from pymongo.collection import Collection


async def get_user_email(client: Collection, token: Token):
    user = await get_current_user(token)
    return user.email