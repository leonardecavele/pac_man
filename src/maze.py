from enum import Enum, IntFlag
from abc import ABC

from pydantic import BaseModel, Field
from mazegenerator import MazeGenerator

from src.type import vec2i, brd


class Maze(ABC):
    def __init__(self, height: int, width: int, maze: brd, og: bool) -> None:
        self.height: int = height
        self.width: int = width
        self.maze: brd = maze
        self.og: bool = og

    class Direction(Enum):
        TOP = (0, -1)
        RIGHT = (1, 0)
        BOT = (0, 1)
        LEFT = (-1, 0)

    class Cell(BaseModel):
        class Walls(IntFlag):
            TOP = 1 << 0
            RIGHT = 1 << 1
            BOT = 1 << 2
            LEFT = 1 << 3
            GHOST_HOUSE = 1 << 4

        value: int = Field(..., ge=0, le=31)
        pos: vec2i = Field(...)

        @property
        def top(self) -> bool:
            return bool(self.value & Maze.Cell.Walls.TOP)

        @property
        def right(self) -> bool:
            return bool(self.value & Maze.Cell.Walls.RIGHT)

        @property
        def bot(self) -> bool:
            return bool(self.value & Maze.Cell.Walls.BOT)

        @property
        def left(self) -> bool:
            return bool(self.value & Maze.Cell.Walls.LEFT)

    @staticmethod
    def direction_to_wall(direction: "Maze.Direction") -> "Maze.Cell.Walls":
        match direction:
            case Maze.Direction.TOP:
                return Maze.Cell.Walls.TOP
            case Maze.Direction.RIGHT:
                return Maze.Cell.Walls.RIGHT
            case Maze.Direction.BOT:
                return Maze.Cell.Walls.BOT
            case Maze.Direction.LEFT:
                return Maze.Cell.Walls.LEFT

    @staticmethod
    def wall_to_direction(wall: "Maze.Cell.Walls") -> "Maze.Direction":
        match wall:
            case Maze.Cell.Walls.TOP:
                return Maze.Direction.TOP
            case Maze.Cell.Walls.RIGHT:
                return Maze.Direction.RIGHT
            case Maze.Cell.Walls.BOT:
                return Maze.Direction.BOT
            case Maze.Cell.Walls.LEFT:
                return Maze.Direction.LEFT


class OriginalMaze(Maze):
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

    def __init__(self):
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
    def __init__(self, height: int, width: int, seed: int) -> None:
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
