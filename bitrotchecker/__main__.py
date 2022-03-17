import os
from typing import List

from cryptography.fernet import Fernet

from bitrotchecker.file_util import get_crc32
from bitrotchecker.mongo_util import get_files_collection
from bitrotchecker.secret_util import get_fernet_key


def main():
    key = get_fernet_key()
    fernet = Fernet(key)

    paths = _get_paths()
    for path in paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_crc = get_crc32(file_path)
                print(f"{file_path} - {file_crc}")

    data = "D:\\Program Files\\Test\\SomeReallyLongFolder\\asdfkljalksdghlkasdhglkhaslkdghlashdglkashldgkhalksdghl.txt"

    encoded_data = fernet.encrypt(data.encode())
    print(encoded_data.decode())
    print(fernet.decrypt(encoded_data).decode())

    # files_collection = get_files_collection()


def _get_paths() -> List[str]:
    paths = []

    with open("paths.txt", mode='r') as paths_files:
        for line in paths_files.readlines():
            if line.startswith("#") or (not line):
                continue

            paths.append(line.strip())

    return paths


if __name__ == '__main__':
    main()
