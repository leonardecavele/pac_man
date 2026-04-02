from abc import ABC, abstractmethod

import pyray as rl

from src.maze import Maze
from src.type import vec2

DEFAULT_VELOCITY: int = 100


class Entity(ABC):
    def __init__(
        self,
        screen_pos: vec2,
        maze_pos: vec2,
        sprite: rl.Texture2D,
        maze: Maze,
    ) -> None:
        self.screen_pos: vec2 = screen_pos
        self.maze_pos: vec2 = maze_pos
        self.sprite: rl.Texture2D = sprite
        self.direction: vec2 = (0, 0)
        self.velocity: int = DEFAULT_VELOCITY
        self.maze: Maze = maze

    @property
    def back_direction(self) -> Maze.Direction | None:
        if self.direction == (0, 0):
            return None
        return Maze.Direction((-self.direction[0], -self.direction[1]))

    @abstractmethod
    def update(self, dt: float = 0.0) -> None:
        pass
