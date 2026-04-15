import pyray as rl

from collections.abc import Callable
from typing import cast

from .entity import Entity

from src.maze import Maze
from src.type import vec2i, vec2f, Direction


class Pac_man(Entity):
    """Player-controlled Pac-Man entity."""

    def __init__(
        self,
        screen_pos: vec2f,
        maze_pos: vec2i,
        sprite: rl.Texture,
        m: Maze,
        default_velocity_px: int,
        textures: dict[str, dict[str, list[rl.Texture]] |
                       list[rl.Texture]],
    ) -> None:
        """
        Initialize Pac-Man.

        screen_pos          -- initial pixel position on screen
        maze_pos            -- initial cell position in the maze grid
        sprite              -- starting texture
        m                   -- reference to the game maze
        default_velocity_px -- base movement speed in pixels per second
        textures            -- full texture atlas used for all animations
        """
        super().__init__(screen_pos, maze_pos, sprite, m, default_velocity_px)
        self.input: vec2i | None = None
        self.velocity_px = int(self.default_velocity_px * 0.80)
        self.turn_window: float = 2
        self.textures: dict[str, list[rl.Texture]] = cast(
            dict[str, list[rl.Texture]], textures["pac_man"]
        )
        self.prev_direction: vec2i = (0, 0)

        self.dying: bool = False
        self.dying_frame: int = 0
        self.dying_timer: float = 0.0
        self.dying_frame_duration: float = 0.08
        self.move_frame_duration: float = 8 / 60

    def try_corner(self, maze_to_screen: Callable[[vec2i], vec2i]) -> bool:
        """
        Attempt a smooth corner turn while Pac-Man is in motion.

        Return True and commit the turn if Pac-Man is close enough to the
        center of his target cell and the requested perpendicular direction is
        valid; return False otherwise.
        """
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

    def animate(self, dt: float) -> None:
        """Advance the animation frame for the current movement or dying
        state."""
        if self.dying:
            self.dying_timer += dt

            while self.dying_timer >= self.dying_frame_duration:
                self.dying_timer -= self.dying_frame_duration
                if self.dying_frame < 14:
                    self.dying_frame += 1
                else:
                    self.dying = False

            self.sprite = self.textures["dying"][self.dying_frame]
            return

        self.tick += 1
        dx, dy = self.direction

        if dx == 0 and dy == 0:
            self.anim_timer = 0.0
            self.anim_frame = 0
            self.sprite = self.textures["dying"][0]
            return

        self.anim_timer += dt

        while self.anim_timer >= self.move_frame_duration:
            self.anim_timer -= self.move_frame_duration
            self.anim_frame = (self.anim_frame + 1) % 2

        idx = self.anim_frame

        if dx == 1:
            self.sprite = self.textures["right"][idx]
        elif dx == -1:
            self.sprite = self.textures["left"][idx]
        elif dy == 1:
            self.sprite = self.textures["down"][idx]
        elif dy == -1:
            self.sprite = self.textures["up"][idx]

    def update(self, dt: float = 0.0) -> None:
        """
        Update Pac-Man's movement intent and target cell.

        Apply the buffered input direction when valid, handle reverse-direction
        requests mid-cell, and set origin/target cells for the movement system.
        """
        self.prev_direction = self.direction

        if self.dying:
            self.direction = (0, 0)
            self.origin_cell = None
            self.target_cell = None
            return

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
