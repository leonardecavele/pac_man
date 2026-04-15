from abc import ABC, abstractmethod
from enum import Enum, auto
from pydantic import BaseModel, Field


class ViewEventType(Enum):
    """Categories of event that a View can emit to the application loop."""

    NONE = auto()
    START_GAME = auto()
    CHANGE_VIEW = auto()
    QUIT = auto()
    END = auto()


class ViewEvent(BaseModel):
    """Event emitted by a View at the end of each update tick."""

    type: ViewEventType = Field(...)
    message: str = Field(default="")


class View(ABC):
    """Abstract base class for all application screens (menu, game, end, etc.)."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        """Render the view contents for the current frame."""
        pass

    @abstractmethod
    def update(self, dt: float) -> ViewEvent:
        """Update view state and return an event describing any state change."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Release any resources owned by this view."""
        pass

    @abstractmethod
    def resize(self) -> None:
        """Recompute layout after the window has been resized."""
        pass
