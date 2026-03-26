import pyray as raylib

from src.display.maze_renderer import MazeRenderer
from src.maze import Maze
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

        raylib.init_window(self.width, self.height, self.title)
        raylib.set_target_fps(self.fps)

        self.maze_image = raylib.gen_image_color(
            self.width, self.height, raylib.BLACK
        )

        renderer = MazeRenderer(
            self.maze_image, self.maze, self.cell_size, self.gap
        )
        renderer.draw()

        self.maze_texture = raylib.load_texture_from_image(self.maze_image)

    def draw(self, entities: list[Entity]) -> None:
        raylib.begin_drawing()
        raylib.clear_background(raylib.WHITE)
        raylib.draw_texture(self.maze_texture, 0, 0, raylib.WHITE)

        for entity in entities:
            x: int = int(entity.screen_pos[0])
            y: int = int(entity.screen_pos[1])

            if isinstance(entity, Pac_man):
                color = raylib.YELLOW
            elif isinstance(entity, Blinky):
                color = raylib.RED
            elif isinstance(entity, Pinky):
                color = raylib.PINK
            elif isinstance(entity, Inky):
                color = raylib.SKYBLUE
            elif isinstance(entity, Clyde):
                color = raylib.ORANGE
            else:
                color = raylib.GRAY

            raylib.draw_rectangle(x, y, self.cell_size, self.cell_size, color)

        raylib.end_drawing()

    def should_close(self) -> bool:
        return raylib.window_should_close()

    def get_frame_time(self) -> float:
        return raylib.get_frame_time()

    def close(self) -> None:
        raylib.unload_texture(self.maze_texture)
        raylib.unload_image(self.maze_image)
        raylib.close_window()

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
