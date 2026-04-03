import sys

from random import randint

from src.maze import Maze, OriginalMaze, RandomMaze
from src.game import Game
from src.error import ErrorCode
from src.parsing.parsing import Parser


def main() -> int:
    parser = Parser("config.json")
    config = parser.run()

    #maze: Maze = RandomMaze(13, 13, 10)
    maze: Maze = OriginalMaze()

    game: Game = Game(
        maze=maze,
        config=config,
        width=1400,
        height=1400,
        title="Pac_Man",
        fps=120,
    )
    game.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
