import os
import tempfile

from bitrotchecker.src.recency_util import RecencyUtil


class TestRecencyUtil:
    def test_record_file_processed(self):
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            recency_file_path = os.path.join(tmp_dir_path, "recency.pickle")
            recency_util = RecencyUtil(recency_file_path=recency_file_path)

            # Record a file
            file_path = "myFile"
            modified_time = 12345.123
            assert recency_util.file_processed_recently(file_path, modified_time) is False
            recency_util.record_file_processed(file_path, modified_time)
            assert recency_util.file_processed_recently(file_path, modified_time) is True

            # Verify the file we recorded from before is still there
            recency_util = RecencyUtil(recency_file_path=recency_file_path)
            assert recency_util.file_processed_recently(file_path, modified_time) is True
            assert recency_util.file_processed_recently(file_path, modified_time + 999.9) is False

    def test_clean_records(self):
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            recency_file_path = os.path.join(tmp_dir_path, "recency.pickle")
            recency_util = RecencyUtil(recency_file_path=recency_file_path)

            # Record some files
            recency_util.record_file_processed("file1", 12345.123)
            recency_util.record_file_processed("file2", 12345.123)
            recency_util.record_file_processed("file3", 12345.123)
            assert len(recency_util.recency_dict) == 3

            # 999 days means all records should stay
            recency_util.clean_records(age_in_days_to_clean=999)
            assert len(recency_util.recency_dict) == 3

            # 0 days means all records should be cleared
            recency_util.clean_records(age_in_days_to_clean=0)
            assert len(recency_util.recency_dict) == 0
