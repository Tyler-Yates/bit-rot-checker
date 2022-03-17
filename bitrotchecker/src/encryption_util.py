import base64
import os.path
from typing import Dict

import tink
from tink import cleartext_keyset_handle, daead, tink_config

from bitrotchecker.src.constants import FILE_PATH_KEY, SIZE_KEY, CRC_KEY
from bitrotchecker.src.file_record import FileRecord

DEFAULT_KEYSET_PATH = "keyset.json"

ENCRYPTION_TIME = 1000


class EncryptionUtil:
    def __init__(self, keyset_path: str = None, create_keyset_if_missing: bool = False):
        tink_config.register()

        if keyset_path:
            self.keyset_path = keyset_path
        else:
            self.keyset_path = DEFAULT_KEYSET_PATH

        if create_keyset_if_missing:
            self.generate_keyset_if_missing()

        keyset_handle = self.read_keyset()

        self.cipher = keyset_handle.primitive(daead.DeterministicAead)
        self.associated_data = b""

    def generate_keyset_if_missing(self):
        if os.path.exists(self.keyset_path):
            return

        tink_config.register()
        key_template = daead.deterministic_aead_key_templates.AES256_SIV
        keyset_handle = tink.KeysetHandle.generate_new(key_template)
        with open(self.keyset_path, "wt") as keyset_file:
            cleartext_keyset_handle.write(tink.JsonKeysetWriter(keyset_file), keyset_handle)

    def read_keyset(self):
        with open(self.keyset_path, "rt") as keyset_file:
            text = keyset_file.read()
            keyset_handle = cleartext_keyset_handle.read(tink.JsonKeysetReader(text))
            return keyset_handle

    def encrypt_string(self, input_string: str) -> str:
        encoded_data = self.cipher.encrypt_deterministically(input_string.encode(), self.associated_data)
        return base64.b64encode(encoded_data).decode()

    def decrypt_string(self, encrypted_string: str) -> str:
        decrypted_data = self.cipher.decrypt_deterministically(base64.b64decode(encrypted_string), self.associated_data)
        return decrypted_data.decode()

    def get_encrypted_file_record(self, file_record: FileRecord) -> Dict:
        return {
            FILE_PATH_KEY: self.encrypt_string(file_record.file_path),
            SIZE_KEY: self.encrypt_string(str(file_record.size)),
            CRC_KEY: self.encrypt_string(file_record.crc),
        }
