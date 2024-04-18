import os
from typing import Optional

from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_result_enum import FileResultValue
from bitrotchecker.src.file_util import should_skip_file, get_checksum_of_file
from bitrotchecker.src.logger_util import LoggerUtil
from bitrotchecker.src.mongo_util import MongoUtil
from bitrotchecker.src.recency_util import RecencyUtil


class FileProcessor:
    def __init__(self, recency_util: RecencyUtil, mongo_util: MongoUtil, logger: LoggerUtil):
        self.recency_util = recency_util
        self.mongo_util = mongo_util
        self.logger = logger

        self.total_skips = 0
        self.num_success = 0
        self.num_failures = 0
        self.failed_files = []

    def _process_file(self, root: str, path: str, true_file_path: str, file_is_immutable: bool) -> Optional[bool]:
        if should_skip_file(true_file_path):
            self.total_skips += 1
            print(f"Skipping {true_file_path} as ignored")
            return None

        file_modified_time = os.path.getmtime(true_file_path)

        if self.recency_util.file_processed_recently(true_file_path, file_modified_time):
            self.total_skips += 1
            print(f"Skipping {true_file_path} as processed recently")
            return None

        saved_file_path = true_file_path.replace(path, "")
        file_size = os.path.getsize(true_file_path)
        file_crc = get_checksum_of_file(true_file_path)

        file_record = FileRecord(saved_file_path, file_modified_time, file_size, file_crc)
        file_result = self.mongo_util.process_file_record(true_file_path, file_record, self.logger, file_is_immutable)
        if file_result.value is FileResultValue.PASS:
            print(f"PASS: {file_result.message} - {file_record}")
            # We only want to log successful files as processed
            self.recency_util.record_file_processed(true_file_path, file_modified_time)
            # Return the success
            return True
        elif file_result.value is file_result.value.FAIL:
            self.logger.write(f"FAIL: {file_result.message} - {file_record}")
            self.failed_files.append(f"{true_file_path} - {file_result.message}")
            # Return the failures
            return False
        elif file_result.value is file_result.value.SKIP:
            print(f"SKIP: {file_result.message} - {file_record}")
            return None

    def process_file(self, root: str, path: str, true_file_path: str, file_is_immutable: bool) -> Optional[bool]:
        try:
            return self._process_file(root, path, true_file_path, file_is_immutable)
        except Exception as e:
            self.logger.write(f"EXCEPTION: {e}")
            return None
