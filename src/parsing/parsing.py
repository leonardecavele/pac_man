import json
import sys
from pydantic import ValidationError

from src.error import ErrorCode
from src.parsing import Config


class Parser:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def run(self) -> Config:
        tmp = ""
        try:
            with open(self.config_path, "r") as config:
                for line in config:
                    if (not line.strip().startswith("#")
                            and not line.strip().startswith("//")):
                        tmp += line
        except FileNotFoundError:
            print(f"{self.config_path} does not exists.")
            sys.exit(ErrorCode.FILE_NOT_FOUND)
        except PermissionError:
            print(f"{self.config_path} cannot be read.")
            sys.exit(ErrorCode.NO_READ_PERMISSION)
        try:
            config_dict = json.loads(tmp)
        except ValueError:
            print(f"{self.config_path}"
                  " is not a valid JSON with comments file.")
            sys.exit(ErrorCode.INVALID_JSON)
        try:
            return (Config.model_validate(config_dict))
        except ValidationError:
            print(f"{self.config_path} is invalid.")
            sys.exit(ErrorCode.INVALID_CONFIG)
