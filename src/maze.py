from enum import Enum, IntFlag

from pydantic import BaseModel, Field
from mazegenerator import MazeGenerator

from src.type import vec2i, brd


class Maze:
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

        value: int = Field(..., ge=0, le=15)
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

    def __init__(self, height: int, width: int, seed: int) -> None:
        maze_generator: MazeGenerator = MazeGenerator(
            (height, width), seed=seed
        )

        self.maze: brd = []
        for y in range(height):
            self.maze.append([])
            for x in range(width):
                self.maze[y].append(
                    Maze.Cell(value=maze_generator.maze[y][x], pos=(x, y))
                )

        self.height = height
        self.width = width

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
