from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from bitrotchecker.secret_util import get_mongo_connection_string

FILE_PATH_KEY = "file_path"
SIZE_KEY = "size"
CRC_KEY = "crc"


def _get_mongo_client() -> MongoClient:
    return MongoClient(get_mongo_connection_string())


def get_files_collection() -> Collection:
    mongo_client = _get_mongo_client()
    files_db: Database = mongo_client.bitrot
    files_collection: Collection = files_db.files
    files_collection.create_index([(FILE_PATH_KEY, DESCENDING)], unique=True)

    print(f"File records present: {files_collection.count_documents({})}")

    return files_collection
