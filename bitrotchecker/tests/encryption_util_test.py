import os.path
import tempfile

from bitrotchecker.src.encryption_util import EncryptionUtil


class TestEncryptionUtil:
    def test_encrypt_string(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            encryption_util = EncryptionUtil(
                keyset_path=os.path.join(temp_dir_path, "keyset.json"), create_keyset_if_missing=True
            )
            input_data = "test"
            encryption1 = encryption_util.encrypt_string(input_data)
            encryption2 = encryption_util.encrypt_string(input_data)

            assert encryption1 != input_data
            assert encryption1 == encryption2

    def test_decrypt_string(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            encryption_util = EncryptionUtil(
                keyset_path=os.path.join(temp_dir_path, "keyset.json"), create_keyset_if_missing=True
            )
            input_data = "test"
            encrypted_data = encryption_util.encrypt_string(input_data)

            decrypted1 = encryption_util.decrypt_string(encrypted_data)
            decrypted2 = encryption_util.decrypt_string(encrypted_data)

            assert encrypted_data != input_data
            assert input_data == decrypted1
            assert decrypted1 == decrypted2
