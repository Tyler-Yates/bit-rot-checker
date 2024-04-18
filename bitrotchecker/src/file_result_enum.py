from enum import Enum


class FileResultValue(Enum):
    # FAIL means the file is suspected to have bit-rot.
    FAIL = 1

    # PASS means the file is suspected to not have bit-rot.
    PASS = 2

    # SKIP means the file was not processed this time.
    SKIP = 3
