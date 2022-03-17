import os.path
from typing import Optional

from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from bitrotchecker.src.constants import FILE_PATH_KEY, SIZE_KEY, CRC_KEY
from bitrotchecker.src.encryption_util import EncryptionUtil
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.configuration_util import get_mongo_connection_string


class MongoUtil:
    def __init__(self):
        self.mongo_client = MongoClient(get_mongo_connection_string())
        self.files_db: Database = self.mongo_client.bitrot
        self.files_collection: Collection = self.files_db.files
        self.files_collection.create_index([(FILE_PATH_KEY, DESCENDING)], unique=True)

        self.encryption = EncryptionUtil()

    def process_file_record(self, root_path: str, file_record: FileRecord) -> Optional[str]:
        encrypted_file_path = self.encryption.encrypt_string(file_record.file_path)
        full_path = os.path.join(root_path, file_record.file_path)

        database_document = self.files_collection.find_one({FILE_PATH_KEY: encrypted_file_path})
        if database_document:
            database_file_path = self.encryption.decrypt_string(database_document[FILE_PATH_KEY])
            database_file_size = int(self.encryption.decrypt_string(database_document[SIZE_KEY]))
            database_file_crc = self.encryption.decrypt_string(database_document[CRC_KEY])

            if file_record.file_path != database_file_path:
                raise ValueError(
                    f"Fatal error! File path {file_record.file_path} does not match database file "
                    f"path {database_file_path}."
                )

            if file_record.size != database_file_size:
                return (
                    f"File {full_path} has a different size than expected. "
                    f"Expected: {database_file_size}, Actual: {file_record.size}"
                )

            if file_record.crc != database_file_crc:
                return (
                    f"File {full_path} has a different CRC than expected. "
                    f"Expected: {database_file_crc}, Actual: {file_record.crc}"
                )
        else:
            self.files_collection.update_one(
                filter={FILE_PATH_KEY: encrypted_file_path},
                update={"$set": (self.encryption.get_encrypted_file_record(file_record))},
                upsert=True,
            )
            print(f"File record created: {file_record}")

        return None
