from enum import IntEnum, auto


class ErrorCode(IntEnum):
    """Exit codes returned by the application on failure or success."""

    NO_ERROR = 0
    FILE_NOT_FOUND = auto()
    NO_READ_PERMISSION = auto()
    INVALID_JSON = auto()
    INVALID_CONFIG = auto()
    INVALID_TYPE = auto()
