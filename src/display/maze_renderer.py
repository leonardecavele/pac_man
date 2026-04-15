import pyray as rl
from src.maze import Maze

WALL_COLOR = rl.Color(25, 25, 166, 255)
WALL_COLOR_GHOST_HOUSE = rl.BEIGE


class MazeRenderer:
    """Render the maze walls onto a raylib Image using cell, gap, and arc
    drawing primitives."""

    def __init__(self, maze_image: rl.Image, maze: Maze,
                 cell_size: int, gap: int) -> None:
        """
        Initialize the renderer and immediately draw the maze onto maze_image.

        maze_image -- destination image to draw into
        maze       -- maze data source
        cell_size  -- pixel size of each cell
        gap        -- pixel width of the corridors between cells
        """
        self.maze_image = maze_image
        self.maze = maze
        self.cell_size = cell_size
        self.gap = gap
        self.thickness = self.gap // 4
        self.draw()

    def draw(self) -> None:
        """Draw the full maze (borders, cells, and open-area joints)
        onto maze_image."""
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

        self._put_open_area_joints()

    def _put_borders(self) -> None:
        """Draw the four outer border rectangles around the entire maze."""
        total_width = (self.cell_size + self.gap) * self.maze.width + self.gap
        total_height = (self.cell_size + self.gap) * self.maze.height \
            + self.gap

        rl.image_draw_rectangle(
            self.maze_image, 0, 0,
            total_width, self.thickness, WALL_COLOR
        )

        rl.image_draw_rectangle(
            self.maze_image, 0, total_height - self.thickness,
            total_width, self.thickness, WALL_COLOR
        )

        rl.image_draw_rectangle(
            self.maze_image, 0, 0,
            self.thickness, total_height, WALL_COLOR
        )

        rl.image_draw_rectangle(
            self.maze_image, total_width - self.thickness, 0,
            self.thickness, total_height, WALL_COLOR
        )

    def _get_neighbors(self,
                       c: Maze.Cell) -> tuple[Maze.Cell | None,
                                              Maze.Cell | None,
                                              Maze.Cell | None,
                                              Maze.Cell | None]:
        """Return the (top, right, bot, left) neighbour cells of c, or None
        at the maze boundary."""
        x, y = c.pos
        c_top = self.maze.maze[y - 1][x] if y > 0 else None
        c_bot = self.maze.maze[y +
                               1][x] if y < len(self.maze.maze) - 1 else None
        c_left = self.maze.maze[y][x - 1] if x > 0 else None
        c_right = self.maze.maze[y][x +
                                    1] if x < len(self.maze.maze[0]) \
            - 1 else None
        return (c_top, c_right, c_bot, c_left)

    def _put_cell(self, c: Maze.Cell, x: int, y: int) -> None:
        """Draw the walls and connecting links for cell c at pixel position
        (x, y)."""
        self._put_links(c, x, y)
        c_top, c_right, c_bot, c_left = self._get_neighbors(c)

        if c.top and c.bot and c.left and c.right:
            rl.image_draw_rectangle(
                self.maze_image, x, y, self.cell_size + 1,
                self.cell_size + 1, rl.BLACK
            )
            return

        offset = ((self.gap - self.thickness) // 2) + self.thickness // 2

        if c.top:
            draw_y = y - self.thickness
            if self._both_ghost_house(c, c_top):
                color = WALL_COLOR_GHOST_HOUSE
                draw_y -= offset
            else:
                color = WALL_COLOR

            rl.image_draw_rectangle(
                self.maze_image, x, draw_y,
                self.cell_size, self.thickness, color
            )

        if c.right:
            draw_x = x + self.cell_size
            if self._both_ghost_house(c, c_right):
                color = WALL_COLOR_GHOST_HOUSE
            else:
                color = WALL_COLOR

            rl.image_draw_rectangle(
                self.maze_image, draw_x, y,
                self.thickness, self.cell_size, color
            )

        if c.bot:
            draw_y = y + self.cell_size
            if self._both_ghost_house(c, c_bot):
                color = WALL_COLOR_GHOST_HOUSE
                draw_y += offset

                rl.image_draw_rectangle(
                    self.maze_image,
                    x + self.cell_size, y + self.cell_size,
                    self.thickness, self.gap, WALL_COLOR
                )
                rl.image_draw_rectangle(
                    self.maze_image,
                    x - self.thickness, y + self.cell_size,
                    self.thickness, self.gap, WALL_COLOR
                )
            else:
                color = WALL_COLOR

            rl.image_draw_rectangle(
                self.maze_image, x, draw_y,
                self.cell_size, self.thickness, color
            )

        if c.left:
            draw_x = x - self.thickness
            if self._both_ghost_house(c, c_left):
                color = WALL_COLOR_GHOST_HOUSE
            else:
                color = WALL_COLOR

            rl.image_draw_rectangle(
                self.maze_image, draw_x, y,
                self.thickness, self.cell_size, color
            )

    def _put_links(self, c: Maze.Cell, x: int, y: int) -> None:
        """Draw gap-filling lines and curved arcs that connect adjacent wall
        segments."""
        c_top, c_right, c_bot, c_left = self._get_neighbors(c)
        self._put_gap_lines(c, x, y, c_top, c_right, c_bot, c_left)
        self._put_arcs(c, x, y, c_top, c_right, c_bot, c_left)

    def _put_gap_lines(
        self, c: Maze.Cell, x: int, y: int,
        c_top: Maze.Cell | None, c_right: Maze.Cell | None,
        c_bot: Maze.Cell | None, c_left: Maze.Cell | None
    ) -> None:
        """Draw small gap-bridging rectangles at shared wall corners between
        adjacent cells."""
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

    def _put_arcs(
        self, c: Maze.Cell, x: int, y: int,
        c_top: Maze.Cell | None, c_right: Maze.Cell | None,
        c_bot: Maze.Cell | None, c_left: Maze.Cell | None
    ) -> None:
        """Draw rounded arc decorations at concave wall junctions for a
        smooth look."""
        G = self.gap
        G2 = G // 2
        CS = self.cell_size
        T = max(1, self.thickness)

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

        if (c.top and c_top and c_left and not c.left
                and not c_left.top and not c_top.left):
            self._draw_thick_circle_lines(
                x, y - G2, G2 - 1, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + T - 2, y - G + T,
                G2, G - T,
                rl.BLACK
            )

        if (c.left and c_left and c_bot and not c.bot
                and not c_bot.left and not c_left.bot):
            self._draw_thick_circle_lines(
                x - G2, y + CS, G2 - 1, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x - G + T, y + CS - G2 + 1,
                G - T, G2,
                rl.BLACK
            )

        if (c.right and c_right and c_top and not c.top
                and not c_top.right and not c_right.top):
            self._draw_thick_circle_lines(
                x + CS + G2, y, G2 - 1, T, WALL_COLOR
            )
            rl.image_draw_rectangle(
                self.maze_image,
                x + CS + T, y - 1,
                G - T, G2 + T,
                rl.BLACK
            )

        self._put_corners(c, x, y, c_top, c_right, c_bot, c_left)

    def _put_corners(
        self, c: Maze.Cell, x: int, y: int,
        c_top: Maze.Cell | None, c_right: Maze.Cell | None,
        c_bot: Maze.Cell | None, c_left: Maze.Cell | None
    ) -> None:
        """Draw convex corner arcs where two perpendicular wall segments
        meet."""
        G = self.gap
        CS = self.cell_size - 1
        T = max(1, self.thickness)
        EXTRA = T

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
        """Draw concentric circle outlines to simulate a thick circular arc."""
        for i in range(thickness):
            rl.image_draw_circle_lines(
                self.maze_image,
                center_x,
                center_y,
                max(0, radius - i),
                color
            )

    def _both_ghost_house(self, a: Maze.Cell, b: Maze.Cell | None) -> bool:
        """Return True if both cells carry the GHOST_HOUSE wall flag."""
        if b is None:
            return False
        return (
            bool(a.value & Maze.Cell.Walls.GHOST_HOUSE)
            and bool(b.value & Maze.Cell.Walls.GHOST_HOUSE)
        )

    def _is_open_2x2(self, gx: int, gy: int) -> bool:
        """Return True if the 2×2 block of cells starting at (gx, gy) is
        completely open."""
        if gx + 1 >= self.maze.width or gy + 1 >= self.maze.height:
            return False

        a = self.maze.maze[gy][gx]
        b = self.maze.maze[gy][gx + 1]
        c = self.maze.maze[gy + 1][gx]
        d = self.maze.maze[gy + 1][gx + 1]

        return (
            not a.right
            and not a.bot
            and not b.left
            and not b.bot
            and not c.top
            and not c.right
            and not d.top
            and not d.left
        )

    def _draw_center_joint(self, gx: int, gy: int) -> None:
        """Draw a decorative circular joint at the centre of the open 2×2
        block at (gx, gy)."""
        step = self.cell_size + self.gap

        center_x = (gx + 1) * step + self.gap // 2
        center_y = (gy + 1) * step + self.gap // 2

        radius = max(2, self.gap // 2)
        thickness = max(1, self.thickness)

        rl.image_draw_circle(
            self.maze_image,
            center_x,
            center_y,
            max(1, radius - thickness),
            rl.BLACK
        )

        self._draw_thick_circle_lines(
            center_x,
            center_y,
            radius,
            thickness,
            WALL_COLOR
        )

    def _put_open_area_joints(self) -> None:
        """Draw center joints at all fully-open 2×2 cell blocks in the maze."""
        for gy in range(self.maze.height - 1):
            for gx in range(self.maze.width - 1):
                if self._is_open_2x2(gx, gy):
                    self._draw_center_joint(gx, gy)
