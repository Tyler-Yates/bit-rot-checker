import json
from typing import Dict

SECRETS_FILE_NAME = "secrets.json"


def _read_secret_file() -> Dict[str, str]:
    with open(SECRETS_FILE_NAME) as secret_file:
        json_data = json.load(secret_file)

    return json_data


def get_mongo_connection_string() -> str:
    return _read_secret_file()["mongo_connection_string"]
