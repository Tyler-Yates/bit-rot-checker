import os
from datetime import datetime
from typing import IO, Optional


class LoggerUtil:
    def __init__(self):
        self.latest_log_file: Optional[IO] = None
        self.dated_log_file: Optional[IO] = None

    def __enter__(self):
        log_file_name = f"{datetime.now()}.txt".replace(":", "_")
        self.latest_log_file = open(os.path.join("logs", "latest.txt"), mode="w")
        self.dated_log_file = open(os.path.join("logs", log_file_name), mode="w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.latest_log_file:
            self.latest_log_file.close()

        if self.dated_log_file:
            self.dated_log_file.close()

    def write(self, message: str):
        print(message)

        self.latest_log_file.write(message)
        self.latest_log_file.write("\n")
        self.latest_log_file.flush()

        self.dated_log_file.write(message)
        self.dated_log_file.write("\n")
        self.dated_log_file.flush()
