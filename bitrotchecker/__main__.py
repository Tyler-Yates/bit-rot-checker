import os
from typing import List

from bitrotchecker.src.encryption_util import EncryptionUtil
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_util import get_crc32
from bitrotchecker.src.mongo_util import MongoUtil


def main():
    mongo_util = MongoUtil()

    paths = _get_paths()
    failed_files = []
    for path in paths:
        num_failures = 0
        print("\n==========================================")
        print(f"Processing files in {path}...\n")
        for root, dirs, files in os.walk(path):
            for file in files:
                true_file_path = os.path.join(root, file)
                saved_file_path = true_file_path.replace(path, "")
                file_size = os.path.getsize(true_file_path)
                file_crc = get_crc32(true_file_path)

                file_record = FileRecord(saved_file_path, file_size, file_crc)
                result = mongo_util.process_file_record(root, file_record)
                if result:
                    print(f"FAIL: {result} - {file_record}")
                    num_failures = num_failures + 1
                    failed_files.append(f"{true_file_path} - {result}")
                else:
                    print(f"PASS: {file_record}")

        print(f"\nFailures in {path}: {num_failures}")

    print("\n===================================")
    print(f"Total failures: {len(failed_files)}")
    for failed_file in failed_files:
        print(failed_file)


def _get_paths() -> List[str]:
    paths = []

    with open("paths.txt", mode="r") as paths_files:
        for line in paths_files.readlines():
            if line.startswith("#") or (not line):
                continue

            paths.append(line.strip())

    return paths


def _test_encrypt(encryption_util: EncryptionUtil, input_data: str):
    encrypted_data = encryption_util.encrypt_string("Test")
    decrypted_data = encryption_util.decrypt_string(encrypted_data)
    print(f"{input_data} - {encrypted_data} - {decrypted_data}")


if __name__ == "__main__":
    # encryption = EncryptionUtil()
    # _test_encrypt(encryption, "Test")
    # _test_encrypt(encryption, "Test")
    # _test_encrypt(encryption, "Test")

    main()
