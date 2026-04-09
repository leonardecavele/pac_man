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
        self.draw()

    def draw(self):
        border = rl.Rectangle(
            0, 0, (self.cell_size + self.gap) * self.maze.width + self.gap,
            (self.cell_size + self.gap) * self.maze.height + self.gap)
        #rl.image_draw_rectangle_lines(self.maze_image, border, 1, WALL_COLOR)
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
                self.cell_size + 1, rl.GRAY
            )
            return

        if c.top:
            rl.image_draw_rectangle(
                self.maze_image, x, y - self.gap // 4,
                self.cell_size, self.gap // 4, rl.BEIGE
            )
        if c.right:
            rl.image_draw_rectangle(
                self.maze_image, x + self.cell_size, y,
                self.gap // 4, self.cell_size, rl.GREEN
            )
        if c.bot:
            rl.image_draw_rectangle(
                self.maze_image, x, y + self.cell_size,
                self.cell_size, self.gap // 4, rl.PINK
            )
        if c.left:
            rl.image_draw_rectangle(
                self.maze_image, x - self.gap // 4, y,
                self.gap // 4, self.cell_size, rl.ORANGE
            )

    def _put_links(self, c: Maze.Cell, x: int, y: int) -> None:
        c_top, c_right, c_bot, c_left = self._get_neighbors(c)
        self._put_gap_lines(c, x, y, c_top, c_right, c_bot, c_left)
        self._put_corners(c, x, y, c_top, c_right, c_bot, c_left)
        self._put_hemicircles(c, x, y, c_top, c_right, c_bot, c_left)

    def _put_gap_lines(self, c, x, y, c_top, c_right, c_bot, c_left):
        G = self.gap
        CS = self.cell_size
        T = max(1, G // 4)

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
        T = max(1, G // 4)

        # right connector
        if (c.bot and c_bot and c_right and not c.right
                and not c_right.bot and not c_bot.right):
            # barre verticale au milieu du carré du gap
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS + G2 - T // 2,
                y + CS,
                T,
                G,
                WALL_COLOR
            )

            # diagonale haut -> barre
            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x + CS, y + CS),
                rl.Vector2(x + CS + G2, y + CS + G2),
                T,
                WALL_COLOR
            )

            # diagonale bas -> barre
            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x + CS, y + CS + G),
                rl.Vector2(x + CS + G2, y + CS + G2),
                T,
                WALL_COLOR
            )

        # left connector
        if (c.top and c_top and c_left and not c.left
                and not c_left.top and not c_top.left):
            rl.image_draw_rectangle(
                self.maze_image,
                x - G2 - T // 2,
                y - G,
                T,
                G,
                WALL_COLOR
            )

            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x, y - G),
                rl.Vector2(x - G2, y - G2),
                T,
                WALL_COLOR
            )

            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x, y),
                rl.Vector2(x - G2, y - G2),
                T,
                WALL_COLOR
            )

        # bottom connector
        if (c.left and c_left and c_bot and not c.bot
                and not c_bot.left and not c_left.bot):
            rl.image_draw_rectangle(
                self.maze_image,
                x - G,
                y + CS + G2 - T // 2,
                G,
                T,
                WALL_COLOR
            )

            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x - G, y + CS),
                rl.Vector2(x - G2, y + CS + G2),
                T,
                WALL_COLOR
            )

            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x, y + CS),
                rl.Vector2(x - G2, y + CS + G2),
                T,
                WALL_COLOR
            )

        # top connector
        if (c.right and c_right and c_top and not c.top
                and not c_top.right and not c_right.top):
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS,
                y - G2 - T // 2,
                G,
                T,
                WALL_COLOR
            )

            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x + CS, y),
                rl.Vector2(x + CS + G2, y - G2),
                T,
                WALL_COLOR
            )

            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x + CS + G, y),
                rl.Vector2(x + CS + G2, y - G2),
                T,
                WALL_COLOR
            )

    def _put_corners(self, c, x, y, c_top, c_right, c_bot, c_left):
        G = self.gap
        CS = self.cell_size
        T = max(1, G // 4)

        # bottom-right corner
        if (c_right and c_bot and c_right.left and not c_right.bot
                and c_bot.top and not c_bot.right):
            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x + CS + G, y + CS + T / 2),
                rl.Vector2(x + CS + T / 2, y + CS + G),
                T,
                WALL_COLOR
            )

        # top-left corner
        if (c_top and c_left and c_top.bot and not c_top.left
                and c_left.right and not c_left.top):
            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x - G, y - T / 2),
                rl.Vector2(x - T / 2, y - G),
                T,
                WALL_COLOR
            )

        # bottom-left corner
        if (c_left and c_bot and c_left.right and not c_left.bot
                and c_bot.top and not c_bot.left):
            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x - G, y + CS + T / 2),
                rl.Vector2(x - T / 2, y + CS + G),
                T,
                WALL_COLOR
            )

        # top-right corner
        if (c_top and c_right and c_top.bot and not c_top.right
                and c_right.left and not c_right.top):
            rl.image_draw_line_ex(
                self.maze_image,
                rl.Vector2(x + CS + T / 2, y - G),
                rl.Vector2(x + CS + G, y - T / 2),
                T,
                WALL_COLOR
            )
