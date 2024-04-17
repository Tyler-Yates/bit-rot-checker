import os.path
from datetime import datetime, timezone
from typing import Tuple, Dict, Optional

import bson
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from bitrotchecker.src.configuration_util import get_mongo_connection_string
from bitrotchecker.src.constants import (
    SIZE_KEY,
    CHECKSUM_KEY,
    FILE_ID_KEY,
    LAST_ACCESSED_KEY,
    MODIFIED_TIME_KEY,
    MONGO_ID_KEY,
    SECONDS_IN_A_YEAR,
)
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.logger_util import LoggerUtil


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
        self.files_collection.create_index(
            [(FILE_ID_KEY, pymongo.ASCENDING), (MODIFIED_TIME_KEY, pymongo.ASCENDING)], unique=True
        )
        self.files_collection.create_index(LAST_ACCESSED_KEY, expireAfterSeconds=SECONDS_IN_A_YEAR)
        print("Successfully connected with Mongo")

    def _find_document(self, file_record: FileRecord, logger: LoggerUtil, file_is_immutable: bool) -> Optional[Dict]:
        database_document = self.files_collection.find_one(
            {FILE_ID_KEY: file_record.file_id, MODIFIED_TIME_KEY: file_record.modified_time}
        )

        if database_document:
            # If the document exists, update its last accessed time so that it is not cleaned up
            current_datetime = datetime.now()
            update_result = self.files_collection.update_one(
                filter={MONGO_ID_KEY: database_document[MONGO_ID_KEY]},
                update={"$set": {LAST_ACCESSED_KEY: current_datetime}},
                upsert=False,
            )

            # Don't look at modified_count as MongoDB may choose to not update the document
            # if the timestamps are too close together.
            if update_result.matched_count != 1:
                raise ValueError(f"Could not update last accessed time for {file_record.file_id}")

            # We want to return the updated document, not the stale one we got earlier
            return self.files_collection.find_one({MONGO_ID_KEY: database_document[MONGO_ID_KEY]})
        else:
            file_record_with_different_mtime = self.files_collection.find_one({FILE_ID_KEY: file_record.file_id})
            if file_record_with_different_mtime is None:
                # We have never seen this file before.
                return None
            else:
                # We have seen this file before, but the modified timestamp is different.
                if file_is_immutable:
                    # The file is immutable so we should fail the comparison
                    logger.write(
                        f"Immutable file has been modified: "
                        f"{file_record.file_path} - "
                        f"{datetime.fromtimestamp(file_record.modified_time, tz=timezone.utc)}"
                    )
                    return file_record_with_different_mtime
                else:
                    # The file is mutable, so we should just create a new record.
                    print(
                        f"File has been seen before but has been modified: "
                        f"{file_record.file_path} - "
                        f"{datetime.fromtimestamp(file_record.modified_time, tz=timezone.utc)}"
                    )
                    return None

    def process_file_record(
        self, root_path: str, file_record: FileRecord, logger: LoggerUtil, file_is_immutable: bool
    ) -> Tuple[bool, str]:
        full_path = os.path.join(root_path, file_record.file_path)

        database_document = self._find_document(file_record, logger, file_is_immutable)
        if database_document:
            # We have already seen this file before so check to see if there is bit rot
            database_file_id = database_document[FILE_ID_KEY]
            database_file_mtime = database_document[MODIFIED_TIME_KEY]
            database_file_size = database_document[SIZE_KEY]
            database_file_crc = database_document[CHECKSUM_KEY]

            if file_record.file_id != database_file_id:
                raise ValueError(
                    f"Fatal error! File ID mismatch: Local File={file_record.file_id!r}"
                    f" but Database={database_file_id!r}."
                )

            if file_record.modified_time != database_file_mtime:
                return (
                    False,
                    f"File mtime mismatch: Local File={file_record.modified_time!r}"
                    f" but Database={database_file_mtime!r}.",
                )

            if file_record.size != database_file_size:
                return (
                    False,
                    f"File {full_path} has a different size than expected. "
                    f"Database={database_file_size!r} but Local File={file_record.size!r}",
                )

            if file_record.checksum != database_file_crc:
                return (
                    False,
                    f"File {full_path} has a different CRC than expected. "
                    f"Database={database_file_crc!r} but Local File={file_record.checksum!r}",
                )
        else:
            # This file record is not in the database. Time to create a new document.
            print(
                f"Creating new file record: {file_record.file_path} - "
                f"{datetime.fromtimestamp(file_record.modified_time, tz=timezone.utc)} - "
                f"{file_record.file_id}"
            )
            self.files_collection.update_one(
                filter={FILE_ID_KEY: file_record.file_id, MODIFIED_TIME_KEY: file_record.modified_time},
                update={"$set": (file_record.get_mongo_document())},
                upsert=True,
            )
            return True, f"File {full_path} record created: {file_record}"

        return True, f"File {full_path} passed verification"

    def get_size_of_documents(self):
        documents = self.files_collection.find()

        smallest_size_bytes = 999999999999999999999999
        largest_size_bytes = -1
        total_size_bytes = 0
        total_documents = 0
        for document in documents:
            size_bytes = len(bson.BSON.encode(document))

            smallest_size_bytes = min(smallest_size_bytes, size_bytes)
            largest_size_bytes = max(largest_size_bytes, size_bytes)
            total_size_bytes += size_bytes
            total_documents += 1

        if total_documents == 0:
            return

        average_document_size_bytes = round(total_size_bytes / total_documents, 1)
        print(f"Smallest document size: {smallest_size_bytes} bytes")
        print(f"Largest document size: {largest_size_bytes} bytes")
        print(f"Average document size: {average_document_size_bytes} bytes")

    def get_all_records_for_file_id(self, file_id: str):
        return self.files_collection.find({FILE_ID_KEY: file_id})
