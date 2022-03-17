import hashlib


class FileRecord:
    def __init__(self, file_path: str, size: int, crc: str):
        self.file_path = file_path
        hasher = hashlib.sha256()
        hasher.update(self.file_path.encode())
        self.file_id = hasher.hexdigest().lower()
        self.size = size
        self.crc = crc

    def __str__(self):
        return f"{self.file_id} - {self.file_path} - {self.crc} - {self.size} bytes"
