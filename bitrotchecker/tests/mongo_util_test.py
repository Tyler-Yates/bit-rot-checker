import time
from unittest import mock
from unittest.mock import Mock

import mongomock

from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_result_enum import FileResultStatus
from bitrotchecker.src.logger_util import LoggerUtil
from bitrotchecker.src.mongo_util import MongoUtil


class TestMongoUtil:
    @staticmethod
    def _print(message: str):
        print(f"LOGGER: {message}")

    def test_mutable_file(self):
        database = mongomock.MongoClient().db
        mongo_util = MongoUtil(database=database)

        logger: LoggerUtil = Mock()
        logger.write = Mock()
        logger.write.side_effect = self._print

        immutability_bool = False

        assert mongo_util.files_collection.count_documents({}) == 0

        # Create the first record which should pass
        file_record = FileRecord("file_path", 12345.6, 1000, 99999999)
        result = mongo_util.process_file_record("root", file_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.PASS
        assert mongo_util.files_collection.count_documents({}) == 1

        # The existing record should be checked and pass
        result = mongo_util.process_file_record("root", file_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.PASS
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the size of the file should lead to a failure
        file_record_different_size = FileRecord(
            file_record.file_path, file_record.modified_time, 2000, file_record.checksum
        )
        result = mongo_util.process_file_record("root", file_record_different_size, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.FAIL
        assert "size" in result.message
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the CRC of the file should lead to a failure
        file_record_different_size = FileRecord(
            file_record.file_path, file_record.modified_time, file_record.size, 22222222
        )
        result = mongo_util.process_file_record("root", file_record_different_size, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.FAIL
        assert "CRC" in result.message
        assert mongo_util.files_collection.count_documents({}) == 1

        # A new file path should mean a new record in the database
        new_file_record = FileRecord("myFile", file_record.modified_time, 999, 11111111)
        result = mongo_util.process_file_record("root", new_file_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.PASS
        assert mongo_util.files_collection.count_documents({}) == 2

        # A new modified time should mean a new record in the database since the file is mutable
        new_file_record = FileRecord(file_record.file_path, file_record.modified_time + 999999, 999, 11111111)
        result = mongo_util.process_file_record("root", new_file_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.PASS
        assert mongo_util.files_collection.count_documents({}) == 3

    def test_immutable_file(self):
        database = mongomock.MongoClient().db
        mongo_util = MongoUtil(database=database)

        logger: LoggerUtil = Mock()
        logger.write = Mock()
        logger.write.side_effect = self._print

        assert mongo_util.files_collection.count_documents({}) == 0

        with mock.patch("os.path.getctime") as mock_getctime:
            self._test_immutable_file(mongo_util, logger, mock_getctime)

    @staticmethod
    def _test_immutable_file(mongo_util: MongoUtil, logger: LoggerUtil, mock_getctime):
        immutability_bool = True

        # Mock to say that every file was created a long time ago to bypass the recency check
        mock_getctime.return_value = 1

        # Create the first file record
        file_record = FileRecord("file_path", 12345.6, 1000, 99999999)
        result = mongo_util.process_file_record("root", file_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.PASS
        assert mongo_util.files_collection.count_documents({}) == 1

        # The existing record should be checked and pass
        result = mongo_util.process_file_record("root", file_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.PASS
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the size of the file should lead to a failure
        file_record_different_size = FileRecord(
            file_record.file_path, file_record.modified_time, 2000, file_record.checksum
        )
        result = mongo_util.process_file_record("root", file_record_different_size, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.FAIL
        assert "size" in result.message
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the CRC of the file should lead to a failure
        file_record_different_size = FileRecord(
            file_record.file_path, file_record.modified_time, file_record.size, 22222222
        )
        result = mongo_util.process_file_record("root", file_record_different_size, logger, False)
        print(result.message)
        assert result.value is FileResultStatus.FAIL
        assert "CRC" in result.message
        assert mongo_util.files_collection.count_documents({}) == 1

        # A new modified time should lead to a failure since the file is immutable
        modified_time_record = FileRecord(
            file_record.file_path, file_record.modified_time + 999999, file_record.size, file_record.checksum
        )
        result = mongo_util.process_file_record("root", modified_time_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.FAIL
        assert mongo_util.files_collection.count_documents({}) == 1

        # A new file path should mean a new record in the database
        new_file_record = FileRecord("myFile", file_record.modified_time, 999, 11111111)
        result = mongo_util.process_file_record("root", new_file_record, logger, immutability_bool)
        print(result.message)
        assert result.value is FileResultStatus.PASS
        assert mongo_util.files_collection.count_documents({}) == 2

        # Now change the mock to say that the file was created right now
        mock_getctime.return_value = time.time()
        new_file_record = FileRecord("newImmutableFile", file_record.modified_time, 999, 11111111)
        result = mongo_util.process_file_record("root", new_file_record, logger, immutability_bool)
        print(result.message)
        # The file should still "pass" verification but no new file record should be added to the database
        # because it should be skipped for being too recently created.
        assert result.value is FileResultStatus.SKIP
        assert mongo_util.files_collection.count_documents({}) == 2
