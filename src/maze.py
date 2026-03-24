from enum import IntEnum

from mazegenerator import MazeGenerator

from src.type import brd


class Maze():
    def __init__(
        self, height: int, width: int, seed: int
    ) -> None:
        maze_generator: MazeGenerator = MazeGenerator((height, width))
        maze_generator.generate(seed)
        self.maze: brd = maze_generator.maze
        self.height = height
        self.width = width

    class Tile(IntEnum):
        UP = 1 << 0
        RIGHT = 1 << 1
        DOWN = 1 << 2
        LEFT = 1 << 3
