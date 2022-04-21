import json
from typing import Dict, List, Any, Optional

from bitrotchecker.src.constants import CONFIG_FILE_NAME


def _read_config_file() -> Dict[str, Any]:
    with open(CONFIG_FILE_NAME) as config_file:
        json_data = json.load(config_file)

    return json_data


def get_mongo_connection_string() -> str:
    return _read_config_file()["mongo_connection_string"]


def get_paths() -> List[str]:
    return _read_config_file()["paths"]


def get_healthcheck_url() -> Optional[str]:
    return _read_config_file()["healthcheck_url"]
