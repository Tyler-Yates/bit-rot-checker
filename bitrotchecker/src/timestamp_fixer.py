import os
import time
from datetime import datetime
from typing import Dict, Optional

from bitrotchecker.src.constants import MODIFIED_TIME_KEY, CHECKSUM_KEY, SIZE_KEY
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_util import get_checksum_of_file
from bitrotchecker.src.mongo_util import MongoUtil


def fix_file(real_file_path: str, database_file_path: str, mongo_util: MongoUtil):
    file_id = FileRecord._calculate_file_id(database_file_path)

    current_mtime = os.path.getmtime(real_file_path)
    print()
    print(f"Processing {real_file_path} - {file_id}")
    print(f"Current Modified Time: {current_mtime}")

    file_records = mongo_util.get_all_records_for_file_id(file_id)
    best_match_file_record: Optional[Dict] = None
    for file_record in file_records:
        database_size = file_record[SIZE_KEY]
        database_checksum = file_record[CHECKSUM_KEY]

        file_size = os.path.getsize(real_file_path)
        file_checksum = get_checksum_of_file(real_file_path)

        if database_size == file_size and database_checksum == file_checksum:
            print(f"Found a match in database: {file_record}")
            if best_match_file_record is None:
                best_match_file_record = file_record
            else:
                print(
                    "FAIL: Multiple database matches with the same size and checksum found. "
                    "You will need to manually pick which one to use."
                )
                return

    if best_match_file_record is None:
        print("FAIL: Could not find database entry to fix timestamp.")
    else:
        # If we did find a match, update the file's modified timestamp
        database_mtime = best_match_file_record[MODIFIED_TIME_KEY]
        print(f"Setting modified time to: {database_mtime}")
        os.utime(real_file_path, (database_mtime, database_mtime))
        print("PASS: Timestamp updated to match with database.")


def fix_files_in_folder(folder: str, mongo_util: MongoUtil):
    for root, dirs, files in os.walk(folder, topdown=False):
        for file_name in files:
            real_file_path = os.path.join(root, file_name)
            database_file_path = real_file_path.replace(folder, "")

            fix_file(real_file_path, database_file_path, mongo_util)


def main():
    ts = time.time()
    utc_offset = (datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()
    print(f"Timezone offset: {utc_offset}")

    mongo_util = MongoUtil()

    with open("timestamp_fix_paths.txt") as input_file:
        for line in input_file.readlines():
            input_folder = line.strip()
            print(f"Fixing modified timestamp for folder: {input_folder}")
            fix_files_in_folder(input_folder, mongo_util)


if __name__ == "__main__":
    main()
