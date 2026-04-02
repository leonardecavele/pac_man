import math

from src.entity import Entity
from src.maze import Maze
from src.type import vec2i, vec2f


class MazeGeometry:
    def __init__(self, maze: Maze, gap: int, cell_size: int) -> None:
        self.maze = maze
        self.gap = gap
        self.cell_size = cell_size

    def maze_to_screen(self, pos: vec2i) -> vec2i:
        x, y = pos
        step: int = self.cell_size + self.gap
        screen_x: int = self.gap + x * step + self.cell_size // 2
        screen_y: int = self.gap + y * step + self.cell_size // 2
        return (screen_x, screen_y)

    def sync_maze_screen_pos(self, entity: Entity) -> None:
        sx, sy = entity.screen_pos
        step: int = self.cell_size + self.gap
        dx, dy = entity.direction

        raw_x: float = (sx - self.gap - self.cell_size / 2) / step
        raw_y: float = (sy - self.gap - self.cell_size / 2) / step

        mx: int = math.floor(raw_x) if dx > 0 else math.ceil(raw_x) if dx < 0 else round(raw_x)
        my: int = math.floor(raw_y) if dy > 0 else math.ceil(raw_y) if dy < 0 else round(raw_y)

        entity.maze_pos = (
            max(0, min(mx, self.maze.width - 1)),
            max(0, min(my, self.maze.height - 1)),
        )

    def get_draw_pos(self, screen_pos: vec2f) -> tuple[int, int]:
        x, y = screen_pos
        return (
            round(x) - self.cell_size // 2 + 1,
            round(y) - self.cell_size // 2 + 1,
        )
