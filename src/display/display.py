import pyray as rl
from mazegenerator import MazeGenerator
from pydantic import BaseModel, Field
from src.type import vec2

WALL_COLOR = rl.Color(25, 25, 166, 255)


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
        self.generator.generate()
        self.maze: list[list[EnhancedCell]] = self._enhanced_maze(maze)
        self.width = 720
        self.height = 720
        rl.init_window(self.width, self.height, "Pac-Man")
        rl.set_target_fps(60)
        self.gap = 18
        cols = len(self.maze[0])
        rows = len(self.maze)
        self.cell_size = min(
            (self.width - (cols - 1) * self.gap) // cols,
            (self.height - (rows - 1) * self.gap) // rows,
        ) - 1
        self.maze_image = rl.gen_image_color(self.width, self.height, rl.BLACK)
        # self._DEBUG_show_grid()
        self.draw_maze()
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.WHITE)
            rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
            rl.end_drawing()

        rl.close_window()

    def _DEBUG_show_grid(self):
        for i in range(self.width // (self.cell_size + self.gap)):
            x = i * (self.cell_size + self.gap) - self.gap // 2
            rl.image_draw_line(self.maze_image, x, 0, x, self.height, rl.RED)
        for i in range(self.height // (self.cell_size + self.gap)):
            y = i * (self.cell_size + self.gap) - self.gap // 2
            rl.image_draw_line(self.maze_image, 0, y, self.width, y, rl.RED)

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

    def get_neighboors(self, c: EnhancedCell):
        x, y = c.pos
        if (y > 0):
            c_top = self.cell(x, y - 1)
        else:
            c_top = None
        if (y < len(self.maze) - 1):
            c_bot = self.cell(x, y + 1)
        else:
            c_bot = None
        if (x > 0):
            c_left = self.cell(x - 1, y)
        else:
            c_left = None
        if (x < len(self.maze[0]) - 1):
            c_right = self.cell(x + 1, y)
        else:
            c_right = None
        return (c_top, c_right, c_bot, c_left)

    def put_links(self, c: EnhancedCell, x: int, y: int) -> None:
        c_top, c_right, c_bot, c_left = self.get_neighboors(c)
        if (c.bot):
            if (c_right and not c.right and c_right.bot):
                rl.image_draw_line(self.maze_image, x + self.cell_size,
                                   y + self.cell_size,
                                   x + self.cell_size + self.gap,
                                   y + self.cell_size, WALL_COLOR)
            # right hemicircle
            if (c_bot and c_right and not c.right and not c_right.bot
                    and not c_bot.right):
                rl.image_draw_circle_lines(self.maze_image,
                                           x + self.cell_size,
                                           y + self.cell_size + self.gap // 2,
                                           self.gap // 2, WALL_COLOR
                                           )
                rl.image_draw_rectangle(self.maze_image,
                                        x + self.cell_size - self.gap,
                                        y + self.cell_size + 1,
                                        self.gap,
                                        self.gap - 1, rl.BLACK)
        if (c.top):
            if (c_right and not c.right and c_right.top):
                rl.image_draw_line(self.maze_image, x + self.cell_size,
                                   y,
                                   x + self.cell_size + self.gap,
                                   y, WALL_COLOR)
            # left hemicircle
            if (c_top and c_left and not c.left and not c_left.top and not c_top.left):
                rl.image_draw_circle_lines(self.maze_image,
                                           x, y - self.gap // 2,
                                           self.gap // 2, WALL_COLOR
                                           )
                rl.image_draw_rectangle(self.maze_image,
                                        x,
                                        y - self.gap + 1,
                                        self.gap,
                                        self.gap - 1, rl.BLACK)
        if (c.left):
            if (c_bot and not c.bot and c_bot.left):
                rl.image_draw_line(self.maze_image, x,
                                   y + self.cell_size,
                                   x,
                                   y + self.cell_size + self.gap, WALL_COLOR)
            # bot hemicircle
            if (c_left and c_bot and not c.bot and not c_bot.left
                    and not c_left.bot):
                rl.image_draw_circle_lines(self.maze_image,
                                           x - self.gap // 2,
                                           y + self.cell_size,
                                           self.gap // 2,
                                           WALL_COLOR)
                rl.image_draw_rectangle(self.maze_image, x - self.gap + 1,
                                        y + self.cell_size - self.gap,
                                        self.gap - 1,
                                        self.gap, rl.BLACK)
        if (c.right):
            if (c_bot and not c.bot and c_bot.right):
                rl.image_draw_line(self.maze_image, x + self.cell_size,
                                   y + self.cell_size,
                                   x + self.cell_size,
                                   y + self.cell_size + self.gap, WALL_COLOR)
            # top hemicircle
            if (c_right and c_top and not c.top and not c_top.right
                    and not c_right.top):
                rl.image_draw_circle_lines(self.maze_image,
                                           x + self.cell_size
                                           + (self.gap // 2), y,
                                           self.gap // 2,
                                           WALL_COLOR)
                rl.image_draw_rectangle(self.maze_image, x + self.cell_size + 1,
                                        y,
                                        self.gap,
                                        self.gap, rl.BLACK)

        # bottom_right corner
        if (c_right and c_bot and c_right.left and not c_right.bot
                and c_bot.top and not c_bot.right):
            rl.image_draw_circle_lines(self.maze_image,
                                       x + self.cell_size,
                                       y + self.cell_size,
                                       self.gap, WALL_COLOR)
            rl.image_draw_rectangle(self.maze_image,
                                    x + self.cell_size + 1,
                                    y,
                                    self.gap - 1,
                                    self.cell_size,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x,
                                    y + self.cell_size + 1,
                                    self.cell_size,
                                    self.gap - 1,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x + self.cell_size - self.gap,
                                    y + self.cell_size - self.gap,
                                    self.gap,
                                    self.gap,
                                    rl.BLACK)
        # top_left corner
        if (c_top and c_left and c_top.bot and not c_top.left
                and c_left.right and not c_left.top):
            rl.image_draw_circle_lines(self.maze_image,
                                       x,
                                       y,
                                       self.gap, WALL_COLOR)
            rl.image_draw_rectangle(self.maze_image,
                                    x,
                                    y - self.gap + 1,
                                    self.cell_size,
                                    self.gap - 1,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x - self.gap + 1,
                                    y,
                                    self.gap - 1,
                                    self.cell_size,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x + 1,
                                    y + 1,
                                    self.gap,
                                    self.gap,
                                    rl.BLACK)

        # bottom_left corner
        if (c_left and c_bot and c_left.right and not c_left.bot
                and c_bot.top and not c_bot.left):
            rl.image_draw_circle_lines(self.maze_image,
                                       x,
                                       y + self.cell_size,
                                       self.gap, WALL_COLOR)
            rl.image_draw_rectangle(self.maze_image,
                                    x,
                                    y + self.cell_size + 1,
                                    self.cell_size,
                                    self.gap - 1,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x - self.gap + 1,
                                    y,
                                    self.gap - 1,
                                    self.cell_size,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x + 1,
                                    y + self.cell_size - self.gap,
                                    self.gap,
                                    self.gap,
                                    rl.BLACK)

        # bottom_right corner
        if (c_top and c_right and c_top.bot and not c_top.right
                and c_right.left and not c_right.top):
            rl.image_draw_circle_lines(self.maze_image,
                                       x + self.cell_size,
                                       y,
                                       self.gap, WALL_COLOR)
            rl.image_draw_rectangle(self.maze_image,
                                    x,
                                    y - self.gap + 1,
                                    self.cell_size,
                                    self.gap - 1,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x + self.cell_size + 1,
                                    y,
                                    self.gap - 1,
                                    self.cell_size,
                                    rl.BLACK)
            rl.image_draw_rectangle(self.maze_image,
                                    x + self.cell_size - self.gap,
                                    y + 1,
                                    self.gap,
                                    self.gap,
                                    rl.BLACK)

    def put_cell(self, c: EnhancedCell, cell_x: int, cell_y: int) -> None:
        """Draw cell wall on image

        Args:
        cell_x, cell_y: Cell coordinates
        """
        self.put_links(c, cell_x, cell_y)
        if (c.top and c.bot and c.left and c.right):
            rl.image_draw_rectangle(self.maze_image, cell_x, cell_y,
                                    self.cell_size + 1, self.cell_size + 1,
                                    rl.BLACK)
            return
        if (c.top):
            rl.image_draw_line(self.maze_image, cell_x, cell_y, cell_x +
                               self.cell_size, cell_y, WALL_COLOR)
        if (c.right):
            rl.image_draw_line(self.maze_image, cell_x + self.cell_size, cell_y,
                               cell_x + self.cell_size, cell_y + self.cell_size, WALL_COLOR)
        if (c.bot):
            rl.image_draw_line(self.maze_image, cell_x, cell_y + self.cell_size,
                               cell_x + self.cell_size, cell_y + self.cell_size, WALL_COLOR)
        if (c.left):
            rl.image_draw_line(self.maze_image, cell_x, cell_y,
                               cell_x, cell_y + self.cell_size, WALL_COLOR)
