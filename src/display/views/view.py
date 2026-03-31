from abc import ABC, abstractmethod


class View(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
