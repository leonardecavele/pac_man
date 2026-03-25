import pyray as rl
from src.display.maze_renderer import MazeRenderer
from src.maze import Maze


class Display:
    def __init__(self, maze: Maze):
        self.maze: Maze = maze
        self.width = 720
        self.height = 720
        self._compute_cell_gap_size()
        rl.init_window(self.width, self.height, "Pac-Man")
        rl.set_target_fps(60)
        self.maze_image = rl.gen_image_color(self.width, self.height, rl.BLACK)
        renderer = MazeRenderer(
            self.maze_image, self.maze, self.cell_size, self.gap
        )
        renderer.draw()
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.WHITE)
            rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
            rl.end_drawing()

        rl.close_window()

    def _compute_cell_gap_size(self):
        self.gap = 18
        while (self.gap >= 0):
            self.cell_size = min(
                (self.width - (self.maze.width + 1) * self.gap)
                // self.maze.width,
                (self.height - (self.maze.height + 1) * self.gap)
                // self.maze.height,
            ) - 1
            if (self.gap >= self.cell_size):
                self.gap -= 2
                continue
            break
