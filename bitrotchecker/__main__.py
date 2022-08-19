import os

import requests

from bitrotchecker.src.configuration_util import get_healthcheck_url, get_mutable_paths, get_immutable_paths
from bitrotchecker.src.file_processor import FileProcessor
from bitrotchecker.src.logger_util import LoggerUtil
from bitrotchecker.src.mongo_util import MongoUtil
from bitrotchecker.src.recency_util import RecencyUtil


def main():
    mongo_util = MongoUtil()
    recency_util = RecencyUtil()

    # Clean recency util so it does not balloon forever
    recency_util.clean_records()

    # To get data on the current database, uncomment next line
    # mongo_util.get_size_of_documents()

    immutable_paths = get_immutable_paths()
    mutable_paths = get_mutable_paths()
    all_paths = immutable_paths + mutable_paths

    total_successes = 0
    total_skips = 0
    os.makedirs("logs", exist_ok=True)

    with LoggerUtil() as logger:
        file_processor = FileProcessor(recency_util, mongo_util, logger)
        for path in all_paths:
            is_immutable = path in immutable_paths
            num_skips = 0
            num_success = 0
            num_failures = 0
            print("\n==========================================")
            print(f"Processing files in {path}...\n")
            for root, dirs, files in os.walk(path):
                for file in files:
                    true_file_path = os.path.join(root, file)
                    success = file_processor.process_file(
                        root=root, path=path, true_file_path=true_file_path, file_is_immutable=is_immutable
                    )
                    if success is None:
                        num_skips += 1
                    elif success:
                        num_success += 1
                    else:
                        num_failures += 1

            print(f"\nSuccesses in {path}: {num_success}")
            print(f"Failures in {path}:  {num_failures}")
            print(f"Skips in {path}:  {num_skips}")
            total_successes = total_successes + num_success
            total_skips = total_skips + num_skips

        failed_files = file_processor.failed_files

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
