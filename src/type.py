from typing import TypeAlias, TYPE_CHECKING

if TYPE_CHECKING:
    from src.maze import Maze

vec2: TypeAlias = tuple[int, int]
brd: TypeAlias = list[list["Maze.Cell"]]
