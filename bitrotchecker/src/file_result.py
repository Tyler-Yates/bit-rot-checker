from dataclasses import dataclass

from bitrotchecker.src.file_result_enum import FileResultStatus


@dataclass
class FileResult:
    value: FileResultStatus
    message: str
