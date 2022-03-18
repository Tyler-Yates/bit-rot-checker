import hashlib
from typing import Dict, Any

from bitrotchecker.src.constants import FILE_ID_KEY, SIZE_KEY, CHECKSUM_KEY


class FileRecord:
    def __init__(self, file_path: str, size: int, checksum: int):
        self.file_path = file_path
        hasher = hashlib.sha256()
        hasher.update(self.file_path.encode())
        self.file_id = hasher.hexdigest().lower()
        self.size = size
        self.checksum = checksum

    def get_mongo_document(self) -> Dict[str, Any]:
        return {
            FILE_ID_KEY: self.file_id,
            # We do not save the file_path
            SIZE_KEY: self.size,
            CHECKSUM_KEY: self.checksum,
        }

    def __str__(self):
        return f"{self.file_id} - {self.file_path} - {self.checksum} - {self.size} bytes"
