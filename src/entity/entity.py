from abc import ABC, abstractmethod

from src.maze import Maze
from src.type import vec2

DEFAULT_VELOCITY: int = 55


class Entity(ABC):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, maze: Maze
    ) -> None:
        self.screen_pos: vec2 = screen_pos
        self.maze_pos: vec2 = maze_pos
        self.sprite: str = sprite
        self.direction: vec2 = (0, 0)
        self.velocity: int = DEFAULT_VELOCITY
        self.maze: Maze = maze

    # Called by the game loop
    def move(self, cell_size: int) -> None:
        self.screen_pos = (
            self.screen_pos[0] + self.direction[0] * self.velocity,
            self.screen_pos[1] + self.direction[1] * self.velocity
        )
        self.maze_pos = (
            self.screen_pos[0] // cell_size,
            self.screen_pos[1] // cell_size
        )

    @abstractmethod
    def update(self) -> None:
        pass
