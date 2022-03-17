class FileRecord:
    def __init__(self, file_path: str, size: int, crc: str):
        self.file_path = file_path
        self.size = size
        self.crc = crc

    def __str__(self):
        return f"{self.file_path} - {self.crc} - {self.size} bytes"
