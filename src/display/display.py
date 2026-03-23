from mazegenerator import MazeGenerator
import pyray as rl


class Display:
    def __init__(self):
        self.generator = MazeGenerator()
        self.generator.generate(42)
        self.maze = self.generator.maze
        print(self.maze)
        rl.init_window(1080, 720, "Pac-Man")
        rl.set_target_fps(60)
        self.cell_size = (min(1080 // len(self.maze[0]),
                              720 // len(self.maze)) - 1)
        self.maze_image = rl.gen_image_color(1080, 720, rl.BLACK)
        self.draw_maze()
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.WHITE)
            rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
            rl.end_drawing()

        rl.close_window()

    def draw_maze(self):
        x, y = 0, 0
        for line in range(len(self.maze)):
            for c in self.maze[line]:
                self.put_cell(c, x * self.cell_size, y * self.cell_size)
                x += 1
            x = 0
            y += 1

    def put_cell(self, c: int, cell_x: int, cell_y: int) -> None:
        """Draw cell wall on image

        Args:
        cell_x, cell_y: Cell coordinates
        """
        if (c & 1):
            rl.image_draw_line(self.maze_image, cell_x, cell_y, cell_x +
                               self.cell_size, cell_y, rl.WHITE)
        if ((c >> 1) & 1):
            rl.image_draw_line(self.maze_image, cell_x + self.cell_size, cell_y,
                               cell_x + self.cell_size, cell_y + self.cell_size, rl.WHITE)
        if ((c >> 2) & 1):
            rl.image_draw_line(self.maze_image, cell_x, cell_y + self.cell_size,
                               cell_x + self.cell_size, cell_y + self.cell_size, rl.WHITE)
        if ((c >> 3) & 1):
            rl.image_draw_line(self.maze_image, cell_x, cell_y,
                               cell_x, cell_y + self.cell_size, rl.WHITE)
        if (c == 0xF):
            rl.image_draw_rectangle(self.maze_image, cell_x, cell_y,
                                    self.cell_size, self.cell_size, rl.WHITE)
