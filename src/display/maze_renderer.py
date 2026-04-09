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
        self._put_arcs(c, x, y, c_top, c_right, c_bot, c_left)

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

    def _draw_tri_arc(self, p1, p2, stem_center_x, stem_center_y, stem_len, vertical):
        T = max(1, self.thickness)

        if vertical:
            rx = int(stem_center_x - T / 2)
            ry = int(stem_center_y - stem_len / 2)

            rl.image_draw_rectangle(
                self.maze_image,
                rx,
                ry,
                T,
                stem_len,
                WALL_COLOR
            )

            a = rl.Vector2(stem_center_x, ry)
            b = rl.Vector2(stem_center_x, ry + stem_len)
        else:
            rx = int(stem_center_x - stem_len / 2)
            ry = int(stem_center_y - T / 2)

            rl.image_draw_rectangle(
                self.maze_image,
                rx,
                ry,
                stem_len,
                T,
                WALL_COLOR
            )

            a = rl.Vector2(rx, stem_center_y)
            b = rl.Vector2(rx + stem_len, stem_center_y)

        rl.image_draw_line_ex(self.maze_image, p1, a, T, WALL_COLOR)
        rl.image_draw_line_ex(self.maze_image, p2, b, T, WALL_COLOR)


    def _put_arcs(self, c, x, y, c_top, c_right, c_bot, c_left):
        G = self.gap
        G2 = G // 2
        CS = self.cell_size

        hemi_stem = max(1, G // 2)
        corner_stem = max(1, G // 3)

        # -------------------------
        # hemicircles
        # -------------------------

        # right connector
        if (c.bot and c_bot and c_right and not c.right
                and not c_right.bot and not c_bot.right):
            self._draw_tri_arc(
                rl.Vector2(x + CS, y + CS),
                rl.Vector2(x + CS, y + CS + G),
                x + CS + G2,
                y + CS + G2,
                hemi_stem,
                True
            )

        # left connector
        if (c.top and c_top and c_left and not c.left
                and not c_left.top and not c_top.left):
            self._draw_tri_arc(
                rl.Vector2(x, y - G),
                rl.Vector2(x, y),
                x - G2,
                y - G2,
                hemi_stem,
                True
            )

        # bottom connector
        if (c.left and c_left and c_bot and not c.bot
                and not c_bot.left and not c_left.bot):
            self._draw_tri_arc(
                rl.Vector2(x - G, y + CS),
                rl.Vector2(x, y + CS),
                x - G2,
                y + CS + G2,
                hemi_stem,
                False
            )

        # top connector
        if (c.right and c_right and c_top and not c.top
                and not c_top.right and not c_right.top):
            self._draw_tri_arc(
                rl.Vector2(x + CS, y),
                rl.Vector2(x + CS + G, y),
                x + CS + G2,
                y - G2,
                hemi_stem,
                False
            )

        # -------------------------
        # corners
        # -------------------------

        # bottom-right corner
        if (c_right and c_bot and c_right.left and not c_right.bot
                and c_bot.top and not c_bot.right):
            self._draw_tri_arc(
                rl.Vector2(x + CS + G, y + CS),
                rl.Vector2(x + CS, y + CS + G),
                x + CS + G2,
                y + CS + G2,
                corner_stem,
                True
            )

        # top-left corner
        if (c_top and c_left and c_top.bot and not c_top.left
                and c_left.right and not c_left.top):
            self._draw_tri_arc(
                rl.Vector2(x, y - G),
                rl.Vector2(x - G, y),
                x - G2,
                y - G2,
                corner_stem,
                True
            )

        # bottom-left corner
        if (c_left and c_bot and c_left.right and not c_left.bot
                and c_bot.top and not c_bot.left):
            self._draw_tri_arc(
                rl.Vector2(x - G, y + CS),
                rl.Vector2(x, y + CS + G),
                x - G2,
                y + CS + G2,
                corner_stem,
                False
            )

        # top-right corner
        if (c_top and c_right and c_top.bot and not c_top.right
                and c_right.left and not c_right.top):
            self._draw_tri_arc(
                rl.Vector2(x + CS, y - G),
                rl.Vector2(x + CS + G, y),
                x + CS + G2,
                y - G2,
                corner_stem,
                False
            )
