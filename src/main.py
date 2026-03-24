import sys

from mazegenerator import MazeGenerator

from src.maze import Maze
from src.error import ErrorCode


def main() -> int:
    maze: Maze = Maze(42, 42, 42)
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
