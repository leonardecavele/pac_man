import math

from abc import ABC, abstractmethod

import pyray as rl

from src.maze import Maze
from src.type import vec2i, vec2f, Direction


class Entity(ABC):
    def __init__(
        self,
        screen_pos: vec2f,
        maze_pos: vec2i,
        sprite: rl.Texture,
        maze: Maze,
        default_velocity_px: int = 0
    ) -> None:
        self.screen_pos: vec2f = screen_pos
        self.maze_pos: vec2i = maze_pos

        self.direction: vec2i = (0, 0)
        self.origin_cell: vec2i | None = None
        self.target_cell: vec2i | None = None
        self.default_velocity_px: int = default_velocity_px
        self.velocity_px = self.default_velocity_px

        self.maze: Maze = maze

        self.sprite: rl.Texture = sprite
        self.tick = 0

        self.anim_timer: float = 0.0
        self.anim_frame: int = 0

    def move_to_target(self, dt: float, target_screen_pos: vec2i) -> bool:
        x, y = self.screen_pos
        tx, ty = target_screen_pos

        dx: float = tx - x
        dy: float = ty - y
        distance: float = math.sqrt(dx * dx + dy * dy)
        step: float = self.velocity_px * dt

        if distance == 0 or distance <= step:
            self.screen_pos = (float(tx), float(ty))
            return True

        self.screen_pos = (
            x + dx / distance * step,
            y + dy / distance * step,
        )
        return False

    def valid_direction(self, direction: vec2i) -> bool:
        return self.valid_direction_from(self.maze_pos, direction)

    def valid_direction_from(self, pos: vec2i, direction: vec2i) -> bool:
        x, y = pos

        if direction == Direction.TOP.value:
            return not self.maze.maze[y][x].top
        if direction == Direction.RIGHT.value:
            return not self.maze.maze[y][x].right
        if direction == Direction.BOT.value:
            return not self.maze.maze[y][x].bot
        if direction == Direction.LEFT.value:
            return not self.maze.maze[y][x].left
        return False

    @property
    def back_direction(self) -> Direction | None:
        if self.direction == (0, 0):
            return None
        return Direction((-self.direction[0], -self.direction[1]))

    @abstractmethod
    def update(self, dt: float = 0.0) -> None:
        pass
