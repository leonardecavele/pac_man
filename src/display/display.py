import pyray as rl

from src.display.maze_renderer import MazeRenderer
from src.maze import Maze
from src.entity import Pacgum, SuperPacgum, Collectible
from src.type import vec2
from .textures import Textures
from src.entity import Entity, Blinky, Inky, Pinky, Clyde, Pac_man


class Display:
    def __init__(
        self, maze: Maze, width: int = 720, height: int = 720,
        title: str = "Pac-Man", fps: int = 60,
    ) -> None:
        self.maze: Maze = maze
        self.width: int = width
        self.height: int = height
        self.title: str = title
        self.fps: int = fps

        self._compute_cell_gap_size()

        rl.init_window(self.width, self.height, self.title)
        rl.set_target_fps(self.fps)

        self.maze_image = rl.gen_image_color(
            self.width, self.height, rl.BLACK
        )
        MazeRenderer(
            self.maze_image, self.maze, self.cell_size, self.gap
        )
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

    def draw(self, entities: list[list[Entity]]) -> None:
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)
        rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
        for i in entities:
            for e in i:
                x, y = e.screen_pos
                x -= self.cell_size // 2
                y -= self.cell_size // 2
                rl.draw_texture(e.sprite, x + 1, y + 1, rl.WHITE)
        rl.end_drawing()

    def should_close(self) -> bool:
        return rl.window_should_close()

    def get_frame_time(self) -> float:
        return rl.get_frame_time()

    def close(self) -> None:
        rl.unload_texture(self.maze_texture)
        rl.unload_image(self.maze_image)
        rl.close_window()

    def _DEBUG_grid(self):
        for i in range(self.maze.width + 1):
            rl.draw_line(i * (self.cell_size + self.gap) + self.gap // 2, 0,
                         i * (self.cell_size + self.gap) +
                         self.gap // 2, self.height,
                         rl.PURPLE)
        for i in range(self.maze.height + 1):
            rl.draw_line(0,
                         i * (self.cell_size + self.gap) + self.gap // 2,
                         self.width,
                         i * (self.cell_size + self.gap) + self.gap // 2,
                         rl.PURPLE)

    def _compute_cell_gap_size(self) -> None:
        self.gap = 18
        while self.gap >= 0:
            self.cell_size = min(
                (self.width - (self.maze.width + 1) * self.gap)
                // self.maze.width,
                (self.height - (self.maze.height + 1) * self.gap)
                // self.maze.height,
            ) - 1
            if self.gap >= self.cell_size:
                self.gap -= 2
                continue
            break

    def _maze_to_screen_pos(self, maze_pos: vec2) -> vec2:
        screen_pos: vec2 = (
            maze_pos[0] * (self.cell_size + self.gap) +
            self.gap + self.cell_size // 2 + 1,
            maze_pos[1] * (self.cell_size + self.gap) +
            self.gap + self.cell_size // 2 + 1
        )
        return (screen_pos)
