from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError

from fastapi import HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED

from config import SECRET_KEY, USER_COLLECTION

from datetime import datetime, timedelta

from db.users import get_user
from db.base import get_client

from document_format import send_csv

from models import TokenData, User, Token


ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: str, collection: str, username: str, password: str):
    user = get_user(get_client(db, collection), username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(get_client(*USER_COLLECTION), username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_authorization(user: User, db: str, collection: str):
    access_dict = user.db_access
    if access_dict is not None:
        if collection in access_dict.get(db):
            return True
    return False


async def authorize(token: Token, db: str, collection: str, return_func, *args, **kwargs):
    user = await get_current_user(token)
    active_user = await get_current_active_user(user)
    if await check_authorization(active_user, db, collection):
        return return_func(*args, **kwargs)
    return HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Unauthorized database access",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def csv_authorize(token: Token, db: str, collection: str, func, filters, email):
    user = await get_current_user(token)
    active_user = await get_current_active_user(user)
    if await check_authorization(active_user, db, collection):
        cursor = func(get_client(db, collection), filters, cursor=True)
        return await send_csv(cursor, email, collection, filters)
    return HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Unauthorized database access",
        headers={"WWW-Authenticate": "Bearer"},
    )
