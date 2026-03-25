from enum import IntEnum, auto


class ErrorCode(IntEnum):
    NO_ERROR = 0
    FILE_NOT_FOUND = auto()
    NO_READ_PERMISSION = auto()
    INVALID_JSON = auto()
    INVALID_CONFIG = auto()
