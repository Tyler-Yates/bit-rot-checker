import os

from bitrotchecker.src.configuration_util import get_paths
from bitrotchecker.src.encryption_util import EncryptionUtil
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_util import get_crc32
from bitrotchecker.src.mongo_util import MongoUtil


def main():
    encryption = EncryptionUtil(create_keyset_if_missing=True)
    mongo_util = MongoUtil(encryption)

    paths = get_paths()
    failed_files = []
    total_successes = 0
    for path in paths:
        num_success = 0
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
                    num_success = num_success + 1

        print(f"\nSuccesses in {path}: {num_success}")
        print(f"Failures in {path}:  {num_failures}")
        total_successes = total_successes + num_success

    print("\n===================================")
    print(f"Total successes: {total_successes}")
    print(f"Total failures:  {len(failed_files)}")
    for failed_file in failed_files:
        print(failed_file)


if __name__ == "__main__":
    main()
