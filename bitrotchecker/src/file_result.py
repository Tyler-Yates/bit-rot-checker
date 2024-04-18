from dataclasses import dataclass

from bitrotchecker.src.file_result_enum import FileResultValue


@dataclass
class FileResult:
    value: FileResultValue
    message: str
