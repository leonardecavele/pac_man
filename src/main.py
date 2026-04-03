import sys

from random import randint

from src.maze import Maze, OriginalMaze, RandomMaze
from src.game import Game
from src.error import ErrorCode
from src.parsing.parsing import Parser


def main() -> int:
    parser = Parser("config.json")
    config = parser.run()

    maze: Maze = RandomMaze(12, 12, 13)
    game: Game = Game(
        maze=maze,
        config=config,
        width=700,
        height=900,
        title="Pac_Man",
        fps=120,
    )
    #maze: Maze = OriginalMaze()
    #game: Game = Game(
    #    maze=maze,
    #    config=config,
    #    width=1050,
    #    height=1050,
    #    title="Pac_Man",
    #    fps=120,
    #)

    game.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
