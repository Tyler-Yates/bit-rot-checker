import os
from datetime import datetime
from typing import IO

from bitrotchecker.src.configuration_util import get_paths
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_util import get_checksum, should_skip_file
from bitrotchecker.src.mongo_util import MongoUtil
from bitrotchecker.src.recency_util import RecencyUtil


def main():
    mongo_util = MongoUtil()
    recency_util = RecencyUtil()

    # To get data on the current database, uncomment next line
    # mongo_util.get_size_of_documents()

    paths = get_paths()
    failed_files = []
    total_successes = 0
    total_skips = 0
    with open(os.path.join("logs", "latest.txt"), mode="w") as latest_log_file:
        with open(os.path.join("logs", f"{datetime.now()}.txt"), mode="w") as log_file:
            for path in paths:
                num_success = 0
                num_failures = 0
                print("\n==========================================")
                print(f"Processing files in {path}...\n")
                for root, dirs, files in os.walk(path):
                    for file in files:
                        true_file_path = os.path.join(root, file)
                        if should_skip_file(true_file_path):
                            total_skips += 1
                            print(f"Skipping {true_file_path} as ignored")
                            continue

                        if recency_util.file_processed_recently(true_file_path):
                            total_skips += 1
                            print(f"Skipping {true_file_path} as processed recently")
                            continue

                        saved_file_path = true_file_path.replace(path, "")
                        file_size = os.path.getsize(true_file_path)
                        file_crc = get_checksum(true_file_path)

                        file_record = FileRecord(saved_file_path, file_size, file_crc)
                        passed, message = mongo_util.process_file_record(root, file_record)
                        if passed:
                            print(f"PASS: {message} - {file_record}")
                            num_success = num_success + 1
                            # We only want to log successful files as processed
                            recency_util.record_file_processed(true_file_path)
                        else:
                            _print_and_write(f"FAIL: {message} - {file_record}", latest_log_file, log_file)
                            num_failures = num_failures + 1
                            failed_files.append(f"{true_file_path} - {message}")

                print(f"\nSuccesses in {path}: {num_success}")
                print(f"Failures in {path}:  {num_failures}")
                total_successes = total_successes + num_success

            print("\n===================================")
            os.makedirs("logs", exist_ok=True)

            _print_and_write(f"Total successes: {total_successes}", latest_log_file, log_file)
            _print_and_write(f"Total failures:  {len(failed_files)}", latest_log_file, log_file)
            _print_and_write(f"Total skips:  {total_skips}", latest_log_file, log_file)


def _print_and_write(message: str, latest_log_file: IO, log_file: IO):
    print(message)
    latest_log_file.write(message)
    latest_log_file.write("\n")
    log_file.write(message)
    log_file.write("\n")


if __name__ == "__main__":
    main()
