import zlib

CHUNK_SIZE = 1024 * 1024


def get_crc32(file_path: str) -> str:
    """Compute the CRC-32 checksum of the contents of the given filename"""
    checksum = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            checksum = zlib.crc32(chunk, checksum)

    return "%X" % (checksum & 0xFFFFFFFF)
