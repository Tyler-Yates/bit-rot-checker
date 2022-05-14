import io

# noinspection PyProtectedMember
import os.path
from typing import List

from bitrotchecker.src.file_util import _get_checksum, should_skip_file


class TestFileUtil:
    def test_get_checksum(self):
        checksum = _get_checksum(io.BytesIO(b"test1"))
        assert 2326977762 == checksum

    def test_skip_prefixes_true(self):
        assert should_skip_file(self._create_file_path(["C:", "Program Files", "MyProgram", ".stver", "test.txt"]))
        assert should_skip_file(self._create_file_path(["C:", "Program Files", "MyProgram", ".stversions", "test.txt"]))

    def test_skip_prefixes_false(self):
        assert not should_skip_file(self._create_file_path(["C:", "Program Files", "MyProgram", "test.txt"]))
        assert not should_skip_file(self._create_file_path(["C:", "Program Files", "stversions", "test.txt"]))

    def test_skip_suffixes_true(self):
        assert should_skip_file(self._create_file_path(["C:", "Program Files", "MyProgram", "test.txt.tmp"]))
        assert should_skip_file(self._create_file_path(["C:", "Program Files", "MyProgram", ".tmp", "test.txt"]))

    def test_skip_suffixes_false(self):
        assert not should_skip_file(self._create_file_path(["C:", "Program Files", "temp", "test.txt"]))
        assert not should_skip_file(self._create_file_path(["C:", "Program Files", ".tmp.5", "test.txt"]))

    @staticmethod
    def _create_file_path(file_paths: List[str]) -> str:
        return os.path.sep.join(file_paths)
