from bitrotchecker.src.file_record import FileRecord


class TestFileRecord:
    def test_file_record(self):
        file_record = FileRecord("C:\\Some Folder\\Some File.txt", 12345.6, 100, 7777777)
        assert file_record.file_id == "52874b88c10c6e35478ff33c6ac67d6c91de5a23fb8c7b2c5ed21c1e7686624a"

        # File ID should NOT be based on modified time
        file_record = FileRecord("C:\\Some Folder\\Some File.txt", 999, 100, 7777777)
        assert file_record.file_id == "52874b88c10c6e35478ff33c6ac67d6c91de5a23fb8c7b2c5ed21c1e7686624a"
