import io

# noinspection PyProtectedMember
from bitrotchecker.src.file_util import _get_checksum


class TestFileUtil:
    def test_get_checksum(self):
        checksum = _get_checksum(io.BytesIO(b"test1"))
        assert 2326977762 == checksum
