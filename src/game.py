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

        center: vec2 = (self.maze.width // 2, self.maze.height // 2)

        top_pos: vec2 = (self.maze.width // 2, 0)
        bottom_pos: vec2 = (self.maze.width // 2, self.maze.height - 1)
        left_pos: vec2 = (0, self.maze.height // 2)
        right_pos: vec2 = (self.maze.width - 1, self.maze.height // 2)

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

    def run(self) -> None:
        while not self.display.should_close():
            dt: float = self.display.get_frame_time()
            self.update(dt)
            self.display.draw(self.entity_list)

        self.display.close()

    def update(self, dt: float) -> None:
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

        for entity in self.entity_list:
            self._move_entity(entity, dt)
            self._sync_maze_pos_from_screen_pos(entity)

        for entity in self.entity_list[:-1]:
            entity.update()

        self.tick_accumulator += dt
        while self.tick_accumulator >= self.tick_interval:
            self.pac_man.update()
            self.tick_accumulator -= self.tick_interval

    def _move_entity(self, entity: Entity, dt: float) -> None:
        sx, sy = entity.screen_pos
        dx, dy = entity.direction

        entity.screen_pos = (
            sx + dx * entity.velocity * dt,
            sy + dy * entity.velocity * dt,
        )

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
