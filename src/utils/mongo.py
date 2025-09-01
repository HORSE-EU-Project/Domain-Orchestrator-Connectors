import logging
import os

from pymongo import MongoClient

logger = logging.getLogger("uvicorn.error")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("MONGO_DB", "doc_database")
MONGO_COLL = os.environ.get("MONGO_COLL", "mitigation_actions")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB]
_col = _db[MONGO_COLL]

_col.create_index("intent_id", unique=True)

def ping() -> bool:
    try:
        _client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(e)
        return False

def insert_raw(doc: dict) -> str:
    result = _col.insert_one(doc)
    return str(result.inserted_id)
