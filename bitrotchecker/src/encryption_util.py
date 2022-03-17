import os.path
from typing import Dict

from cryptography.fernet import Fernet

from bitrotchecker.src.constants import FILE_PATH_KEY, SIZE_KEY, CRC_KEY, FILE_ID_KEY
from bitrotchecker.src.file_record import FileRecord

DEFAULT_KEYSET_PATH = "key.txt"

ENCRYPTION_TIME = 1000


class EncryptionUtil:
    def __init__(self, keyset_path: str = None, create_keyset_if_missing: bool = False):
        if keyset_path:
            self.keyset_path = keyset_path
        else:
            self.keyset_path = DEFAULT_KEYSET_PATH

        if create_keyset_if_missing:
            self.generate_key_if_missing()

        self.cipher = Fernet(self.read_key())

    def generate_key_if_missing(self):
        if os.path.exists(self.keyset_path):
            return

        print("Creating new key...")
        key = Fernet.generate_key()
        with open(self.keyset_path, "wt") as keyset_file:
            keyset_file.write(key.decode())

    def read_key(self) -> str:
        print("Reading key...")
        with open(self.keyset_path, "rt") as keyset_file:
            return keyset_file.read()

    def encrypt_string(self, input_string: str) -> str:
        return self.cipher.encrypt(input_string.encode()).decode()

    def decrypt_string(self, encrypted_string: str) -> str:
        return self.cipher.decrypt(encrypted_string.encode()).decode()

    def get_encrypted_file_record(self, file_record: FileRecord) -> Dict:
        return {
            FILE_ID_KEY: file_record.file_id,
            FILE_PATH_KEY: self.encrypt_string(file_record.file_path),
            SIZE_KEY: file_record.size,
            CRC_KEY: self.encrypt_string(file_record.crc),
        }
