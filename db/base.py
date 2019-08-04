from pymongo import MongoClient

from config import MONGO_URI

from pymongo.collection import Collection
from typing import List


# initialize connection to the mongo cluster
client = MongoClient(MONGO_URI, 27017, w=2)


def get_client(db: str, collection: str) -> Collection:
    """A helper function that takes the names of the intended
    database and collection and returns a Collection object
    for database operations."""
    return client[db][collection]


def convert_ids(docs: List) -> List:
    """A helper function that takes a list of mongo documents (which
    are python dictionaries) and converts every ObjectId to a str.
    
    Not to be used outside of this module"""
    try:
        for doc in docs:
            doc["_id"] = str(doc["_id"])
    except TypeError:
        pass
    return docs


def get_collections(db: str) -> List:
    return client[db].list_collection_names()
