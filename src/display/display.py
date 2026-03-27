import pyray as raylib

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

        raylib.init_window(self.width, self.height, self.title)
        raylib.set_target_fps(self.fps)

        self.maze_image = raylib.gen_image_color(
            self.width, self.height, raylib.BLACK
        )

        renderer = MazeRenderer(
            self.maze_image, self.maze, self.cell_size, self.gap
        )
        renderer.draw()
        self.maze_texture = rl.load_texture_from_image(self.maze_image)
        self.textures = Textures(self.cell_size)._load_textures()
        self._gen_pacgums()

        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.WHITE)
            rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
            self._draw_pacgums()
            # self._DEBUG_grid()
            rl.end_drawing()

        self.maze_texture = raylib.load_texture_from_image(self.maze_image)

    def draw(self, entities: list[Entity]) -> None:
        raylib.begin_drawing()
        raylib.clear_background(raylib.WHITE)
        raylib.draw_texture(self.maze_texture, 0, 0, raylib.WHITE)

        for entity in entities:

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

            entity_size: int = max(4, self.cell_size - 8)
            draw_x: int = int(entity.screen_pos[0] - entity_size / 2)
            draw_y: int = int(entity.screen_pos[1] - entity_size / 2)

            raylib.draw_rectangle(
                draw_x, draw_y, entity_size, entity_size, color
            )

        raylib.end_drawing()

    def should_close(self) -> bool:
        return raylib.window_should_close()

    def get_frame_time(self) -> float:
        return raylib.get_frame_time()

    def close(self) -> None:
        raylib.unload_texture(self.maze_texture)
        raylib.unload_image(self.maze_image)
        raylib.close_window()

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

    def _draw_pacgums(self):
        for i in self.pacgums:
            x, y = i.screen_pos
            x = x - self.cell_size // 2
            y = y - self.cell_size // 2
            rl.draw_texture(i.sprite, x, y, rl.WHITE)

    def _maze_to_screen_pos(self, maze_pos: vec2) -> vec2:
        screen_pos: vec2 = (
            maze_pos[0] * (self.cell_size + self.gap) +
            self.gap + self.cell_size // 2 + 1,
            maze_pos[1] * (self.cell_size + self.gap) +
            self.gap + self.cell_size // 2 + 1
        )
        return (screen_pos)

    def _gen_pacgums(self) -> None:
        self.pacgums: list[Collectible] = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if (self.maze.maze[y][x].value == 15):
                    continue
                if ((x == 0 and y == 0) or
                    (x == 0 and y == self.maze.height - 1) or
                    (x == self.maze.width - 1 and y == 0) or
                    (x == self.maze.width - 1
                     and y == self.maze.height - 1)):
                    self.pacgums.append(SuperPacgum(
                        self._maze_to_screen_pos((x, y)), (x, y),
                        self.textures["super_pacgum"], self.maze)
                    )
                else:
                    self.pacgums.append(
                        Pacgum(self._maze_to_screen_pos((x, y)), (x, y),
                               self.textures["pacgum"], self.maze)
                    )
