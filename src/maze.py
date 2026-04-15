from enum import IntFlag
from abc import ABC

from pydantic import BaseModel, Field
from mazegenerator import MazeGenerator

from src.type import vec2i, brd, Direction


class Maze(ABC):
    """Abstract base class for a grid-based maze used in gameplay."""

    def __init__(self, height: int, width: int, maze: brd, og: bool) -> None:
        """
        Initialize the maze.

        height -- number of rows in the grid
        width  -- number of columns in the grid
        maze   -- 2-D list of Cell objects
        og     -- True for the classic layout, False for a generated maze
        """
        self.height: int = height
        self.width: int = width
        self.maze: brd = maze
        self.og: bool = og

    class Cell(BaseModel):
        """A single maze cell described by its wall bitmask and grid position."""

        class Walls(IntFlag):
            """Bitmask flags for the walls present on a cell's four sides."""
            TOP = 1 << 0
            RIGHT = 1 << 1
            BOT = 1 << 2
            LEFT = 1 << 3
            GHOST_HOUSE = 1 << 4

        value: int = Field(..., ge=0, le=31)
        pos: vec2i = Field(...)

        @property
        def top(self) -> bool:
            """Return True if the cell has a wall on its top side."""
            return bool(self.value & Maze.Cell.Walls.TOP)

        @property
        def right(self) -> bool:
            """Return True if the cell has a wall on its right side."""
            return bool(self.value & Maze.Cell.Walls.RIGHT)

        @property
        def bot(self) -> bool:
            """Return True if the cell has a wall on its bottom side."""
            return bool(self.value & Maze.Cell.Walls.BOT)

        @property
        def left(self) -> bool:
            """Return True if the cell has a wall on its left side."""
            return bool(self.value & Maze.Cell.Walls.LEFT)

    @staticmethod
    def direction_to_wall(direction: "Direction") -> "Maze.Cell.Walls":
        """Return the Walls flag that corresponds to the given Direction."""
        match direction:
            case Direction.TOP:
                return Maze.Cell.Walls.TOP
            case Direction.RIGHT:
                return Maze.Cell.Walls.RIGHT
            case Direction.BOT:
                return Maze.Cell.Walls.BOT
            case Direction.LEFT:
                return Maze.Cell.Walls.LEFT

    @staticmethod
    def wall_to_direction(wall: "Maze.Cell.Walls") -> "Direction":
        """Return the Direction that corresponds to the given Walls flag."""
        match wall:
            case Maze.Cell.Walls.TOP:
                return Direction.TOP
            case Maze.Cell.Walls.RIGHT:
                return Direction.RIGHT
            case Maze.Cell.Walls.BOT:
                return Direction.BOT
            case Maze.Cell.Walls.LEFT:
                return Direction.LEFT
            case _:
                return (Direction.BOT)


class ClassicMaze(Maze):
    """Pre-defined classic Pac-Man maze layout (10 × 17 grid)."""

    CLASSIC_MAP: list[list[int]] = [
        [9, 5, 5, 1, 5, 3, 15, 9, 5, 3, 15, 9, 5, 1, 5, 5, 3],
        [8, 5, 5, 2, 15, 12, 5, 2, 15, 8, 5, 6, 15, 8, 5, 5, 2],
        [10, 15, 9, 4, 5, 1, 5, 6, 15, 12, 5, 1, 5, 4, 3, 15, 10],
        [8, 5, 4, 1, 5, 0, 5, 5, 21, 5, 5, 0, 5, 1, 4, 5, 2],
        [8, 5, 5, 2, 15, 10, 15, 13, 21, 7, 15, 10, 15, 8, 5, 5, 2],
        [12, 3, 15, 10, 15, 8, 5, 5, 5, 5, 5, 2, 15, 10, 15, 9, 6],
        [9, 6, 15, 10, 15, 12, 5, 3, 15, 9, 5, 6, 15, 10, 15, 12, 3],
        [8, 5, 1, 4, 5, 1, 5, 0, 5, 0, 5, 1, 5, 4, 1, 5, 2],
        [10, 15, 12, 5, 5, 2, 15, 12, 5, 6, 15, 8, 5, 5, 6, 15, 10],
        [12, 5, 5, 5, 5, 4, 5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 6],
    ]

    def __init__(self) -> None:
        """Build the classic maze from the CLASSIC_MAP constant."""
        height: int = len(self.CLASSIC_MAP)
        width: int = len(self.CLASSIC_MAP[0])

        maze: brd = []
        for y in range(height):
            row: list[Maze.Cell] = []
            for x in range(width):
                row.append(
                    Maze.Cell(value=self.CLASSIC_MAP[y][x], pos=(x, y))
                )
            maze.append(row)
        super().__init__(height, width, maze, True)


class RandomMaze(Maze):
    """Procedurally generated maze using MazeGenerator."""

    def __init__(self, height: int, width: int, seed: int) -> None:
        """
        Generate a random maze.

        height -- number of rows
        width  -- number of columns
        seed   -- seed passed to the maze generator for reproducibility
        """
        maze_generator = MazeGenerator((height, width), seed=seed)

        maze: brd = []
        for y in range(height):
            row: list[Maze.Cell] = []
            for x in range(width):
                row.append(
                    Maze.Cell(value=maze_generator.maze[y][x], pos=(x, y))
                )
            maze.append(row)

        super().__init__(height, width, maze, False)
