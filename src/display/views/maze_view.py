import pyray as rl
import math
from enum import Enum, auto

from src.display.maze_renderer import MazeRenderer
from .view import View, ViewEvent, ViewEventType
from src.maze import Maze
from src.type import vec2
from src.entity import (
    Ghost, Entity, Blinky, Inky, Pinky, Clyde, Pac_man, Pacgum,
    SuperPacgum
)
from src.parsing.config import Config


class CollisionEvent(Enum):
    NONE = auto()
    DEATH = auto()


class MazeView(View):
    def __init__(
        self, maze: Maze, config: Config, textures: dict[str, rl.Texture2D],
        gap: int, cell_size: int, width: int = 720, height: int = 720
    ) -> None:
        self.maze: Maze = maze
        self.width: int = width
        self.height: int = height
        self.config = config
        self.textures = textures
        self.gap = gap
        self.cell_size = cell_size

        self.maze_image = rl.gen_image_color(
            self.width, self.height, rl.BLACK
        )
        MazeRenderer(
            self.maze_image, self.maze, self.cell_size, self.gap
        )
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

        self.tick_rate: float = 8.0
        self.tick_interval: float = 1.0 / self.tick_rate
        self.init()

    def init(self) -> None:
        self.score: int = 0
        self.timer: float = 0.0
        self.fright: bool = False
        self.fright_time: float = 0
        self.tick_accumulator: float = 0.0
        self.ghost_behavior: dict[float, Ghost.State] = {
            7: Ghost.State.SCATTER,
            27: Ghost.State.CHASE,
            34: Ghost.State.SCATTER,
            54: Ghost.State.CHASE,
            59: Ghost.State.SCATTER,
            79: Ghost.State.CHASE,
            84: Ghost.State.SCATTER,
            float("inf"): Ghost.State.CHASE,
        }
        center: vec2 = ((self.maze.width // 2), self.maze.height // 2)

        top_pos: vec2 = (self.maze.width // 2, 1)
        bottom_pos: vec2 = (self.maze.width // 2, self.maze.height - 2)
        left_pos: vec2 = (1, self.maze.height // 2)
        right_pos: vec2 = (self.maze.width - 2, self.maze.height // 2)

        self.pac_man: Pac_man = Pac_man(
            screen_pos=self._maze_to_screen(center),
            maze_pos=center,
            sprite=self.textures["pac_man"],
            m=self.maze,
        )

        blinky: Blinky = Blinky(
            screen_pos=self._maze_to_screen(top_pos),
            maze_pos=top_pos,
            sprite=self.textures["blinky"],
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
        )

        inky: Inky = Inky(
            screen_pos=self._maze_to_screen(right_pos),
            maze_pos=right_pos,
            sprite=self.textures["inky"],
            m=self.maze,
            pac_man=self.pac_man,
            blinky=blinky,
            house_pos=center,
        )

        pinky: Pinky = Pinky(
            screen_pos=self._maze_to_screen(left_pos),
            maze_pos=left_pos,
            sprite=self.textures["pinky"],
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
        )

        clyde: Clyde = Clyde(
            screen_pos=self._maze_to_screen(bottom_pos),
            maze_pos=bottom_pos,
            sprite=self.textures["clyde"],
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
        )

        self.enemies: list[Ghost] = [
            blinky,
            inky,
            pinky,
            clyde
        ]
        self.collectibles = self._gen_pacgums()

        for entity in self.enemies:
            entity.update()

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)
        rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)
        for i in [self.collectibles, self.enemies, [self.pac_man]]:
            for e in i:
                x, y = e.screen_pos
                x -= self.cell_size // 2
                y -= self.cell_size // 2
                rl.draw_texture(e.sprite, x + 1, y + 1, rl.WHITE)
        rl.draw_text(f"Score: {self.score} - Timer: {math.floor(self.timer)}",
                     self.gap,
                     (self.maze.height + 1) * (self.cell_size + self.gap),
                     30, rl.WHITE)

    def update(self, dt: float) -> ViewEvent:
        self._handle_input()

        self.timer += dt
        if (self.fright):
            self.fright_time += dt
        else:
            self.tick_accumulator += dt
            for time, state in self.ghost_behavior.items():
                if (time < self.tick_accumulator):
                    continue
                self.switch_state(state)
                break
        if (self.fright_time > 6):
            self.fright_time = 0
            self.fright = False
            for e in self.enemies:
                e.load_save()

        pac = self.pac_man
        prev_pos = pac.maze_pos
        pac.move(dt)
        self._sync_maze_pos_from_screen_pos(pac)
        dx, dy = pac.direction
        if (pac.direction == (0, 0) or pac.maze_pos != prev_pos or
                (pac.next_direction and dx and pac.next_direction[0]) or
                (pac.next_direction and dy and pac.next_direction[1])):
            pac.update()

        for ghost in self.enemies:
            prev_pos = ghost.maze_pos
            ghost.move(dt)
            self._sync_maze_pos_from_screen_pos(ghost)
            if ghost.maze_pos != prev_pos:
                ghost.update()

        if (not len(self.collectibles)):
            return (ViewEvent(
                type=ViewEventType.CHANGE_VIEW, message="main_menu"
            ))
        match self._check_collision():
            case CollisionEvent.DEATH:
                self.init()
                return (ViewEvent(
                    type=ViewEventType.CHANGE_VIEW, message="main_menu"
                ))
            case _:
                return (ViewEvent(type=ViewEventType.NONE))

    def _collides(self, a: Entity, b: Entity) -> bool:
        size: int = self.cell_size // 2
        return (
            abs(a.screen_pos[0] - b.screen_pos[0]) < size
            and abs(a.screen_pos[1] - b.screen_pos[1]) < size
        )

    def _check_collision(self) -> CollisionEvent:
        for gum in self.collectibles:
            if self._collides(gum, self.pac_man):
                self.collectibles.remove(gum)
                if (isinstance(gum, SuperPacgum)):
                    self.score += self.config.points_per_super_pacgum
                    self.fright = True
                    self.fright_time = 0
                    for e in self.enemies:
                        e.sprite = self.textures["fleeing"]
                        e.change_state(Ghost.State.FRIGHTENED)
                else:
                    self.score += self.config.points_per_pacgum
                return (CollisionEvent.NONE)
        for ghost in self.enemies:
            if self._collides(ghost, self.pac_man):
                if (ghost.state == Ghost.State.FRIGHTENED):
                    self.enemies.remove(ghost)
                    self.score += self.config.points_per_ghost
                else:
                    return (CollisionEvent.DEATH)
        return (CollisionEvent.NONE)

    def switch_state(self, state: Ghost.State) -> None:
        for e in self.enemies:
            e.state = state

    def _sync_maze_pos_from_screen_pos(self, entity: Entity) -> None:
        sx, sy = entity.screen_pos
        step: int = self.cell_size + self.gap
        dx, dy = entity.direction

        raw_x: float = (sx - self.gap -
                        self.cell_size / 2) / step
        raw_y: float = (sy - self.gap -
                        self.cell_size / 2) / step

        mx: int = math.floor(raw_x) if dx > 0 else math.ceil(
            raw_x) if dx < 0 else round(raw_x)
        my: int = math.floor(raw_y) if dy > 0 else math.ceil(
            raw_y) if dy < 0 else round(raw_y)

        entity.maze_pos = (
            max(0, min(mx, self.maze.width - 1)),
            max(0, min(my, self.maze.height - 1)),
        )

    def _maze_to_screen(self, pos: vec2) -> vec2:
        x, y = pos
        step: int = self.cell_size + self.gap

        screen_x: int = (
            self.gap
            + x * step
            + self.cell_size // 2
        )
        screen_y: int = (
            self.gap
            + y * step
            + self.cell_size // 2
        )
        return (screen_x, screen_y)

    def close(self) -> None:
        rl.unload_texture(self.maze_texture)
        rl.unload_image(self.maze_image)

    def _DEBUG_grid(self):
        for i in range(self.maze.width + 1):
            rl.draw_line(i * (self.cell_size + self.gap) + self.gap // 2, 0,
                         i * (self.cell_size + self.gap) +
                         self.gap // 2, self.height,
                         rl.PURPLE)
        for i in range(self.maze.height + 1):
            rl.draw_line(0,
                         i * (self.cell_size + self.gap) + self.gap // 2,
                         self.width,
                         i * (self.cell_size + self.gap) + self.gap // 2,
                         rl.PURPLE)

    def _handle_input(self) -> None:
        next_direction: vec2 | None = None

        if (
            rl.is_key_down(rl.KEY_UP)
            or rl.is_key_down(rl.KEY_W)
            or rl.is_key_down(rl.KEY_Z)
            or rl.is_key_down(rl.KEY_K)
        ):
            next_direction = Maze.Direction.TOP.value
        elif (
            rl.is_key_down(rl.KEY_RIGHT)
            or rl.is_key_down(rl.KEY_D)
            or rl.is_key_down(rl.KEY_L)
        ):
            next_direction = Maze.Direction.RIGHT.value
        elif (
            rl.is_key_down(rl.KEY_DOWN)
            or rl.is_key_down(rl.KEY_S)
            or rl.is_key_down(rl.KEY_J)
        ):
            next_direction = Maze.Direction.BOT.value
        elif (
            rl.is_key_down(rl.KEY_LEFT)
            or rl.is_key_down(rl.KEY_A)
            or rl.is_key_down(rl.KEY_Q)
            or rl.is_key_down(rl.KEY_H)
        ):
            next_direction = Maze.Direction.LEFT.value

        if next_direction is not None:
            self.pac_man.next_direction = next_direction

    def _gen_pacgums(self) -> list[Entity]:
        pacgums: list[Entity] = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if (self.maze.maze[y][x].value == 15):
                    continue
                if ((x == 0 and y == 0) or
                    (x == 0 and y == self.maze.height - 1) or
                    (x == self.maze.width - 1 and y == 0) or
                    (x == self.maze.width - 1
                     and y == self.maze.height - 1)):
                    pacgums.append(SuperPacgum(
                        self._maze_to_screen((x, y)), (x, y),
                        self.textures["super_pacgum"], self.maze)
                    )
                else:
                    pacgums.append(
                        Pacgum(self._maze_to_screen((x, y)), (x, y),
                               self.textures["pacgum"], self.maze)
                    )
        return (pacgums)
