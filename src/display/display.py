import pyray as rl
from mazegenerator import MazeGenerator
from src.display.enhanced_cell import EnhancedCell
from src.display.maze_renderer import MazeRenderer
from src.maze import Maze


class Display:
    def __init__(self, maze: Maze):
        self.maze: Maze = maze
        self.brd: list[list[EnhancedCell]] = self._enhanced_maze(maze)
        self.width = 720
        self.height = 720
        rl.init_window(self.width, self.height, "Pac-Man")
        rl.set_target_fps(60)
        self.gap = 18
        cols = len(self.maze.maze[0])
        rows = len(self.maze.maze)
        self.cell_size = min(
            (self.width - (cols - 1) * self.gap) // cols,
            (self.height - (rows - 1) * self.gap) // rows,
        ) - 1
        self.maze_image = rl.gen_image_color(self.width, self.height, rl.BLACK)
        renderer = MazeRenderer(self.maze_image, self.brd,
                                self.cell_size, self.gap)
        renderer.draw()
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.WHITE)
            rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
            rl.end_drawing()

        rl.close_window()

    def _enhanced_maze(self, maze: Maze):
        new: list[list[EnhancedCell]] = []
        for y in range(len(maze.maze)):
            new.append([])
            for x in range(len(maze.maze[y])):
                new[y].append(EnhancedCell(value=maze.maze[y][x], pos=(x, y)))
        return new
