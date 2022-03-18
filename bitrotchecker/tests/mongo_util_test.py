import mongomock

from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.mongo_util import MongoUtil


class TestMongoUtil:
    def test_encrypt_string(self):
        database = mongomock.MongoClient().db
        mongo_util = MongoUtil(database=database)

        assert mongo_util.files_collection.count_documents({}) == 0

        file_record = FileRecord("file_path", 1000, 99999999)
        passed, message = mongo_util.process_file_record("root", file_record)
        print(message)
        assert passed is True
        assert mongo_util.files_collection.count_documents({}) == 1

        # The existing record should be checked and pass
        passed, message = mongo_util.process_file_record("root", file_record)
        print(message)
        assert passed is True
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the size of the file should lead to a failure
        file_record_different_size = FileRecord(file_record.file_path, 2000, file_record.checksum)
        passed, message = mongo_util.process_file_record("root", file_record_different_size)
        print(message)
        assert passed is False
        assert "size" in message
        assert mongo_util.files_collection.count_documents({}) == 1

        # Changing the CRC of the file should lead to a failure
        file_record_different_size = FileRecord(file_record.file_path, file_record.size, 22222222)
        passed, message = mongo_util.process_file_record("root", file_record_different_size)
        print(message)
        assert passed is False
        assert "CRC" in message
        assert mongo_util.files_collection.count_documents({}) == 1

        # A new file path should mean a new record in the database
        new_file_record = FileRecord("myFile", 999, 11111111)
        passed, message = mongo_util.process_file_record("root", new_file_record)
        print(message)
        assert passed is True
        assert mongo_util.files_collection.count_documents({}) == 2
