from typing import TypeAlias, TYPE_CHECKING

if TYPE_CHECKING:
    from src.maze import Maze

vec2i: TypeAlias = tuple[int, int]
vec2f: TypeAlias = tuple[float, float]
brd: TypeAlias = list[list["Maze.Cell"]]
