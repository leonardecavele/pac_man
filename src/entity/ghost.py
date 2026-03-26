import random

from math import sqrt
from enum import IntFlag
from abc import ABC, abstractmethod

from .pac_man import Pac_man
from .entity import DEFAULT_VELOCITY, Entity

from src.type import vec2
from src.maze import Maze


# update is to be called every new cell entered, not every frame

class Ghost(Entity, ABC):
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
        self.flip: bool = False

    def change_state(self, new_state: State) -> None:
        match new_state:
            case self.State.ANGRY:
                self.velocity = DEFAULT_VELOCITY * 2
                self.state = self.State.ANGRY
            case self.State.CHASE:
                self.flip = True
                self.state = self.State.CHASE
            case self.State.SCATTER:
                self.flip = True
                self.state = self.State.SCATTER
            case self.State.EATEN:
                self.velocity = DEFAULT_VELOCITY * 3
                self.state = self.State.EATEN
            case self.State.FRIGHTENED:
                self.flip = True
                self.state = self.State.FRIGHTENED

    def target_direction(self) -> None:
        x, y = self.maze_pos
        directions = self.legal_directions(x, y)

        # case ghost must flip
        if self.flip:
            back = self.back_direction
            if back is not None:
                self.direction = back.value
            self.flip = False
            return

        # case ghost has no valid move
        if not directions:
            self.direction = (0, 0)
            return

        # case ghost must move randomly
        if self.target is None:
            random_direction = random.choice(directions)
            self.direction = random_direction.value
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

    @abstractmethod
    def update(self) -> None:
        ...


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
        self.target = self.corner

    def update(self) -> None:
        if self.state & self.State.EATEN:
            self.target = self.house
        elif self.state & self.State.FRIGHTENED:
            self.target = None
        elif self.state & (self.State.CHASE | self.State.ANGRY):
            self.target = self.pac_man.maze_pos
        else:
            self.target = self.corner

        self.target_direction()


class Inky(Ghost):
    def __init__(
        self,
        screen_pos: vec2,
        maze_pos: vec2,
        sprite: str,
        m: Maze,
        pac_man: Pac_man,
        blinky: Blinky,
        house_pos: vec2
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
        self.blinky: Blinky = blinky
        self.target = self.corner

    def chase(self) -> vec2:
        px, py = self.pac_man.maze_pos
        dx, dy = self.pac_man.direction
        bx, by = self.blinky.maze_pos

        if (dx, dy) == (0, -1):
            ahead = (px - 2, py - 2)
        else:
            ahead = (px + dx * 2, py + dy * 2)

        ax, ay = ahead
        return (ax * 2 - bx, ay * 2 - by)

    def update(self) -> None:
        if self.state & self.State.EATEN:
            self.target = self.house
        elif self.state & self.State.FRIGHTENED:
            self.target = None
        elif self.state & self.State.CHASE:
            self.target = self.chase()
        else:
            self.target = self.corner

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
        self.target = self.corner

    def update(self) -> None:
        if self.state & self.State.EATEN:
            self.target = self.house
        elif self.state & self.State.FRIGHTENED:
            self.target = None
        elif self.state & self.State.CHASE:
            px, py = self.pac_man.maze_pos
            dx, dy = self.pac_man.direction

            if (dx, dy) == (0, -1):
                self.target = (px - 4, py - 4)
            else:
                self.target = (px + dx * 4, py + dy * 4)
        else:
            self.target = self.corner

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
        self.target = self.corner

    def update(self) -> None:
        if self.state & self.State.EATEN:
            self.target = self.house
        elif self.state & self.State.FRIGHTENED:
            self.target = None
        elif self.state & self.State.CHASE:
            if self.euclidean(self.maze_pos, self.pac_man.maze_pos) < 8:
                self.target = self.corner
            else:
                self.target = self.pac_man.maze_pos
        else:
            self.target = self.corner

        self.target_direction()
