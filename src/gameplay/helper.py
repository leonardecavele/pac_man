import math

from src.entity import Entity
from src.maze import Maze
from src.type import vec2i, vec2f


class GameGeometry:
    """Compute and expose the pixel-level geometry used to render the maze."""

    def __init__(self, width: int, height: int, maze: Maze) -> None:
        """
        Initialize game geometry for the given viewport dimensions.

        width  -- viewport width in pixels
        height -- viewport height in pixels
        maze   -- maze whose dimensions drive the cell/gap calculations
        """
        self.maze = maze
        self.width = width
        self.height = height
        self._compute_cell_gap_size()

    def _compute_cell_gap_size(self) -> None:
        """Compute the largest cell_size and gap that fit the maze in the viewport."""
        self.gap = 18
        margin = int(self.height * 0.2)
        while self.gap >= 0:
            self.cell_size = min(
                (self.width - margin - (self.maze.width + 1)
                 * self.gap) // self.maze.width,
                (self.height - margin - (self.maze.height + 1)
                 * self.gap) // self.maze.height,
            ) - 1
            if self.gap >= self.cell_size:
                self.gap -= 2
                continue
            break

    def maze_to_screen(self, pos: vec2f) -> vec2i:
        """Convert a maze grid position to the centre pixel position on screen."""
        x, y = pos
        step: int = self.cell_size + self.gap
        screen_x: int = int(self.gap + x * step + self.cell_size // 2)
        screen_y: int = int(self.gap + y * step + self.cell_size // 2)
        return (screen_x, screen_y)

    def sync_maze_screen_pos(self, entity: Entity) -> None:
        """Update entity.maze_pos to reflect its current screen_pos and direction."""
        sx, sy = entity.screen_pos
        step: int = self.cell_size + self.gap
        dx, dy = entity.direction

        raw_x: float = (sx - self.gap - self.cell_size / 2) / step
        raw_y: float = (sy - self.gap - self.cell_size / 2) / step

        mx: int = math.floor(raw_x) if dx > 0 else math.ceil(
            raw_x) if dx < 0 else round(raw_x)
        my: int = math.floor(raw_y) if dy > 0 else math.ceil(
            raw_y) if dy < 0 else round(raw_y)

        entity.maze_pos = (
            max(0, min(mx, self.maze.width - 1)),
            max(0, min(my, self.maze.height - 1)),
        )

    def get_draw_pos(self, screen_pos: vec2f) -> tuple[int, int]:
        """Return the top-left pixel coordinate at which to draw an entity sprite."""
        x, y = screen_pos
        return (
            round(x) - self.cell_size // 2 + 1,
            round(y) - self.cell_size // 2 + 1,
        )
