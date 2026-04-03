from typing import TYPE_CHECKING

import pyray as rl

from src.entity import (
    Blinky, Clyde, Collectible, Ghost, Inky, Pac_man, Pacgum, Pinky, SuperPacgum
)
from src.maze import Maze
from src.parsing.config import Config
from src.type import vec2i

if TYPE_CHECKING:
    from .maze_geometry import MazeGeometry

DEFAULT_VELOCITY_CELLS: int = 6


class MazeState:
    def __init__(
        self,
        maze: Maze,
        config: Config,
        textures: dict[str, rl.Texture2D],
        geometry: "MazeGeometry",
        cell_size: int
    ) -> None:
        self.maze = maze
        self.config = config
        self.textures = textures
        self.geometry = geometry
        self.fright_duration: float = 6.0
        self.default_velocity_px: int = DEFAULT_VELOCITY_CELLS * cell_size
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
        self.ghost_release_schedule: dict[str, float] = {
            "blinky": 0.0,
            "pinky": 2.0,
            "inky": 4.0,
            "clyde": 6.0,
        }
        self.reset()

    def reset(self) -> None:
        self.score: int = 0
        self.timer: float = 0.0
        self.fright: bool = False
        self.fright_time: float = 0.0
        self.ghost_schedule_time: float = 0.0
        self.current_ghost_mode: Ghost.State = Ghost.State.SCATTER

        center: vec2i = (self.maze.width // 2, self.maze.height // 2)
        house_exit: vec2i = (center[0], max(0, center[1] - 1))
        pac_man_start: vec2i = (self.maze.width // 2, self.maze.height - 2)

        if self.maze.og:
            blinky_spawn: vec2i = center
            pinky_spawn: vec2i = (max(0, center[0] - 1), house_exit[1])
            inky_spawn: vec2i = (
                min(self.maze.width - 1, center[0] + 1), house_exit[1]
            )
            clyde_spawn: vec2i = (
                center[0], min(self.maze.height - 1, center[1] + 1)
            )
        else:
            blinky_spawn = (self.maze.width - 1, 0)
            pinky_spawn = (0, 0)
            inky_spawn = (self.maze.width - 1, self.maze.height - 1)
            clyde_spawn = (0, self.maze.height - 1)

        self.pac_man = Pac_man(
            screen_pos=self.geometry.maze_to_screen(pac_man_start),
            maze_pos=pac_man_start,
            sprite=self.textures["pac_man"],
            m=self.maze,
            default_velocity_px=self.default_velocity_px
        )

        blinky = Blinky(
            screen_pos=self.geometry.maze_to_screen(blinky_spawn),
            maze_pos=blinky_spawn,
            sprite=self.textures["blinky"],
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
            default_velocity_px=self.default_velocity_px
        )

        inky = Inky(
            screen_pos=self.geometry.maze_to_screen(inky_spawn),
            maze_pos=inky_spawn,
            sprite=self.textures["inky"],
            m=self.maze,
            pac_man=self.pac_man,
            blinky=blinky,
            house_pos=center,
            default_velocity_px=self.default_velocity_px
        )

        pinky = Pinky(
            screen_pos=self.geometry.maze_to_screen(pinky_spawn),
            maze_pos=pinky_spawn,
            sprite=self.textures["pinky"],
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
            default_velocity_px=self.default_velocity_px
        )

        clyde = Clyde(
            screen_pos=self.geometry.maze_to_screen(clyde_spawn),
            maze_pos=clyde_spawn,
            sprite=self.textures["clyde"],
            m=self.maze,
            pac_man=self.pac_man,
            house_pos=center,
            default_velocity_px=self.default_velocity_px
        )

        self.ghosts: list[Ghost] = [blinky, inky, pinky, clyde]
        self.collectibles: list[Collectible] = self._gen_collectibles()
        self.initial_collectible_count: int = len(self.collectibles)

        for ghost in self.ghosts:
            ghost.house_exit = ghost.corner
            ghost.released = False
            ghost.exiting_house = False
            ghost.direction = (0, 0)
            ghost.change_state(self.current_ghost_mode)
            ghost.update()

    def _gen_collectibles(self) -> list[Collectible]:
        pacgums: list[Collectible] = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.maze[y][x].value == 15:
                    continue
                common_args = {
                    "screen_pos": self.geometry.maze_to_screen((x, y)),
                    "maze_pos": (x, y),
                    "maze": self.maze,
                }
                if self._is_corner((x, y)):
                    pacgums.append(
                        SuperPacgum(
                            sprite=self.textures["super_pacgum"],
                            points=self.config.points_per_super_pacgum,
                            **common_args,
                        )
                    )
                    continue
                pacgums.append(
                    Pacgum(
                        sprite=self.textures["pacgum"],
                        points=self.config.points_per_pacgum,
                        **common_args,
                    )
                )
        return pacgums

    def _is_corner(self, pos: vec2i) -> bool:
        x, y = pos
        return (
            (x == 0 and y == 0)
            or (x == 0 and y == self.maze.height - 1)
            or (x == self.maze.width - 1 and y == 0)
            or (x == self.maze.width - 1 and y == self.maze.height - 1)
        )

    def start_fright_mode(self) -> None:
        self.fright = True
        self.fright_time = 0.0

        for ghost in self.ghosts:
            if ghost.state == Ghost.State.EATEN:
                continue

            if ghost.state != Ghost.State.FRIGHTENED:
                ghost.save_state()

            ghost.change_state(Ghost.State.FRIGHTENED)
            ghost.update()

    def end_fright_mode(self) -> None:
        self.fright = False
        self.fright_time = 0.0
        for ghost in self.ghosts:
            if ghost.state == Ghost.State.FRIGHTENED:
                ghost.load_save()
                ghost.update()

    def collectible_ratio_remaining(self) -> float:
        if self.initial_collectible_count == 0:
            return 0.0
        return len(self.collectibles) / self.initial_collectible_count
