import sys

from random import randint

from src.app import App
from src.error import ErrorCode
from src.parsing.parsing import Parser


def main() -> int:
    parser = Parser("config.json")
    config = parser.run()

    app: App = App(
        config=config,
        screen_ratio=0.80,
        title="Pac_Man",
        fps=120,
    )
    app.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
