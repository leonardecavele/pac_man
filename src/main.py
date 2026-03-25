import sys

from src.maze import Maze
from src.error import ErrorCode
from src.display import Display
from src.parsing.parsing import Parser
from src.entity.collectible import Pacgum


def gen_pacgums(maze: Maze):
    pacgums: list[Pacgum] = []
    for y in range(maze.height):
        for x in range(maze.width):
            if ((x == 0 and y == 0) or (x == 0 and y == maze.height - 1) or
                    (x == maze.width - 1 and y == 0) or
                    (x == maze.width - 1 and y == maze.height - 1) or
                    maze.maze[y][x].value == 15):
                continue
            pacgums.append(Pacgum((0, 0), (x, y), "", maze))
    return (pacgums)


def main() -> int:
    parser = Parser("config.json")
    config = parser.run()
    maze: Maze = Maze(15, 15, 42)
    pacgums = gen_pacgums(maze)
    Display(maze, pacgums)
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
