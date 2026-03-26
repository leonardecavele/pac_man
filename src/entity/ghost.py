from math import sqrt
from enum import IntFlag

from .pac_man import Pac_man
from .entity import DEFAULT_VELOCITY, Entity

from src.type import vec2
from src.maze import Maze


# frightened mode
# flip direction immediately ( go back ) and then move randomly


# CHASE MODE
# flip direction immediately ( go back ) when entering
# depends on the ghost

# scatter mode
# flip direction immediately ( go back ) when entering
# go on their corners
# tweek by the main loop but only a few frames


# house mode
# run at house and goes back to chase or scatter depending
# on the game state

# find a way to increase velocity of blinky in angry mode


# update is to be called every new cell entered, not every frame


class Ghost(Entity):
    class State(IntFlag):
        SCATTER = 1 << 0
        EATEN = 1 << 1
        FRIGHTENED = 1 << 2
        CHASE = 1 << 3
        ANGRY = 1 << 4  # only for blinky

    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze,
        pac_man: Pac_man, house_pos: vec2, corner_pos: vec2
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m)
        self.state: Ghost.State = self.State.SCATTER
        self.pac_man: Pac_man = pac_man
        self.corner: vec2 = corner_pos
        self.house: vec2 = house_pos
        self.target: vec2 | None = None

    def target_direction(self) -> None:
        x, y = self.maze_pos
        directions = self.legal_directions(x, y)

        if not directions or self.target is None:
            self.direction = (0, 0)
            return

        best_direction: Maze.Direction = directions[0]
        best_pos: vec2 = (
            x + best_direction.value[0], y + best_direction.value[1]
        )
        best_distance = self.manhattan(best_pos, self.target)

        for direction in directions[1:]:
            pos = (x + direction.value[0], y + direction.value[1])
            distance = self.manhattan(pos, self.target)

            if distance < best_distance:
                best_distance = distance
                best_direction = direction

        self.direction = best_direction.value

    def legal_directions(self, x: int, y: int) -> list[Maze.Direction]:
        back = self.back_direction
        directions: list[Maze.Direction] = []

        for direction in Maze.Direction:
            if self.maze.maze[y][x] & Maze.convert(direction):
                continue
            if back is not None and direction == back:
                continue
            directions.append(direction)

        if not directions and back is not None:
            return [back]
        return directions

    @property
    def back_direction(self) -> Maze.Direction | None:
        if self.direction == (0, 0):
            return None
        return Maze.Direction((-self.direction[0], -self.direction[1]))

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
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze,
        pac_man: Pac_man, house_pos: vec2
    ) -> None:
        super().__init__(
            screen_pos,
            maze_pos,
            sprite,
            m,
            pac_man,
            house_pos,
            (self.maze.width - 1, 0)
        )
        self.target: vec2 = self.corner

    def update(self) -> None:
        if (
            self.state & self.State.SCATTER
            and not self.state & self.State.ANGRY
        ):
            self.target = self.corner
        else:
            self.target = self.pac_man.maze_pos
        self.target_direction()


class Inky(Ghost):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze,
        pac_man: Pac_man, house_pos: vec2
    ) -> None:
        super().__init__(
            screen_pos,
            maze_pos,
            sprite,
            m,
            pac_man,
            house_pos,
            (self.maze.width - 1, self.maze.height - 1)
        )
        self.target: vec2 = self.corner

    def update(self) -> None:
        if self.state & self.State.SCATTER:
            self.target = self.corner
        else:
            self.target = self.pac_man.maze_pos
        self.target_direction()


class Pinky(Ghost):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze,
        pac_man: Pac_man, house_pos: vec2
    ) -> None:
        super().__init__(
            screen_pos,
            maze_pos,
            sprite,
            m,
            pac_man,
            house_pos,
            (0, 0)
        )
        self.target: vec2 = self.corner

    def update(self) -> None:
        if self.state & self.State.SCATTER:
            self.target = self.corner
        else:
            self.target = self.pac_man.maze_pos
        self.target_direction()


class Clyde(Ghost):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze,
        pac_man: Pac_man, house_pos: vec2
    ) -> None:
        super().__init__(
            screen_pos,
            maze_pos,
            sprite,
            m,
            pac_man,
            house_pos,
            (0, self.maze.height - 1)
        )
        self.target: vec2 = self.corner

    def update(self) -> None:
        if (
            self.euclidean(self.maze_pos, self.pac_man.maze_pos) <= 8
            or self.state & self.State.SCATTER
        ):
            self.target = self.corner
        else:
            self.target = self.pac_man.maze_pos
        self.target_direction()
