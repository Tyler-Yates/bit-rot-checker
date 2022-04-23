import os

import requests

from bitrotchecker.src.configuration_util import get_paths, get_healthcheck_url
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_util import get_checksum_of_file, should_skip_file
from bitrotchecker.src.logger_util import LoggerUtil
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
    os.makedirs("logs", exist_ok=True)

    with LoggerUtil() as logger:
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
                    file_modified_time = os.path.getmtime(true_file_path)
                    file_size = os.path.getsize(true_file_path)
                    file_crc = get_checksum_of_file(true_file_path)

                    file_record = FileRecord(saved_file_path, file_modified_time, file_size, file_crc)
                    passed, message = mongo_util.process_file_record(root, file_record, logger)
                    if passed:
                        print(f"PASS: {message} - {file_record}")
                        num_success = num_success + 1
                        # We only want to log successful files as processed
                        recency_util.record_file_processed(true_file_path)
                    else:
                        logger.write(f"FAIL: {message} - {file_record}")
                        num_failures = num_failures + 1
                        failed_files.append(f"{true_file_path} - {message}")

            print(f"\nSuccesses in {path}: {num_success}")
            print(f"Failures in {path}:  {num_failures}")
            total_successes = total_successes + num_success

        print("\n===================================")
        logger.write(f"Total successes: {total_successes}")
        logger.write(f"Total failures:  {len(failed_files)}")
        logger.write(f"Total skips:  {total_skips}")

    # If we have a healthcheck URL, ping it if there were no errors
    healthcheck_url = get_healthcheck_url()
    if healthcheck_url is None:
        print("No healthcheck URL. Skipping.")
        return

    total_failures = len(failed_files)
    if total_failures > 0:
        print(f"There were {total_failures} errors. Not sending healthcheck.")
        return

    try:
        requests.get(healthcheck_url, timeout=10)
        print(f"Pinged healthcheck {healthcheck_url}")
    except requests.RequestException as e:
        print(f"Ping failed: {e}")


if __name__ == "__main__":
    main()
