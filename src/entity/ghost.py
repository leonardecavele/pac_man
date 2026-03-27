import random
import heapq

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

    def change_state(self, new_state: "Ghost.State") -> None:
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

    def a_star_direction(self, target: vec2) -> vec2 | None:
        counter: int = 0

        def push(
            queue: list[tuple[int, int, Maze.Cell]],
            new_cell: Maze.Cell,
            score: int
        ) -> None:
            nonlocal counter
            heapq.heappush(queue, (score, counter, new_cell))
            counter += 1

        start_x, start_y = self.maze_pos
        goal_x, goal_y = target

        if not (0 <= goal_x < self.maze.width and 0 <= goal_y < self.maze.height):
            return None

        start_pos: vec2 = (start_x, start_y)
        goal_pos: vec2 = (goal_x, goal_y)

        if start_pos == goal_pos:
            return None

        back: Maze.Direction | None = self.back_direction

        visited: set[vec2] = set()
        parent: dict[vec2, vec2] = {}

        queue: list[tuple[int, int, Maze.Cell]] = []
        g: dict[vec2, int] = {}
        h: dict[vec2, int] = {}

        g[start_pos] = 0
        h[start_pos] = self.manhattan(start_pos, goal_pos)
        push(
            queue,
            self.maze.maze[start_y][start_x],
            g[start_pos] + h[start_pos]
        )

        while queue:
            _, _, current = heapq.heappop(queue)
            x, y = current.pos

            if (x, y) == goal_pos:
                current_pos: vec2 = (x, y)

                while current_pos in parent and parent[current_pos] != start_pos:
                    current_pos = parent[current_pos]

                if current_pos not in parent:
                    return None

                dx: int = current_pos[0] - start_x
                dy: int = current_pos[1] - start_y
                return (dx, dy)

            if (x, y) in visited:
                continue

            visited.add((x, y))

            for direction in Maze.Direction:
                if (x, y) == start_pos and back is not None and direction == back:
                    continue

                if self.maze.maze[y][x].value & Maze.convert(direction):
                    continue

                new_x: int = x + direction.value[0]
                new_y: int = y + direction.value[1]

                if not (0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height):
                    continue

                if (new_x, new_y) in visited:
                    continue

                new_pos: vec2 = (new_x, new_y)
                new_g: int = g[(x, y)] + 1

                if new_pos not in g or new_g < g[new_pos]:
                    parent[new_pos] = (x, y)
                    g[new_pos] = new_g
                    h[new_pos] = self.manhattan(new_pos, goal_pos)
                    push(
                        queue,
                        self.maze.maze[new_y][new_x],
                        new_g + h[new_pos]
                    )

        return None


    def target_direction(self) -> None:
        x, y = self.maze_pos
        directions = self.legal_directions(x, y)

        if self.flip:
            back = self.back_direction
            if back is not None:
                self.direction = back.value
            self.flip = False
            return

        if not directions:
            self.direction = (0, 0)
            return

        if self.target is None:
            random_direction = random.choice(directions)
            self.direction = random_direction.value
            return

        next_direction: vec2 | None = self.a_star_direction(self.target)

        if next_direction is not None:
            self.direction = next_direction
            return

        best_direction: Maze.Direction = directions[0]
        best_pos: vec2 = (
            x + best_direction.value[0], y + best_direction.value[1]
        )
        best_distance: int = self.manhattan(best_pos, self.target)

        for direction in directions[1:]:
            pos: vec2 = (x + direction.value[0], y + direction.value[1])
            distance: int = self.manhattan(pos, self.target)

            if distance < best_distance:
                best_distance = distance
                best_direction = direction

        self.direction = best_direction.value

    def legal_directions(self, x: int, y: int) -> list[Maze.Direction]:
        back = self.back_direction
        directions: list[Maze.Direction] = []

        for direction in Maze.Direction:
            if self.maze.maze[y][x].value & Maze.convert(direction):
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
            (m.width - 1, 0)
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
            (m.width - 1, m.height - 1)
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
            (0, m.height - 1)
        )
        self.target = self.corner

    def update(self) -> None:
        if self.state & self.State.EATEN:
            self.target = self.house
        elif self.state & self.State.FRIGHTENED:
            self.target = None
        elif self.state & self.State.CHASE:
            if self.euclidean(self.maze_pos, self.pac_man.maze_pos) < 4:
                self.target = self.corner
            else:
                self.target = self.pac_man.maze_pos
        else:
            self.target = self.corner

        self.target_direction()
