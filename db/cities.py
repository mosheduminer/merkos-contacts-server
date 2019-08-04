from db.base import convert_ids
from datetime import datetime

from pymongo.collection import Collection


def get_cities(client: Collection):
    return sorted(client.distinct("city"))


def new_city_data(client: Collection, city: str, info: str):
    result = client.update_one({"city": city}, {"$set": {datetime.utcnow().isoformat()[:-7]: info}}, upsert=True)
    if result.acknowledged:
        return {"success": True}
    return {"success": False}


def get_city_data(client: Collection, city: str = None, skip: int = 0):
    if city:
        return convert_ids([client.find_one({"city": city})])
    return convert_ids([doc for doc in client.find({}).skip(skip).limit(10)])
