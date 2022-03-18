import os
import pickle
from datetime import datetime
from typing import Optional

from bitrotchecker.src.constants import RECENCY_FILE_NAME, RECENCY_MINIMUM_AGE_DAYS


class RecencyUtil:
    def __init__(self):
        self.recency_dict = dict()

        if os.path.exists(RECENCY_FILE_NAME):
            with open(RECENCY_FILE_NAME, mode="rb") as recency_file:
                self.recency_dict = pickle.load(recency_file)

    def _save_pickle(self):
        with open(RECENCY_FILE_NAME, mode="wb") as recency_file:
            pickle.dump(self.recency_dict, recency_file)

    def record_file_processed(self, true_file_path: str):
        self.recency_dict[true_file_path] = datetime.now()
        self._save_pickle()

    def file_processed_recently(self, true_file_path: str):
        datetime_last_processed: Optional[datetime] = self.recency_dict.get(true_file_path, None)
        if datetime_last_processed is None:
            return False

        datetime_diff = datetime.now() - datetime_last_processed
        return datetime_diff.days < RECENCY_MINIMUM_AGE_DAYS
