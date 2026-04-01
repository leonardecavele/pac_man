from abc import ABC, abstractmethod
import pyray as rl

from src.maze import Maze
from src.type import vec2

DEFAULT_VELOCITY: int = 100


class Entity(ABC):
    def __init__(
            self, screen_pos: vec2, maze_pos: vec2, sprite: rl.Texture2D,
            maze: Maze
    ) -> None:
        self.screen_pos: vec2 = screen_pos
        self.maze_pos: vec2 = maze_pos
        self.sprite: str = sprite
        self.direction: vec2 = (0, 0)
        self.velocity: int = DEFAULT_VELOCITY
        self.maze: Maze = maze

    @property
    def back_direction(self) -> Maze.Direction | None:
        if self.direction == (0, 0):
            return None
        return Maze.Direction((-self.direction[0], -self.direction[1]))

    def valid_direction(self, direction: vec2) -> bool:
        x, y = self.maze_pos

        if direction == Maze.Direction.TOP.value:
            return not self.maze.maze[y][x].top
        if direction == Maze.Direction.RIGHT.value:
            return not self.maze.maze[y][x].right
        if direction == Maze.Direction.BOT.value:
            return not self.maze.maze[y][x].bot
        if direction == Maze.Direction.LEFT.value:
            return not self.maze.maze[y][x].left
        return False

    # Called by the game loop
    @abstractmethod
    def update(self) -> None:
        pass
