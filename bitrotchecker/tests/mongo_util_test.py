from unittest.mock import Mock

import mongomock

from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.logger_util import LoggerUtil
from bitrotchecker.src.mongo_util import MongoUtil


class TestMongoUtil:
    @staticmethod
    def _print(message: str):
        print(f"LOGGER: {message}")

    def test_encrypt_string(self):
        database = mongomock.MongoClient().db
        mongo_util = MongoUtil(database=database)

        logger: LoggerUtil = Mock()
        logger.write = Mock()
        logger.write.side_effect = self._print

        assert mongo_util.files_collection.count_documents({}) == 0

        file_record = FileRecord("file_path", 12345.6, 1000, 99999999)
        passed, message = mongo_util.process_file_record("root", file_record, logger)
        print(message)
        assert passed is True
        assert mongo_util.files_collection.count_documents({}) == 1

        # The existing record should be checked and pass
        passed, message = mongo_util.process_file_record("root", file_record, logger)
        print(message)
        assert passed is True
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the size of the file should lead to a failure
        file_record_different_size = FileRecord(
            file_record.file_path, file_record.modified_time, 2000, file_record.checksum
        )
        passed, message = mongo_util.process_file_record("root", file_record_different_size, logger)
        print(message)
        assert passed is False
        assert "size" in message
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the CRC of the file should lead to a failure
        file_record_different_size = FileRecord(
            file_record.file_path, file_record.modified_time, file_record.size, 22222222
        )
        passed, message = mongo_util.process_file_record("root", file_record_different_size, logger)
        print(message)
        assert passed is False
        assert "CRC" in message
        assert mongo_util.files_collection.count_documents({}) == 1

        # A new file path should mean a new record in the database
        new_file_record = FileRecord("myFile", file_record.modified_time, 999, 11111111)
        passed, message = mongo_util.process_file_record("root", new_file_record, logger)
        print(message)
        assert passed is True
        assert mongo_util.files_collection.count_documents({}) == 2

        # A new modified time should mean a new record in the database
        new_file_record = FileRecord(file_record.file_path, file_record.modified_time + 999999, 999, 11111111)
        passed, message = mongo_util.process_file_record("root", new_file_record, logger)
        print(message)
        assert passed is True
        assert mongo_util.files_collection.count_documents({}) == 3
