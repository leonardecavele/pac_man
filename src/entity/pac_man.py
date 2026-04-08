import math
import pyray as rl

from collections.abc import Callable

from .entity import Entity

from src.maze import Maze
from src.type import vec2i, vec2f, Direction


class Pac_man(Entity):
    def __init__(
        self,
        screen_pos: vec2f,
        maze_pos: vec2i,
        sprite: str,
        m: Maze,
        default_velocity_px: int,
        textures: dict[str, dict[str, list[rl.Texture2D]] | list[rl.Texture2D]]
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m, default_velocity_px)
        self.input: vec2i | None = None
        self.velocity_px = int(self.default_velocity_px * 0.80)
        self.turn_window: float = 4.5
        self.textures = textures
        self.dying: bool = False

    def try_corner(self, maze_to_screen: Callable[[vec2i], vec2i]) -> bool:
        if self.target_cell is None or self.input is None:
            return False

        if self.direction == (0, 0):
            return False

        if self.input == self.direction:
            return False

        if (
            self.back_direction is not None
            and self.input == self.back_direction.value
        ):
            return False

        is_perpendicular: bool = (
            self.direction[0] != self.input[0]
            and self.direction[1] != self.input[1]
        )

        if not is_perpendicular:
            return False

        if not self.valid_direction_from(self.target_cell, self.input):
            return False

        target_x, target_y = maze_to_screen(self.target_cell)
        x, y = self.screen_pos

        if self.direction[0] != 0:
            if abs(x - target_x) > self.turn_window:
                return False
        else:
            if abs(y - target_y) > self.turn_window:
                return False

        self.screen_pos = (float(target_x), float(target_y))
        self.maze_pos = self.target_cell
        self.origin_cell = None
        self.target_cell = None
        self.direction = self.input
        self.update()
        return True

    def animate(self):
        self.tick += 1
        dx, dy = self.direction
        idx = self.tick // 8 % 2
        if (dx == 0 and dy == 0 and self.tick == 1):
            self.sprite = self.textures["pac_man"]["dying"][0]
        elif (dx == 1):
            self.sprite = self.textures["pac_man"]["right"][idx]
        elif (dx == -1):
            self.sprite = self.textures["pac_man"]["left"][idx]
        elif (dy == 1):
            self.sprite = self.textures["pac_man"]["down"][idx]
        elif (dy == -1):
            self.sprite = self.textures["pac_man"]["up"][idx]

    def update(self, dt: float = 0.0) -> None:
        if self.dying:
            self.direction = (0, 0)

        if self.target_cell is not None:
            if (
                self.input is not None
                and self.back_direction is not None
                and Direction(self.input) == self.back_direction
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
