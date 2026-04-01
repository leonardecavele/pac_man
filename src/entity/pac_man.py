import math

from .entity import Entity

from src.maze import Maze
from src.type import vec2


class Pac_man(Entity):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m)
        self.input: vec2 | None = None
        self.origin_cell: vec2 | None = None
        self.target_cell: vec2 | None = None
        self.velocity = 120

    def move_to_target(self, dt: float, target_screen_pos: vec2) -> bool:
        x, y = self.screen_pos
        tx, ty = target_screen_pos

        dx: float = tx - x
        dy: float = ty - y
        distance: float = math.sqrt(dx * dx + dy * dy)
        step: float = self.velocity * dt

        if distance <= step:
            self.screen_pos = target_screen_pos
            return True

        if distance == 0:
            self.screen_pos = target_screen_pos
            return True

        self.screen_pos = (
            x + dx / distance * step,
            y + dy / distance * step,
        )
        return False

    # called every tick
    def update(self) -> None:
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

        wanted_direction: vec2 | None = None

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
