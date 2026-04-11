from typing import TYPE_CHECKING
import pyray as rl

from .entity import Entity

from src.maze import Maze
from src.type import vec2i, vec2f
from typing import cast

if TYPE_CHECKING:
    from src.gameplay import MazeState


class Collectible(Entity):
    def __init__(
        self,
        screen_pos: vec2f,
        maze_pos: vec2f,
        sprite: rl.Texture,
        maze: Maze,
        points: int,
        default_velocity_px: int = 0
    ) -> None:
        super().__init__(
            screen_pos,
            cast(vec2i, (int(maze_pos[0]), int(maze_pos[1]))),
            sprite, maze, default_velocity_px
        )
        self.maze_pos: vec2f = maze_pos  # type: ignore[assignment]
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
    def __init__(
        self,
        screen_pos: vec2f,
        maze_pos: vec2f,
        sprite: rl.Texture,
        maze: Maze,
        points: int,
        default_velocity_px: int = 0
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, maze, points,
                         default_velocity_px)
        self.blink_interval: float = 0.15
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
