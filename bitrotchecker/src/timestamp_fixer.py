import os
import time
from datetime import datetime
from typing import Dict, Optional

from bitrotchecker.src.constants import MODIFIED_TIME_KEY, CHECKSUM_KEY, SIZE_KEY
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.file_util import get_checksum_of_file
from bitrotchecker.src.mongo_util import MongoUtil


def fix_file(real_file_path: str, database_file_path: str, mongo_util: MongoUtil, verify_checksum: bool):
    file_to_fix = FileRecord(file_path=database_file_path, full_file_path=real_file_path)

    # Calculating checksum is expensive, so only do it if necessary
    file_checksum = get_checksum_of_file(real_file_path) if verify_checksum else None

    print()
    print(f"Processing {real_file_path} - {file_to_fix.file_id}")
    print(f"Current Modified Time: {file_to_fix.modified_time}")

    file_records = mongo_util.get_all_records_for_file_id(file_to_fix.file_id)
    best_match_file_record: Optional[Dict] = None
    num_id_matches = 0
    for file_record in file_records:
        num_id_matches += 1
        database_size = file_record[SIZE_KEY]
        database_checksum = file_record[CHECKSUM_KEY]

        if database_size == file_to_fix.size:
            if file_checksum is None or database_checksum == file_checksum:
                print(f"Found a match in database: {file_record}")
                if best_match_file_record is None:
                    best_match_file_record = file_record
                else:
                    print(
                        "FAIL: Multiple database matches with the same size and checksum found. "
                        "You will need to manually pick which one to use."
                    )
                    return
            else:
                print(f"Mismatch checksum: local={file_checksum} vs database={database_checksum}")
        else:
            print(f"Mismatch size: local={file_to_fix.size} vs database={database_size}")

    print(f"Found {num_id_matches} ID matches in database.")

    if best_match_file_record is None:
        print("FAIL: Could not find database entry to fix timestamp.")
    else:
        database_mtime = best_match_file_record[MODIFIED_TIME_KEY]

        if database_mtime == file_to_fix.modified_time:
            print("SKIP: File mtime already matches database")
            return

        mtime_nanos = _get_nanos_from_mtime(database_mtime)
        print(f"Setting modified time to: {mtime_nanos} nanos")
        os.utime(real_file_path, ns=(mtime_nanos, mtime_nanos))
        print("PASS: Timestamp updated to match with database.")


def fix_files_in_folder(prefix: str, folder: str, mongo_util: MongoUtil, verify_checksum: bool):
    root_path = os.path.join(prefix, folder)
    for root, dirs, files in os.walk(root_path, topdown=False):
        for file_name in files:
            real_file_path = os.path.join(root, file_name)
            database_file_path = real_file_path.replace(prefix, "")

            fix_file(real_file_path, database_file_path, mongo_util, verify_checksum)


def _get_nanos_from_mtime(db_mtime: float) -> int:
    """
    Floats are annoying and can lead to precision errors when trying to set the modified time of the files.
    Use integers with nanoseconds to try and avoid these.
    """
    truncated_nanos = int(db_mtime) * (10**9)
    num_digits = len(str(truncated_nanos))

    str_nanos = str(db_mtime).replace(".", "").ljust(num_digits, "0")
    return int(str_nanos)


def main():
    ts = time.time()
    utc_offset = (datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()
    print(f"Timezone offset: {utc_offset}")

    mongo_util = MongoUtil()
    verify_checksum = True

    with open("timestamp_fix_paths.txt", encoding="utf-8") as input_file:
        for line in input_file.readlines():
            splits = line.split(",")
            prefix = splits[0].strip()
            folder = splits[1].strip()
            print("===================================================")
            print(f"Fixing modified timestamp for folder: {folder}")
            fix_files_in_folder(prefix, folder, mongo_util, verify_checksum)


if __name__ == "__main__":
    main()
