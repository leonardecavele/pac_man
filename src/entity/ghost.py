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

    def next_direction(self, target: vec2) -> vec2:
        best_direction: vec2 = (0, 0)
        best_score: int = 0

        for direction in Maze.Direction:
            new_x: int = self.maze_pos[0] + direction.value[0]
            new_y: int = self.maze_pos[1] + direction.value[1]
            score: int = self.manhattan((new_x, new_y), target)

            if best_score is None or score < best_score:
                best_score = score
                best_direction = direction.value

        return best_direction

    @staticmethod
    def euclidean(pos1: vec2, pos2: vec2) -> int:
        dx: int = pos2[0] - pos1[0]
        dy: int = pos2[1] - pos1[1]
        return int(sqrt(dx * dx + dy * dy))

    @staticmethod
    def manhattan(pos1: vec2, pos2: vec2) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


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
        if self.euclidean(self.maze_pos, self.pac_man.maze_pos) <= 8:
            direction = self.next_direction((self.maze.height, 0))
        else:
            direction = self.next_direction(self.pac_man.maze_pos)
        self.direction = direction
