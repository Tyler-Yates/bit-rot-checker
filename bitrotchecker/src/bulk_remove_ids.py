from bitrotchecker.src.mongo_util import MongoUtil


def main():
    ids_to_remove = set()
    with open("ids_to_remove_from_database.txt") as input_file:
        for line in input_file.readlines():
            line = line.strip()
            ids_to_remove.add(line)

    answer = input(f"This will delete {len(ids_to_remove)} file IDs from the database. Proceed? ")
    if answer.lower() not in ["y", "yes"]:
        exit(1)

    mongo_util = MongoUtil()
    for file_id in ids_to_remove:
        documents_deleted = mongo_util.remove_records_with_file_id(file_id=file_id)
        print(f"Deleted {documents_deleted} documents with file ID {file_id}")


if __name__ == '__main__':
    main()
