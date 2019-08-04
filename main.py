from fastapi import FastAPI, Body, Depends, HTTPException

from models import ContactModel, UpdateContactModel, Token

from db.base import get_client, get_collections
from db.contacts import (create_new_contact, read_contact_by_attr, read_contact_by_id,
                        read_contact_by_attr_contains, update_contact, delete_contact)
from db.cities import get_cities, get_city_data, new_city_data

from db.users import get_user
from security import (oauth2_scheme, get_current_user, get_current_active_user, authenticate_user,
                      create_access_token, authorize, csv_authorize)
from datetime import timedelta
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi.security import OAuth2PasswordRequestForm

from db.email import get_user_email

from config import USER_COLLECTION

from typing import List, Dict

app = FastAPI()


ACCESS_TOKEN_EXPIRE_MINUTES = 45


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user("users", "accounts", form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/get-collections")
async def collection_names(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    active_user = await get_current_active_user(user)
    return active_user.db_access


@app.post("/get-cities")
async def city_names(db: str, collection: str, token: str = Depends(oauth2_scheme)):
    return await authorize(token, db, collection, get_cities, get_client(db, collection))


@app.post("/new-city-info")
async def new_city_info(db: str, city: str, info: List[str] = Body(...), token: str = Depends(oauth2_scheme)):
    return await authorize(token, db, "city_info", new_city_data, get_client(db, "city_info"), city, info[0])


@app.post("/get-cities-info")
async def get_cities_info(db: str, city: str = None, skip: int = 0, token: str = Depends(oauth2_scheme)):
    return await authorize(token, db, "city_info", get_city_data, get_client(db, "city_info"), city, skip)


@app.post("/new-contact")
async def new_contact(db: str, collection: str, contact: ContactModel, token: str = Depends(oauth2_scheme)):
    return await authorize(token, db, collection, create_new_contact, get_client(db, collection), contact)


@app.put("/update-contact")
async def put_contact(
    db: str, collection: str, _id: str, contact: UpdateContactModel, token: str = Depends(oauth2_scheme)
        ):
    return await authorize(token, db, collection, update_contact, get_client(db, collection), _id, contact)


@app.post("/get-contact-by-id")
async def get_contact_by_id(
    db: str, collection: str, _id: str, token: str = Depends(oauth2_scheme)
    ):
    return await authorize(token, db, collection, read_contact_by_id, get_client(db, collection), _id)


@app.post("/get-contact-by-attr")
async def get_contact_by_attr(
    db: str, collection: str, filters: Dict = Body(..., example={"name": "test", "age": 35}), exact: bool = True,
    skip: int = 0, token: str = Depends(oauth2_scheme)
        ):
    """`filters` should be a dictionary of key-value pairs of attributes and attribute value"""
    if not exact:
        return await authorize(token, db, collection, read_contact_by_attr_contains, get_client(db, collection), filters, skip=skip)
    return await authorize(token, db, collection, read_contact_by_attr, get_client(db, collection), filters, skip=skip)


@app.delete("/delete-contact")
async def delete_contact_by_id(db: str, collection: str, _id: str, token: str = Depends(oauth2_scheme)):
    return await authorize(token, db, collection, delete_contact, get_client(db, collection), _id)


@app.post("/send-csv")
async def send_contacts_csv(
    db: str, collection: str, filters: Dict = Body(..., example={"name": "test"}), exact: bool = True,
    token: str = Depends(oauth2_scheme)
        ):
    email = await get_user_email(get_client(*USER_COLLECTION), token)
    if email:
        if not exact:
            return await csv_authorize(token, db, collection, read_contact_by_attr_contains, filters, email)
        return await csv_authorize(token, db, collection, read_contact_by_attr, filters, email)
    return {"success": "no email provided"}
