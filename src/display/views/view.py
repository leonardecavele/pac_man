from abc import ABC, abstractmethod
from enum import Enum, auto
from pydantic import BaseModel, Field


class ViewEventType(Enum):
    NONE = auto()
    START_GAME = auto()
    CHANGE_VIEW = auto()
    QUIT = auto()
    END = auto()


class ViewEvent(BaseModel):
    type: ViewEventType = Field(...)
    message: str = Field(default="")


class View(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> ViewEvent:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def resize(self) -> None:
        pass
