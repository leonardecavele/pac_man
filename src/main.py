import sys

from mazegenerator import MazeGenerator

from src.error import ErrorCode
from src.display import Display


def main() -> int:
    maze_generator: MazeGenerator = MazeGenerator()
    maze_generator.generate(42)
    maze: list[list[int]] = maze_generator.maze
    display: Display = Display(maze)
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
