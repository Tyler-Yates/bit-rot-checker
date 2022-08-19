import os
import time
from datetime import datetime

from bitrotchecker.src.constants import MODIFIED_TIME_KEY
from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.mongo_util import MongoUtil


def fix_file(real_file_path: str, database_file_path: str, utc_offset: float, mongo_util: MongoUtil):
    file_id = FileRecord._calculate_file_id(database_file_path)

    current_mtime = os.path.getmtime(real_file_path)
    print()
    print(f"Processing {real_file_path} - {file_id}")
    fixed_mtime = current_mtime + utc_offset
    print(f"Current Modified Time         : {current_mtime}")
    print(f"Proposed correct Modified Time: {fixed_mtime}")

    file_records = mongo_util.get_all_records_for_file_id(file_id)
    for file_record in file_records:
        database_mtime = file_record[MODIFIED_TIME_KEY]
        if int(database_mtime) == int(fixed_mtime):
            print("Found match in database with fixed time. Correct timestamp of file on disk.")
            # Use the database time to get back millisecond precision if present
            os.utime(real_file_path, (database_mtime, database_mtime))
            return

    # If we get to this point, there were no database records matching.
    print("Could not find database entry to fix timestamp")


def fix_files_in_folder(folder: str, utc_offset: float, mongo_util: MongoUtil):
    for root, dirs, files in os.walk(folder, topdown=False):
        for file_name in files:
            real_file_path = os.path.join(root, file_name)
            database_file_path = real_file_path.replace(folder, "")

            fix_file(real_file_path, database_file_path, utc_offset, mongo_util)


def main():
    ts = time.time()
    utc_offset = (datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()
    print(f"Timezone offset: {utc_offset}")

    mongo_util = MongoUtil()

    with open("timestamp_fix_paths.txt") as input_file:
        for line in input_file.readlines():
            input_folder = line.strip()
            print(f"Fixing modified timestamp for folder: {input_folder}")
            fix_files_in_folder(input_folder, utc_offset, mongo_util)


if __name__ == "__main__":
    main()
