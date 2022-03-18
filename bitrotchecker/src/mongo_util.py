import os.path
from typing import Tuple

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from bitrotchecker.src.configuration_util import get_mongo_connection_string
from bitrotchecker.src.constants import SIZE_KEY, CHECKSUM_KEY, FILE_ID_KEY
from bitrotchecker.src.file_record import FileRecord


class MongoUtil:
    def __init__(self, database: Database = None):
        if database:
            print("Using provided database object")
            self.files_db: Database = database
        else:
            print("Connecting to Mongo database...")
            mongo_client = MongoClient(get_mongo_connection_string())
            self.files_db: Database = mongo_client.bitrot

        self.files_collection: Collection = self.files_db.files
        self.files_collection.create_index(FILE_ID_KEY, unique=True)
        print("Successfully connected with Mongo")

    def process_file_record(self, root_path: str, file_record: FileRecord) -> Tuple[bool, str]:
        full_path = os.path.join(root_path, file_record.file_path)

        database_document = self.files_collection.find_one({FILE_ID_KEY: file_record.file_id})
        if database_document:
            database_file_id = database_document[FILE_ID_KEY]
            database_file_size = database_document[SIZE_KEY]
            database_file_crc = database_document[CHECKSUM_KEY]

            if file_record.file_id != database_file_id:
                raise ValueError(
                    f"Fatal error! File ID mismatch: {file_record.file_id} expected but {database_file_id} found."
                )

            if file_record.size != database_file_size:
                return (
                    False,
                    f"File {full_path} has a different size than expected. "
                    f"Expected: {database_file_size}, Actual: {file_record.size}",
                )

            if file_record.checksum != database_file_crc:
                return (
                    False,
                    f"File {full_path} has a different CRC than expected. "
                    f"Expected: {database_file_crc}, Actual: {file_record.checksum}",
                )
        else:
            self.files_collection.update_one(
                filter={FILE_ID_KEY: file_record.file_id},
                update={"$set": (file_record.get_mongo_document())},
                upsert=True,
            )
            return True, f"File {full_path} record created: {file_record}"

        return True, f"File {full_path} passed verification"
