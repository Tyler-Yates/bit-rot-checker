import base64
from typing import Dict

import tink
from tink import aead, cleartext_keyset_handle, daead, tink_config

from bitrotchecker.constants import FILE_PATH_KEY, SIZE_KEY, CRC_KEY
from bitrotchecker.file_record import FileRecord

KEYSET_PATH = 'keyset.json'

ENCRYPTION_TIME = 1000


class EncryptionUtil:
    def __init__(self):
        tink_config.register()
        keyset_handle = self.read_keyset()

        self.cipher = keyset_handle.primitive(daead.DeterministicAead)
        self.associated_data = b''

    @staticmethod
    def generate_keyset():
        tink_config.register()
        key_template = daead.deterministic_aead_key_templates.AES256_SIV
        keyset_handle = tink.KeysetHandle.generate_new(key_template)
        with open(KEYSET_PATH, 'wt') as keyset_file:
            cleartext_keyset_handle.write(tink.JsonKeysetWriter(keyset_file), keyset_handle)

    @staticmethod
    def read_keyset():
        with open(KEYSET_PATH, 'rt') as keyset_file:
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
            CRC_KEY: self.encrypt_string(file_record.crc)
        }
