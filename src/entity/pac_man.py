from .entity import DEFAULT_VELOCITY, Entity

from src.maze import Maze
from src.type import vec2i, vec2f


class Pac_man(Entity):
    def __init__(
        self, screen_pos: vec2f, maze_pos: vec2i, sprite: str, m: Maze
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m)
        self.input: vec2i | None = None
        self.velocity = int(DEFAULT_VELOCITY * 0.80)

    def update(self, dt: float = 0.0) -> None:
        if self.target_cell is not None:
            if (
                self.input is not None
                and self.back_direction is not None
                and Maze.Direction(self.input) == self.back_direction
                and self.origin_cell is not None
            ):
                self.direction = self.input
                self.origin_cell, self.target_cell = (
                    self.target_cell,
                    self.origin_cell,
                )
            return

        wanted_direction: vec2i | None = None

        if self.input is not None and self.valid_direction(self.input):
            wanted_direction = self.input
        elif self.direction != (0, 0) and self.valid_direction(self.direction):
            wanted_direction = self.direction
        else:
            self.direction = (0, 0)
            return

        self.direction = wanted_direction
        self.origin_cell = self.maze_pos
        self.target_cell = (
            self.maze_pos[0] + self.direction[0],
            self.maze_pos[1] + self.direction[1],
        )
