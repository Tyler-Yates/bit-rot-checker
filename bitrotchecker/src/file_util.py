import os.path
import zlib

CHUNK_SIZE = 4096

SKIP_PREFIXES = [".st"]


def get_checksum(file_path: str) -> int:
    checksum = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            checksum = zlib.crc32(chunk, checksum)

    return checksum & 0xFFFFFFFF


def should_skip_file(file_path: str) -> bool:
    path_parts = file_path.split(os.path.sep)

    for prefix in SKIP_PREFIXES:
        for path_parth in path_parts:
            if path_parth.startswith(prefix):
                return True

    return False
