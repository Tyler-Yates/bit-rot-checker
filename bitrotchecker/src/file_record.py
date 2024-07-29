import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, Any

from bitrotchecker.src.constants import FILE_ID_KEY, SIZE_KEY, CHECKSUM_KEY, MODIFIED_TIME_KEY, LAST_ACCESSED_KEY
from bitrotchecker.src.file_util import get_checksum_of_file


class FileRecord:
    def __init__(self, file_path: str, full_file_path: str):
        self.file_path = file_path
        self.full_file_path = full_file_path

    @property
    def size(self) -> float:
        return os.path.getsize(self.full_file_path)

    @property
    def modified_time(self) -> float:
        return os.path.getmtime(self.full_file_path)

    @property
    def checksum(self) -> int:
        return get_checksum_of_file(self.full_file_path)

    @property
    def file_id(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(self.full_file_path.encode())
        return hasher.hexdigest().lower()

    def get_mongo_document(self) -> Dict[str, Any]:
        return {
            FILE_ID_KEY: self.file_id,
            # We do not save the file_path for privacy reasons
            MODIFIED_TIME_KEY: self.modified_time,
            SIZE_KEY: self.size,
            CHECKSUM_KEY: self.checksum,
            # Set the last accessed time to now since we are likely accessing the document
            LAST_ACCESSED_KEY: datetime.now(),
        }

    def __str__(self):
        # Don't include CRC as that can be very expensive to calculate
        return (
            f"id={self.file_id} - {self.file_path} -"
            f" Modified '{datetime.fromtimestamp(self.modified_time, tz=timezone.utc)}' -"
            f" {self.size} bytes"
        )
