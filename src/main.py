import sys

from src.maze import Maze
from src.game import Game
from src.error import ErrorCode
# from src.parsing.parsing import Parser


def main() -> int:
    # parser = Parser("config.json")
    # config = parser.run()
    maze: Maze = Maze(20, 20, 42)
    game: Game = Game(
        maze=maze,
        width=900,
        height=700,
        title="Pac_Man",
        fps=60,
    )
    game.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
