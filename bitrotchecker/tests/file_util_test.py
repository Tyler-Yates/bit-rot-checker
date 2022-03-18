import tempfile

from bitrotchecker.src.file_util import get_checksum


class TestFileUtil:
    def test_get_checksum(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write("test1".encode())
            temp_file.flush()

            checksum = get_checksum(temp_file.name)
            assert 2326977762 == checksum
