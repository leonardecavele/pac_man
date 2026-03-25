import sys

from src.maze import Maze
from src.error import ErrorCode
from src.display import Display
from src.parsing.parsing import Parser


def main() -> int:
    parser = Parser("config.json")
    config = parser.run()
    maze: Maze = Maze(20, 20, 42)
    Display(maze)
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
