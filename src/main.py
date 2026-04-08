import sys

from random import randint

from src.game import Game
from src.error import ErrorCode
from src.parsing.parsing import Parser


def main() -> int:
    parser = Parser("config.json")
    config = parser.run()

    game: Game = Game(
        config=config,
        screen_ratio=0.50,
        title="Pac_Man",
        fps=120,
    )
    game.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
