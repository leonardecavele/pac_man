import sys

from src.app import App
from src.error import ErrorCode
from src.parsing import Parser


def main() -> int:
    if (len(sys.argv) != 2):
        sys.exit(ErrorCode.INVALID_CONFIG)
    parser = Parser(sys.argv[1])
    config = parser.run()

    app: App = App(
        config=config,
        screen_ratio=0.70,
        title="Pac_Man",
        fps=120,
    )
    app.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
