import os
import pickle
from datetime import datetime
from typing import Optional, Tuple, Dict

from atomicwrites import atomic_write

from bitrotchecker.src.constants import RECENCY_FILE_NAME, RECENCY_MINIMUM_AGE_DAYS


class RecencyUtil:
    def __init__(self, recency_file_path=RECENCY_FILE_NAME):
        self.recency_dict = dict()
        self.recency_file_path = recency_file_path

        if os.path.exists(self.recency_file_path):
            with open(self.recency_file_path, mode="rb") as recency_file:
                self.recency_dict: Dict[str, Tuple] = pickle.load(recency_file)

    def _save_pickle(self):
        with atomic_write(self.recency_file_path, mode="wb", overwrite=True) as recency_file:
            recency_file.write(pickle.dumps(self.recency_dict, protocol=pickle.HIGHEST_PROTOCOL))

    def record_file_processed(self, true_file_path: str, file_modified_time: float):
        self.recency_dict[true_file_path] = (datetime.now(), file_modified_time)
        self._save_pickle()

    def file_processed_recently(self, true_file_path: str, file_modified_time: float) -> bool:
        recency_tuple: Optional[Tuple[datetime, datetime]] = self.recency_dict.get(true_file_path, None)
        if recency_tuple is None:
            return False

        datetime_last_processed = recency_tuple[0]
        recorded_last_modified_time = recency_tuple[1]

        # If the file was modified since the last time we saw it, we need to check it again
        if file_modified_time != recorded_last_modified_time:
            self._remove_recency_record(true_file_path)
            return False

        # If the file is not modified, check if we should read it fully
        datetime_diff = datetime.now() - datetime_last_processed
        return datetime_diff.days < RECENCY_MINIMUM_AGE_DAYS

    def clean_records(self, age_in_days_to_clean=RECENCY_MINIMUM_AGE_DAYS):
        file_paths_to_remove = []

        for file_path, information_tuple in self.recency_dict.items():
            days_since_record = (datetime.now() - information_tuple[0]).days
            if days_since_record >= age_in_days_to_clean:
                file_paths_to_remove.append(file_path)

        for file_path in file_paths_to_remove:
            self.recency_dict.pop(file_path)
        self._save_pickle()

    def _remove_recency_record(self, true_file_path: str):
        removed_record = self.recency_dict.pop(true_file_path, None)

        if removed_record is None:
            print(f"File path {true_file_path} was not in the recency dictionary")
        else:
            self._save_pickle()
