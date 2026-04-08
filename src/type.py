from typing import TypeAlias, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from src.maze import Maze

vec2i: TypeAlias = tuple[int, int]
vec2f: TypeAlias = tuple[float, float]
brd: TypeAlias = list[list["Maze.Cell"]]


class Direction(Enum):
    TOP = (0, -1)
    RIGHT = (1, 0)
    BOT = (0, 1)
    LEFT = (-1, 0)
