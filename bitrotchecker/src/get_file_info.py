import sys

from bitrotchecker.src.file_record import FileRecord
from bitrotchecker.src.mongo_util import MongoUtil


def main():
    file_path = sys.argv[1]

    if not file_path.startswith("\\"):
        file_path = "\\" + file_path

    print("File: " + file_path)
    file_record = FileRecord(file_path=file_path, full_file_path="")
    print(file_record.file_id)

    mongo_util = MongoUtil()
    records = mongo_util.get_all_records_for_file_id(file_record.file_id)
    for record in records:
        print("=" * 50)
        print(record)
        print(format(record["checksum"], 'X'))
        print("=" * 50)


if __name__ == '__main__':
    main()
