from typing import TYPE_CHECKING

from .entity import Entity

if TYPE_CHECKING:
    from src.gameplay import MazeState


class Collectible(Entity):
    def __init__(self, *args, points: int, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.points = points
        self.visible: bool = True

    def update(self, dt: float = 0.0) -> None:
        return

    def on_collect(self, state: "MazeState") -> None:
        state.score += self.points


class Pacgum(Collectible):
    def update(self, dt: float = 0.0) -> None:
        self.visible = True


class SuperPacgum(Collectible):
    def __init__(self, *args, points: int, **kwargs) -> None:
        super().__init__(*args, points=points, **kwargs)
        self.blink_interval: float = 0.40
        self._elapsed: float = 0.0

    def update(self, dt: float = 0.0) -> None:
        self._elapsed += dt
        if self._elapsed < self.blink_interval:
            return
        self.visible = not self.visible
        self._elapsed = 0.0

    def on_collect(self, state: "MazeState") -> None:
        super().on_collect(state)
        state.start_fright_mode()
