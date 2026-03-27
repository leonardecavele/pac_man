from .entity import Entity

from src.maze import Maze
from src.type import vec2


class Pac_man(Entity):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m)
        self.next_direction: vec2 | None = None

    def _can_move(self, direction: vec2) -> bool:
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

    # called every tick
    def update(self) -> None:
        if (
            self.next_direction is not None
            and self._can_move(self.next_direction)
        ):
            self.direction = self.next_direction

        if self.direction != (0, 0) and not self._can_move(self.direction):
            self.direction = (0, 0)
