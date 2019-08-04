from db.base import convert_ids
from bson.objectid import ObjectId

import re

from models import ContactModel, UpdateContactModel

from typing import List, Dict
from pymongo.collection import Collection


def create_new_contact(client: Collection, contact: ContactModel) -> bool:
    """This function supports create operations for contacts.

    Use the `get_client` function from this module to receive a `Collection`
    object for use as 'client'.
    'contact' must be a pydantic `ContactModel`, as defined in models.
    Returns `True` upon success, `False` upon failure."""
    contact_dict = contact.dict(skip_defaults=True)
    contact_dict = {k:v for k, v in contact_dict.items() if v}
    result = client.insert_one(contact_dict)
    if result.acknowledged:
        return {"success": True}
    return {"success": False}


def read_contact_by_id(client: Collection, _id: str):
    return convert_ids([client.find_one({"_id": ObjectId(_id)})])


def read_contact_by_attr(client: Collection, filters: Dict, cursor: bool = False, skip: int = 0) -> List[Dict]:
    """This function returns a list of all contact documents exactly matching
    the search filters.

    Use the `get_client` function from this module to receive a `Collection`
    object for use as `client`."""
    if cursor and filters is not None:
        return client.find(filters, {"_id": 0})
    elif cursor and filters is None:
        return client.find({}, {"_id": 0})
    elif filters is not None:
        return convert_ids([doc for doc in client.find(filters).skip(skip).limit(10)])
    return convert_ids([doc for doc in client.find().skip(skip).limit(10)])


def read_contact_by_attr_contains(client: Collection, filters: Dict, cursor: bool = False, skip: int = 0) -> List[Dict]:
    """This function returns a list of all contact documents fuzzily matching
    the search filters.

    Use the `get_client` function from this module to receive a `Collection`
    object for use as `client`."""
    search_dict = {}
    for k, v in filters.items():
        search_dict[k] = {"$regex": re.compile(f".*{v}.*", re.IGNORECASE)}
    if cursor:
        return client.find(search_dict, {"_id": 0})
    return convert_ids([doc for doc in client.find(search_dict).skip(skip).limit(10)])


def update_contact(client: Collection, _id: str, contact: UpdateContactModel) -> bool:
    """This function modifies previous contact information. To be used upon
    discovery of inaccurate data.
    
    Use the `get_client` function from this module to receive a `Collection`
    object for use as `client`.
    
    Returns `True` upon success, `False` upon failure."""
    contact_dict = contact.dict(skip_defaults=True)
    rm = {k:v for k, v in contact_dict.items() if not v}
    result = client.update_one({"_id": ObjectId(_id)}, {"$set": contact_dict})
    client.update_one({"_id": ObjectId(_id)}, {"$unset": rm})
    if result.acknowledged:
        return {"success": True}
    return {"success": False}


def add_further_note_to_contact(client: Collection, _id: str, note: str) -> bool:
    """This function appends further (and distinct) notes to the 'notes'
    array in a contact document.
    
    Use the `get_client` function from this module to receive a `Collection`
    object for use as `client`.
    
    Returns `True` upon success, `False` upon failure."""
    result = client.update_one({"_id", ObjectId(_id)}, {"$push": {"notes": note}})
    if result.acknowledged:
        return {"success": True}
    return {"success": False}


def delete_contact(client: Collection, _id: str) -> bool:
    """This function deletes a contact document.

    Use the `get_client` function from this module to receive a `Collection`
    object for use as `client`.

    Returns `True` upon success, `False` upon failure."""
    result = client.delete_one({"_id": ObjectId(_id)})
    if result.acknowledged:
        return {"success": True}
    return {"success": False}
