from enum import IntEnum

from pydantic import BaseModel, Field
from mazegenerator import MazeGenerator

from src.type import vec2, brd


class Maze():

    class Cell(BaseModel):

        class Walls(IntEnum):
            TOP = 1 << 0
            RIGHT = 1 << 1
            BOT = 1 << 2
            LEFT = 1 << 3

        value: int = Field(..., ge=0, le=15)
        pos: vec2 = Field(...)

        @property
        def top(self):
            return bool(self.value & Maze.Cell.Walls.TOP)

        @property
        def right(self):
            return bool(self.value & Maze.Cell.Walls.RIGHT)

        @property
        def bot(self):
            return bool(self.value & Maze.Cell.Walls.BOT)

        @property
        def left(self):
            return bool(self.value & Maze.Cell.Walls.LEFT)

    def __init__(
        self, height: int, width: int, seed: int
    ) -> None:
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
