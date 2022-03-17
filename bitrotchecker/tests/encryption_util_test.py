import os.path
import tempfile

from bitrotchecker.src.encryption_util import EncryptionUtil


class TestEncryptionUtil:
    def test_encrypt_string(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            encryption_util = EncryptionUtil(
                keyset_path=os.path.join(temp_dir_path, "key.txt"), create_keyset_if_missing=True
            )
            input_data = "test"
            encrypted_data = encryption_util.encrypt_string(input_data)

            assert encrypted_data != input_data

    def test_decrypt_string(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            encryption_util = EncryptionUtil(
                keyset_path=os.path.join(temp_dir_path, "key.txt"), create_keyset_if_missing=True
            )
            input_data = "test"
            encrypted_data = encryption_util.encrypt_string(input_data)

            decrypted1 = encryption_util.decrypt_string(encrypted_data)
            decrypted2 = encryption_util.decrypt_string(encrypted_data)

            assert encrypted_data != input_data
            assert input_data == decrypted1
            assert decrypted1 == decrypted2

    def test_multiple_encryptions(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            encryption_util = EncryptionUtil(
                keyset_path=os.path.join(temp_dir_path, "key.txt"), create_keyset_if_missing=True
            )
            input_data = "test"
            encrypted_data_1 = encryption_util.encrypt_string(input_data)
            encrypted_data_2 = encryption_util.encrypt_string(input_data)

            assert encrypted_data_1 != input_data
            assert encrypted_data_2 != input_data

            # We expect them to be different
            assert encrypted_data_1 != encrypted_data_2

            # Decrypting should result in the same data however
            assert encryption_util.decrypt_string(encrypted_data_1) == input_data
            assert encryption_util.decrypt_string(encrypted_data_2) == input_data
