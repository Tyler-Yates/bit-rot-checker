import os

from bitrotchecker.src.configuration_util import get_paths
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_util import get_checksum, should_skip_file
from bitrotchecker.src.mongo_util import MongoUtil


def main():
    mongo_util = MongoUtil()

    # To get data on the current database, uncomment next line
    # mongo_util.get_size_of_documents()

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
                if should_skip_file(true_file_path):
                    print(f"Skipping {true_file_path}")
                    continue

                saved_file_path = true_file_path.replace(path, "")
                file_size = os.path.getsize(true_file_path)
                file_crc = get_checksum(true_file_path)

                file_record = FileRecord(saved_file_path, file_size, file_crc)
                passed, message = mongo_util.process_file_record(root, file_record)
                if passed:
                    print(f"PASS: {message} - {file_record}")
                    num_success = num_success + 1
                else:
                    print(f"FAIL: {message} - {file_record}")
                    num_failures = num_failures + 1
                    failed_files.append(f"{true_file_path} - {message}")

        print(f"\nSuccesses in {path}: {num_success}")
        print(f"Failures in {path}:  {num_failures}")
        total_successes = total_successes + num_success

    print("\n===================================")
    print(f"Total successes: {total_successes}")
    print(f"Total failures:  {len(failed_files)}")
    if len(failed_files) > 0:
        print("\nFailed files:")
        for failed_file in failed_files:
            print(failed_file)


if __name__ == "__main__":
    main()
