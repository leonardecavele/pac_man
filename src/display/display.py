import pyray as rl
from mazegenerator import MazeGenerator
from pydantic import BaseModel, Field
from src.type import vec2


class EnhancedCell(BaseModel):
    value: int = Field(..., ge=0, le=15)
    pos: vec2 = Field(...)

    @property
    def top(self):
        return (bool(self.value & 1))

    @property
    def right(self):
        return (bool((self.value >> 1) & 1))

    @property
    def bot(self):
        return (bool((self.value >> 2) & 1))

    @property
    def left(self):
        return (bool((self.value >> 3) & 1))


class Display:
    def __init__(self, maze: list[list[int]]):
        self.generator = MazeGenerator()
        self.generator.generate(42)
        self.maze: list[list[EnhancedCell]] = self._enhanced_maze(maze)
        print(self.maze)
        rl.init_window(1080, 720, "Pac-Man")
        rl.set_target_fps(60)
        self.gap = 10
        cols = len(self.maze[0])
        rows = len(self.maze)
        self.cell_size = min(
            (1080 - (cols - 1) * self.gap) // cols,
            (720 - (rows - 1) * self.gap) // rows,
        ) - 1
        self.maze_image = rl.gen_image_color(1080, 720, rl.BLACK)
        self.draw_maze()
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.WHITE)
            rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
            rl.end_drawing()

        rl.close_window()

    def _enhanced_maze(self, maze: list[list[int]]):
        new: list[list[EnhancedCell]] = []
        for y in range(len(maze)):
            new.append([])
            for x in range(len(maze[y])):
                new[y].append(EnhancedCell(value=maze[y][x],
                                           pos=(x, y)))
        return (new)

    def cell(self, x: int, y: int) -> EnhancedCell:
        return (self.maze[y][x])

    def draw_maze(self):
        x, y = 0, 0
        for line in range(len(self.maze)):
            for c in range(len(self.maze[line])):
                self.put_cell(self.cell(c, line), x * (self.cell_size + self.gap),
                              y * (self.cell_size + self.gap))
                x += 1
            x = 0
            y += 1

    def put_cell(self, c: EnhancedCell, cell_x: int, cell_y: int) -> None:
        """Draw cell wall on image

        Args:
        cell_x, cell_y: Cell coordinates
        """
        if (c.top):
            rl.image_draw_line(self.maze_image, cell_x, cell_y, cell_x +
                               self.cell_size, cell_y, rl.WHITE)
        if (c.right):
            rl.image_draw_line(self.maze_image, cell_x + self.cell_size, cell_y,
                               cell_x + self.cell_size, cell_y + self.cell_size, rl.WHITE)
        if (c.bot):
            rl.image_draw_line(self.maze_image, cell_x, cell_y + self.cell_size,
                               cell_x + self.cell_size, cell_y + self.cell_size, rl.WHITE)
        if (c.left):
            rl.image_draw_line(self.maze_image, cell_x, cell_y,
                               cell_x, cell_y + self.cell_size, rl.WHITE)
        # if (c == 0xF):
        #     rl.image_draw_rectangle(self.maze_image, cell_x, cell_y,
        #                             self.cell_size, self.cell_size, rl.WHITE)
