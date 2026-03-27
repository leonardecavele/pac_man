import pyray as raylib

from src.display.display import Display
from src.maze import Maze
from src.entity import Ghost, Entity, Blinky, Inky, Pinky, Clyde, Pac_man
from src.type import vec2


class Game:
    def __init__(
        self,
        maze: Maze,
        width: int = 720,
        height: int = 720,
        title: str = "pac_man",
        fps: int = 60,
        tick_rate: float = 8.0,
    ) -> None:
        self.maze: Maze = maze
        self.display: Display = Display(
            maze=maze,
            width=width,
            height=height,
            title=title,
            fps=fps,
        )
        self.timer: float = 0.0

        self.tick_rate: float = tick_rate
        self.tick_interval: float = 1.0 / self.tick_rate
        self.tick_accumulator: float = 0.0

        center: vec2 = ((self.maze.width // 2) + 3, self.maze.height // 2)

        top_pos: vec2 = (self.maze.width // 2, 1)
        bottom_pos: vec2 = (self.maze.width // 2, self.maze.height - 2)
        left_pos: vec2 = (1, self.maze.height // 2)
        right_pos: vec2 = (self.maze.width - 2, self.maze.height // 2)

        self.pac_man: Pac_man = Pac_man(
            screen_pos=self._maze_to_screen(center),
            maze_pos=center,
            sprite="pac_man",
            m=self.maze,
        )

        blinky: Blinky = Blinky(
            screen_pos=self._maze_to_screen(top_pos),
            maze_pos=top_pos,
            sprite="blinky",
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
        )

        inky: Inky = Inky(
            screen_pos=self._maze_to_screen(right_pos),
            maze_pos=right_pos,
            sprite="inky",
            m=self.maze,
            pac_man=self.pac_man,
            blinky=blinky,
            house_pos=center,
        )

        pinky: Pinky = Pinky(
            screen_pos=self._maze_to_screen(left_pos),
            maze_pos=left_pos,
            sprite="pinky",
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
        )

        clyde: Clyde = Clyde(
            screen_pos=self._maze_to_screen(bottom_pos),
            maze_pos=bottom_pos,
            sprite="clyde",
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
        )

        self.entity_list: list[Entity] = [
            blinky,
            inky,
            pinky,
            clyde,
            self.pac_man,
        ]

        for entity in self.entity_list:
            if isinstance(entity, Ghost):
                entity.update()

    def run(self) -> None:
        while not self.display.should_close():
            dt: float = self.display.get_frame_time()
            self.update(dt)
            self.display.draw(self.entity_list)

        self.display.close()

    def update(self, dt: float) -> None:
        self._handle_input()

        self.timer += dt
        cycle_time: float = self.timer % 50.0

        if cycle_time < 10.0:
            global_ghost_state: Ghost.State = Ghost.State.SCATTER
        else:
            global_ghost_state = Ghost.State.CHASE

        for entity in self.entity_list:
            if isinstance(entity, Ghost):
                if entity.state not in (
                    Ghost.State.EATEN, Ghost.State.FRIGHTENED
                ):
                    if entity.state != global_ghost_state:
                        entity.change_state(global_ghost_state)

        self.tick_accumulator += dt
        while self.tick_accumulator >= self.tick_interval:
            self.pac_man.update()
            self.tick_accumulator -= self.tick_interval

        for entity in self.entity_list:
            previous_maze_pos: vec2 = entity.maze_pos

            entity.move(dt)
            self._sync_maze_pos_from_screen_pos(entity)
            self._snap_entity_to_corridor(entity)

            if isinstance(entity, Ghost) and entity.maze_pos != previous_maze_pos:
                entity.screen_pos = self._maze_to_screen(entity.maze_pos)
                entity.update()

    def _snap_entity_to_corridor(self, entity: Entity) -> None:
        center_x: float
        center_y: float
        center_x, center_y = self._maze_to_screen(entity.maze_pos)

        dx: int
        dy: int
        dx, dy = entity.direction

        if dx != 0:
            entity.screen_pos = (entity.screen_pos[0], center_y)
        elif dy != 0:
            entity.screen_pos = (center_x, entity.screen_pos[1])
        else:
            entity.screen_pos = (center_x, center_y)

    def _sync_maze_pos_from_screen_pos(self, entity: Entity) -> None:
        entity.maze_pos = self._screen_to_maze(entity.screen_pos)

    def _maze_to_screen(self, pos: vec2) -> tuple[float, float]:
        x, y = pos
        step: int = self.display.cell_size + self.display.gap

        screen_x: float = (
            self.display.gap
            + x * step
            + self.display.cell_size / 2
        )
        screen_y: float = (
            self.display.gap
            + y * step
            + self.display.cell_size / 2
        )
        return (screen_x, screen_y)

    def _screen_to_maze(self, pos: tuple[float, float]) -> vec2:
        sx, sy = pos
        step: int = self.display.cell_size + self.display.gap

        mx: int = round(
            (sx - self.display.gap - self.display.cell_size / 2) / step
        )
        my: int = round(
            (sy - self.display.gap - self.display.cell_size / 2) / step
        )

        mx = max(0, min(mx, self.maze.width - 1))
        my = max(0, min(my, self.maze.height - 1))

        return (mx, my)

    def _handle_input(self) -> None:
        next_direction: vec2 | None = None

        if (
            raylib.is_key_down(raylib.KEY_UP)
            or raylib.is_key_down(raylib.KEY_W)
            or raylib.is_key_down(raylib.KEY_Z)
            or raylib.is_key_down(raylib.KEY_K)
        ):
            next_direction = Maze.Direction.TOP.value
        elif (
            raylib.is_key_down(raylib.KEY_RIGHT)
            or raylib.is_key_down(raylib.KEY_D)
            or raylib.is_key_down(raylib.KEY_L)
        ):
            next_direction = Maze.Direction.RIGHT.value
        elif (
            raylib.is_key_down(raylib.KEY_DOWN)
            or raylib.is_key_down(raylib.KEY_S)
            or raylib.is_key_down(raylib.KEY_J)
        ):
            next_direction = Maze.Direction.BOT.value
        elif (
            raylib.is_key_down(raylib.KEY_LEFT)
            or raylib.is_key_down(raylib.KEY_A)
            or raylib.is_key_down(raylib.KEY_Q)
            or raylib.is_key_down(raylib.KEY_H)
        ):
            next_direction = Maze.Direction.LEFT.value

        if next_direction is not None:
            self.pac_man.next_direction = next_direction
