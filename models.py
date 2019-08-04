from typing import Optional, List, Dict

from pydantic import BaseModel, EmailStr


class ContactModel(BaseModel):
    """This model contains all possible information for a merkos contact"""
    name: str
    age: Optional[int]
    jewish_knowledge: Optional[str]
    country: Optional[str]
    city: str
    street_address: str
    phone: Optional[List[int]]
    email: Optional[str]
    affiliation: Optional[str]
    children: Optional[str]
    marital_status: Optional[str]
    spouse: Optional[str]
    languages: Optional[str]
    notes: Optional[List[str]]


class UpdateContactModel(ContactModel):
    """Used for updating contacts"""
    name: Optional[str]
    city: Optional[str]
    street_address: Optional[str]


class User(BaseModel):
    username: str
    email: Optional[str]
    db_access: Optional[Dict]
    full_name: Optional[str]
    disabled: Optional[bool]


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
