import json
import sys
from pydantic import ValidationError

from src.error import ErrorCode
from src.parsing import Config


class Parser:
    """Parse and validate a JSON (with comments) game configuration file."""

    def __init__(self, config_path: str):
        """Initialize the parser with the absolute path to the config file."""
        self.config_path = config_path

    def run(self) -> Config:
        """Read, parse, and validate the configuration file.

        Return a validated Config instance on success.
        Exit the process with an appropriate ErrorCode on any failure.
        """
        tmp = ""
        try:
            with open(self.config_path, "r") as config:
                for line in config:
                    if (not line.strip().startswith("#")
                            and not line.strip().startswith("//")):
                        tmp += line
        except UnicodeDecodeError:
            print(f"{self.config_path} has invalid type")
            sys.exit(ErrorCode.INVALID_TYPE)
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
