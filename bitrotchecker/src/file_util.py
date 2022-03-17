import os.path
import zlib

CHUNK_SIZE = 1024 * 1024

SKIP_PREFIXES = [".st"]


def get_crc32(file_path: str) -> str:
    """Compute the CRC-32 checksum of the contents of the given filename"""
    checksum = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            checksum = zlib.crc32(chunk, checksum)

    return "%X" % (checksum & 0xFFFFFFFF)


def should_skip_folder(folder_path: str) -> bool:
    folder_names = folder_path.split(os.path.sep)

    for prefix in SKIP_PREFIXES:
        for folder_name in folder_names:
            if folder_name.startswith(prefix):
                return True

    return False
