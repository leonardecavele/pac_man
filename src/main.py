import sys

from src.maze import Maze
from src.game import Game
from src.error import ErrorCode
from src.parsing.parsing import Parser


def main() -> int:
    parser = Parser("config.json")
    config = parser.run()
    maze: Maze = Maze(12, 12, 11)
    game: Game = Game(
        maze=maze,
        config=config,
        width=1000,
        height=1200,
        title="Pac_Man",
        fps=120,
    )
    game.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
