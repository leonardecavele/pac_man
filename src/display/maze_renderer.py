import pyray as rl
from src.maze import Maze

WALL_COLOR = rl.Color(25, 25, 166, 255)


class MazeRenderer:
    def __init__(self, maze_image, maze: Maze,
                 cell_size: int, gap: int):
        self.maze_image = maze_image
        self.maze = maze
        self.cell_size = cell_size
        self.gap = gap
        self.thickness = self.gap // 4
        self.draw()

    def draw(self):
        self._put_borders()

        x, y = 0, 0
        for line in range(self.maze.height):
            for c in range(self.maze.width):
                self._put_cell(
                    self.maze.maze[line][c],
                    x * (self.cell_size + self.gap) + self.gap,
                    y * (self.cell_size + self.gap) + self.gap
                )
                x += 1
            x = 0
            y += 1

    def _put_borders(self):
        total_width = (self.cell_size + self.gap) * self.maze.width + self.gap
        total_height = (self.cell_size + self.gap) * self.maze.height + self.gap

        # top
        rl.image_draw_rectangle(
            self.maze_image, 0, 0,
            total_width, self.thickness, WALL_COLOR
        )

        # bottom
        rl.image_draw_rectangle(
            self.maze_image, 0, total_height - self.thickness,
            total_width, self.thickness, WALL_COLOR
        )

        # left
        rl.image_draw_rectangle(
            self.maze_image, 0, 0,
            self.thickness, total_height, WALL_COLOR
        )

        # right
        rl.image_draw_rectangle(
            self.maze_image, total_width - self.thickness, 0,
            self.thickness, total_height, WALL_COLOR
        )

    def _get_neighbors(self, c: Maze.Cell):
        x, y = c.pos
        c_top = self.maze.maze[y - 1][x] if y > 0 else None
        c_bot = self.maze.maze[y +
                               1][x] if y < len(self.maze.maze) - 1 else None
        c_left = self.maze.maze[y][x - 1] if x > 0 else None
        c_right = self.maze.maze[y][x +
                                    1] if x < len(self.maze.maze[0]) - 1 else None
        return c_top, c_right, c_bot, c_left

    def _put_cell(self, c: Maze.Cell, x: int, y: int) -> None:
        self._put_links(c, x, y)

        if c.top and c.bot and c.left and c.right:
            rl.image_draw_rectangle(
                self.maze_image, x, y, self.cell_size + 1,
                self.cell_size + 1, rl.BLACK
            )
            return

        if c.top:
            rl.image_draw_rectangle(
                self.maze_image, x, y - self.thickness,
                self.cell_size, self.thickness, WALL_COLOR
            )
        if c.right:
            rl.image_draw_rectangle(
                self.maze_image, x + self.cell_size, y,
                self.thickness, self.cell_size, WALL_COLOR
            )
        if c.bot:
            rl.image_draw_rectangle(
                self.maze_image, x, y + self.cell_size,
                self.cell_size, self.thickness, WALL_COLOR
            )
        if c.left:
            rl.image_draw_rectangle(
                self.maze_image, x - self.thickness, y,
                self.thickness, self.cell_size, WALL_COLOR
            )

    def _put_links(self, c: Maze.Cell, x: int, y: int) -> None:
        c_top, c_right, c_bot, c_left = self._get_neighbors(c)
        self._put_gap_lines(c, x, y, c_top, c_right, c_bot, c_left)
        self._put_hemicircles(c, x, y, c_top, c_right, c_bot, c_left)
        self._put_corners(c, x, y, c_top, c_right, c_bot, c_left)

    def _put_gap_lines(self, c, x, y, c_top, c_right, c_bot, c_left):
        G = self.gap
        CS = self.cell_size
        T = max(1, self.thickness)

        if c.bot and c_right and not c.right and c_right.bot:
            rl.image_draw_rectangle(
                self.maze_image, x + CS, y + CS,
                G, T, WALL_COLOR
            )

        if c.top and c_right and not c.right and c_right.top:
            rl.image_draw_rectangle(
                self.maze_image, x + CS, y - T,
                G, T, WALL_COLOR
            )

        if c.left and c_bot and not c.bot and c_bot.left:
            rl.image_draw_rectangle(
                self.maze_image, x - T, y + CS,
                T, G, WALL_COLOR
            )

        if c.right and c_bot and not c.bot and c_bot.right:
            rl.image_draw_rectangle(
                self.maze_image, x + CS, y + CS,
                T, G, WALL_COLOR
            )

    def _put_hemicircles(self, c, x, y, c_top, c_right, c_bot, c_left):
        G = self.gap
        G2 = G // 2
        CS = self.cell_size
        T = max(1, self.thickness)

        # right hemicircle
        if (c.bot and c_bot and c_right and not c.right
                and not c_right.bot and not c_bot.right):
            self._draw_thick_circle_lines(
                x + CS, y + CS + G2, G2 - 1, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS - G2, y + CS + T,
                G2, G - T,
                rl.BLACK
            )

        # left hemicircle
        if (c.top and c_top and c_left and not c.left
                and not c_left.top and not c_top.left):
            self._draw_thick_circle_lines(
                x, y - G2, G2 - 1, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + T, y - G + T,
                G2, G - T,
                rl.BLACK
            )

        # bot hemicircle
        if (c.left and c_left and c_bot and not c.bot
                and not c_bot.left and not c_left.bot):
            self._draw_thick_circle_lines(
                x - G2, y + CS, G2 - 1, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x - G + T, y + CS - G2,
                G - T, G2,
                rl.BLACK
            )

        # top hemicircle
        if (c.right and c_right and c_top and not c.top
                and not c_top.right and not c_right.top):
            self._draw_thick_circle_lines(
                x + CS + G2, y, G2 - 1, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS + T, y,
                G - T, G2 + T,
                rl.BLACK
            )

    def _put_corners(self, c, x, y, c_top, c_right, c_bot, c_left):
        G = self.gap
        CS = self.cell_size - 1
        T = max(1, self.thickness)
        EXTRA = T

        # bottom-right corner
        if (c_right and c_bot and c_right.left and not c_right.bot
                and c_bot.top and not c_bot.right):
            self._draw_thick_circle_lines(
                x + CS, y + CS, G, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS + T - EXTRA, y,
                G - T + EXTRA, CS, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x, y + CS + T - EXTRA,
                CS, G - T + EXTRA, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS - G + T - EXTRA, y + CS - G + T - EXTRA,
                G + EXTRA, G + EXTRA, rl.BLACK
            )

        # top-left corner
        if (c_top and c_left and c_top.bot and not c_top.left
                and c_left.right and not c_left.top):
            self._draw_thick_circle_lines(
                x, y, G, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x, y - G + T,
                CS, G - T + EXTRA, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x - G + T, y,
                G - T + EXTRA, CS, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + T, y + T,
                G + EXTRA, G + EXTRA, rl.BLACK
            )

        # bottom-left corner
        if (c_left and c_bot and c_left.right and not c_left.bot
                and c_bot.top and not c_bot.left):
            self._draw_thick_circle_lines(
                x, y + CS, G, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x, y + CS + T - EXTRA,
                CS, G - T + EXTRA, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x - G + T, y,
                G - T + EXTRA, CS, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + T, y + CS - G + T - EXTRA,
                G + EXTRA, G + EXTRA, rl.BLACK
            )

        # top-right corner
        if (c_top and c_right and c_top.bot and not c_top.right
                and c_right.left and not c_right.top):
            self._draw_thick_circle_lines(
                x + CS, y, G, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x, y - G + T,
                CS, G - T + EXTRA, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS + T - EXTRA, y,
                G - T + EXTRA, CS, rl.BLACK
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS - G + T - EXTRA, y + T,
                G + EXTRA, G + EXTRA, rl.BLACK
            )

    def _draw_thick_circle_lines(
        self, center_x: int, center_y: int,
        radius: int, thickness: int, color: rl.Color
    ) -> None:
        for i in range(thickness):
            rl.image_draw_circle_lines(
                self.maze_image,
                center_x,
                center_y,
                max(0, radius - i),
                color
            )
