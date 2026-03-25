import sys

from src.maze import Maze
from src.error import ErrorCode
from src.display import Display


def main() -> int:
    maze: Maze = Maze(42, 42, 42)
    Display(maze)
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
