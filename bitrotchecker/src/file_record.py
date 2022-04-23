import hashlib
from datetime import datetime, timezone
from typing import Dict, Any

from bitrotchecker.src.constants import FILE_ID_KEY, SIZE_KEY, CHECKSUM_KEY, MODIFIED_TIME_KEY, LAST_ACCESSED_KEY


class FileRecord:
    def __init__(self, file_path: str, modified_time: float, size: int, checksum: int):
        self.file_path = file_path
        self.modified_time = modified_time
        self.size = size
        self.checksum = checksum

        self.file_id = self._calculate_file_id(self.file_path)

    @staticmethod
    def _calculate_file_id(file_path: str):
        hasher = hashlib.sha256()
        hasher.update(file_path.encode())
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
        return (
            f"{self.file_id} - {self.file_path} -"
            f" Modified '{datetime.fromtimestamp(self.modified_time, tz=timezone.utc)}' -"
            f" CRC {self.checksum} - {self.size} bytes"
        )
