import os
import sys

from src.app import App
from src.error import ErrorCode
from src.parsing import Parser


def main() -> int:
    """Run the Pac-Man application and return an exit code."""
    config_path = os.path.abspath(sys.argv[1]) if len(sys.argv) == 2 else None

    if '__compiled__' in globals():
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if config_path is None:
        if (len(sys.argv) < 2):
            print("The program must have a valid config file")
        else:
            print("The program must only have one valid config file")
        sys.exit(ErrorCode.INVALID_CONFIG)
    parser = Parser(config_path)
    config = parser.run()

    app: App = App(
        config=config,
        screen_ratio=0.70,
        title="Pac_Man",
        fps=60,
    )
    app.run()
    return ErrorCode.NO_ERROR


if (__name__ == "__main__"):
    sys.exit(main())
