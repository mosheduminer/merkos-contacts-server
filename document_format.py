import csv
from tempfile import mkdtemp
import os
import shutil

from models import ContactModel
from pymongo.cursor import Cursor

from email_script import email_csv

from typing import List, Dict


async def send_csv(cursor: Cursor, email_address: str, collection: str, search_terms: Dict):
    temp_dir = mkdtemp()
    temp_file = os.path.join(temp_dir, "temp_csv")
    csv_file = open(temp_file, "w", newline="")
    writer = csv.writer(csv_file)
    writer.writerow(list(ContactModel.schema()["properties"].keys()))
    for doc in cursor:
        model_dict = ContactModel.parse_obj(doc).dict()
        values = list(model_dict.values())
        # this if clause extracts the items of sublist `notes` to main list level
        if model_dict["notes"]:
            notes = values.pop()
            for note in notes:
                values.append(note)
        writer.writerow(values)
    csv_file.close()
    await email_csv(temp_file, email_address, collection, search_terms)
    shutil.rmtree(temp_dir)
    return {"success": True}
