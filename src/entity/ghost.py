from math import sqrt

from .pac_man import Pac_man
from .entity import Entity

from src.type import vec2
from src.maze import Maze


class Ghost(Entity):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2,
        sprite: str, m: Maze, pac_man: Pac_man
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m)
        self.scatter: bool = False
        self.pac_man: Pac_man = pac_man

    def a_star(self, target: vec2) -> vec2:
        return (0, 0)

    @staticmethod
    def pos_distance(pos1: vec2, pos2: vec2) -> int:
        dx: int = pos2[0] - pos1[0]
        dy: int = pos2[1] - pos1[1]
        return int(sqrt(dx * dx + dy * dy))


class Blinky(Ghost):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2,
        sprite: str, m: Maze, pac_man: Pac_man
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m, pac_man)
        self.angry: bool = False


class Inky(Ghost):
    pass


class Pinky(Ghost):
    pass


class Clyde(Ghost):
    def update(self) -> None:
        direction: vec2
        if self.pos_distance(self.maze_pos, self.pac_man.maze_pos) <= 8:
            direction = self.a_star((self.maze.height, 0))
        else:
            direction = self.a_star(self.pac_man.maze_pos)
        self.direction = direction
