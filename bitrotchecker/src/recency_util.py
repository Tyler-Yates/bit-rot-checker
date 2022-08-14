import os
import pickle
from datetime import datetime
from typing import Optional, Tuple

from atomicwrites import atomic_write

from bitrotchecker.src.constants import RECENCY_FILE_NAME, RECENCY_MINIMUM_AGE_DAYS


class RecencyUtil:
    def __init__(self):
        self.recency_dict = dict()

        if os.path.exists(RECENCY_FILE_NAME):
            with open(RECENCY_FILE_NAME, mode="rb") as recency_file:
                self.recency_dict = pickle.load(recency_file)

    def _save_pickle(self):
        with atomic_write(RECENCY_FILE_NAME, mode="wb", overwrite=True) as recency_file:
            recency_file.write(pickle.dumps(self.recency_dict, protocol=pickle.HIGHEST_PROTOCOL))

    def record_file_processed(self, true_file_path: str):
        self.recency_dict[true_file_path] = (datetime.now(), os.path.getmtime(true_file_path))
        self._save_pickle()

    def file_processed_recently(self, true_file_path: str):
        recency_tuple: Optional[Tuple[datetime, datetime]] = self.recency_dict.get(true_file_path, None)
        if recency_tuple is None:
            return False

        datetime_last_processed = recency_tuple[0]
        last_modified_time = recency_tuple[1]

        # If the file was modified since the last time we saw it, we need to check it again
        if os.path.getmtime(true_file_path) != last_modified_time:
            return False

        # If the file is not modified, check if we should read it fully
        datetime_diff = datetime.now() - datetime_last_processed
        return datetime_diff.days < RECENCY_MINIMUM_AGE_DAYS
