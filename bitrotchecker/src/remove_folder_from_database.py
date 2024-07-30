import os

from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.mongo_util import MongoUtil


def main():
    prefix = "A:\\Syncthing\\zenfone10\\sms_backup_zenfone10"
    folder = ""
    mongo_util = MongoUtil()

    root_path = os.path.join(prefix, folder)
    for (root, dirs, files) in os.walk(root_path):
        for f in files:
            full_file_path = str(os.path.join(root, f))
            if ".stversions" in full_file_path:
                continue

            file_record = FileRecord(file_path=full_file_path.replace(prefix, ""), full_file_path=full_file_path)
            print(f"Removing file record {file_record}")
            mongo_util.remove_records_with_file_id(file_record.file_id)


if __name__ == '__main__':
    main()
