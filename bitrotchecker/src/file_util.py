import os.path
import zlib
from typing import IO

from bitrotchecker.src.constants import CHUNK_SIZE, SKIP_PREFIXES, SKIP_SUFFIXES


def get_checksum_of_file(file_path: str) -> int:
    with open(file_path, "rb") as file:
        return _get_checksum(file)


def _get_checksum(file: IO):
    checksum = 0
    while chunk := file.read(CHUNK_SIZE):
        checksum = zlib.crc32(chunk, checksum)
    return checksum & 0xFFFFFFFF


def should_skip_file(file_path: str) -> bool:
    path_parts = file_path.split(os.path.sep)

    for path_parth in path_parts:
        for prefix in SKIP_PREFIXES:
            if path_parth.startswith(prefix):
                return True
        for suffix in SKIP_SUFFIXES:
            if path_parth.endswith(suffix):
                return True

    return False
