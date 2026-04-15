from typing import TYPE_CHECKING, cast

import pyray as rl

from src.entity import (
    Blinky, Clyde, Collectible, Ghost, Inky,
    Pac_man, Pacgum, Pinky, SuperPacgum
)
from src.maze import Maze
from src.parsing import Config
from src.type import vec2i, Direction
from src.sounds import Sounds

if TYPE_CHECKING:
    from .helper import GameGeometry

DEFAULT_VELOCITY_CELLS: int = 6


class GameState:
    """Hold all mutable data that describes the current state of a game session."""

    def __init__(
        self,
        maze: Maze,
        config: Config,
        textures: dict[str, dict[str, list[rl.Texture]] |
                       list[rl.Texture]],
        sounds: Sounds,
        geometry: "GameGeometry"
    ) -> None:
        """
        Initialize a new game session.

        maze     -- the maze layout for this session
        config   -- validated game configuration (lives, points, time limit)
        textures -- full texture atlas shared by all entities
        sounds   -- sound manager
        geometry -- pre-computed pixel geometry for the current viewport
        """
        self.maze = maze
        self.config = config
        self.textures = textures
        self.level = 1
        self.game_over: bool = False
        self.game_win: bool = False
        self.sounds = sounds
        self.geometry = geometry
        self.freeze_time: float = 0.0
        self.start_time: float = 0.01
        self.music_hide: float = 4.0
        self.show_ghost_path: bool = False
        self.last_pacgum_eat_time: float = 0.0
        self.fright_duration: float = 6.0
        self.default_velocity_px: int = DEFAULT_VELOCITY_CELLS * \
            self.geometry.cell_size
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
        if maze.og:
            self.ghost_release_schedule: dict[str, float] = {
                "blinky": 0.0,
                "pinky": 2.0,
                "inky": 4.0,
                "clyde": 6.0,
            }
        else:
            self.ghost_release_schedule = {
                "blinky": 0.0,
                "pinky": 0.0,
                "inky": 0.0,
                "clyde": 0.0,
            }
        self.global_reset()
        self.collectible_reset()
        self.entity_reset()

        self.sounds.play_sound("start_music")

    def global_reset(self) -> None:
        """Reset lives, score, timer, and the music-hide counter to initial values."""
        self.HP = self.config.lives
        self.score: int = 0
        self.timer: float = 0.0
        self.music_hide = 4.0

    def collectible_reset(self) -> None:
        """Regenerate all collectibles and record the initial count."""
        self.collectibles: list[Collectible] = self._gen_collectibles()
        self.initial_collectible_count: int = len(self.collectibles)

    def entity_reset(self) -> None:
        """Respawn Pac-Man and all ghosts at their starting positions and states."""
        self.fright: bool = False
        self.fright_time: float = 0.0
        self.ghost_schedule_time: float = 0.0
        self.current_ghost_mode: Ghost.State = Ghost.State.SCATTER

        center: vec2i = (self.maze.width // 2, self.maze.height // 2)

        if self.maze.og:
            self.pac_man_spawn: vec2i = (center[0], 7)
            house_exit: vec2i = (center[0], 3)
            blinky_spawn: vec2i = house_exit
            inky_spawn: vec2i = (max(0, center[0] - 1), house_exit[1] + 1)
            clyde_spawn: vec2i = (
                min(self.maze.width - 1, center[0] + 1), house_exit[1] + 1
            )
            pinky_spawn: vec2i = (center[0], house_exit[1] + 1)
        else:
            self.pac_man_spawn = center
            blinky_spawn = (self.maze.width - 1, 0)
            pinky_spawn = (0, 0)
            inky_spawn = (self.maze.width - 1, self.maze.height - 1)
            clyde_spawn = (0, self.maze.height - 1)

        _tex = cast(dict[str, list[rl.Texture]], self.textures["pac_man"])
        self.pac_man = Pac_man(
            screen_pos=self.geometry.maze_to_screen(self.pac_man_spawn),
            maze_pos=self.pac_man_spawn,
            sprite=_tex["dying"][0],
            m=self.maze,
            default_velocity_px=self.default_velocity_px,
            textures=self.textures
        )

        def _gtex(name: str) -> dict[str, list[rl.Texture]]:
            return cast(dict[str, list[rl.Texture]], self.textures[name])

        if self.maze.og:
            blinky_sprite = _gtex("blinky")["left"][0]
            inky_sprite = _gtex("inky")["up"][0]
            pinky_sprite = _gtex("pinky")["down"][0]
            clyde_sprite = _gtex("clyde")["up"][0]
        else:
            blinky_sprite = _gtex("blinky")["down"][0]
            inky_sprite = _gtex("inky")["left"][0]
            pinky_sprite = _gtex("pinky")["right"][0]
            clyde_sprite = _gtex("clyde")["up"][0]

        blinky = Blinky(
            screen_pos=self.geometry.maze_to_screen(blinky_spawn),
            maze_pos=blinky_spawn,
            sprite=blinky_sprite,
            m=self.maze,
            pac_man=self.pac_man,
            textures=self.textures,
            house_pos=blinky_spawn,
            default_velocity_px=self.default_velocity_px
        )

        inky = Inky(
            screen_pos=self.geometry.maze_to_screen(inky_spawn),
            maze_pos=inky_spawn,
            sprite=inky_sprite,
            m=self.maze,
            pac_man=self.pac_man,
            blinky=blinky,
            textures=self.textures,
            house_pos=inky_spawn,
            default_velocity_px=self.default_velocity_px
        )

        pinky = Pinky(
            screen_pos=self.geometry.maze_to_screen(pinky_spawn),
            maze_pos=pinky_spawn,
            sprite=pinky_sprite,
            m=self.maze,
            pac_man=self.pac_man,
            textures=self.textures,
            house_pos=pinky_spawn,
            default_velocity_px=self.default_velocity_px
        )

        clyde = Clyde(
            screen_pos=self.geometry.maze_to_screen(clyde_spawn),
            maze_pos=clyde_spawn,
            sprite=clyde_sprite,
            m=self.maze,
            pac_man=self.pac_man,
            textures=self.textures,
            house_pos=clyde_spawn,
            default_velocity_px=self.default_velocity_px
        )

        if self.maze.og:
            blinky.direction = Direction.LEFT.value
            inky.direction = Direction.TOP.value
            pinky.direction = Direction.BOT.value
            clyde.direction = Direction.TOP.value
        else:
            blinky.direction = Direction.BOT.value
            inky.direction = Direction.LEFT.value
            pinky.direction = Direction.RIGHT.value
            clyde.direction = Direction.TOP.value

        self.ghosts: list[Ghost] = [blinky, inky, pinky, clyde]

        for ghost in self.ghosts:
            if self.maze.og:
                ghost.house_exit = house_exit
                ghost.released = False
                ghost.exiting_house = False
            else:
                ghost.house_exit = ghost.house
                ghost.released = True
                ghost.exiting_house = False

            ghost.change_state(self.current_ghost_mode)
            ghost.flip = False
            ghost.origin_cell = None
            ghost.target_cell = None

        if self.maze.og:
            blinky.released = True
            blinky.exiting_house = False
            blinky.direction = Direction.LEFT.value
            blinky.origin_cell = blinky.maze_pos
            blinky.target_cell = (blinky.maze_pos[0] - 1, blinky.maze_pos[1])

    def _gen_collectibles(self) -> list[Collectible]:
        """Generate and return all pacgums and super-pacgums for the current maze."""
        pacgums: list[Collectible] = []
        for y in range(self.maze.height):
            if (y != 9):
                continue
            for x in range(self.maze.width):
                if self.maze.maze[y][x].value == 15:
                    continue
                if self.maze.og:
                    if (
                        (x, y) == (7, 4)
                        or (x, y) == (8, 4)
                        or (x, y) == (9, 4)
                    ):
                        continue

                scr = self.geometry.maze_to_screen((x, y))
                if self._is_corner((x, y)):
                    pacgums.append(
                        SuperPacgum(
                            screen_pos=scr,
                            maze_pos=(float(x), float(y)),
                            maze=self.maze,
                            sprite=cast(
                                list[rl.Texture],
                                self.textures["super_pacgum"]
                            )[0],
                            points=self.config.points_per_super_pacgum,
                        )
                    )
                    continue
                pacgums.append(
                    Pacgum(
                        screen_pos=scr,
                        maze_pos=(float(x), float(y)),
                        maze=self.maze,
                        sprite=cast(
                            list[rl.Texture], self.textures["pacgum"]
                        )[0],
                        points=self.config.points_per_pacgum,
                    )
                )
                self._put_mid_pacgums(x, y, pacgums)
        return pacgums

    def _no_pacgum(self, x: float, y: float,
                   pacgums: list[Collectible]) -> bool:
        """Return True if no collectible already occupies position (x, y)."""
        for i in pacgums:
            if (i.maze_pos[0] == x and i.maze_pos[1] == y):
                return (False)
        return (True)

    def _put_mid_pacgums(self, x: int, y: int,
                         pacgums: list[Collectible]) -> None:
        """Add mid-cell pacgums on each open side of cell (x, y) if not already present."""
        cell = self.maze.maze[y][x]
        if (not cell.top and self._no_pacgum(x, y - .5, pacgums)):
            pacgums.append(Pacgum(
                sprite=cast(list[rl.Texture], self.textures["pacgum"])[0],
                points=self.config.points_per_pacgum,
                maze=self.maze,
                maze_pos=(x, y - .5),
                screen_pos=self.geometry.maze_to_screen((x, y - .5))
            ))
        if (not cell.bot and self._no_pacgum(x, y + .5, pacgums)):
            pacgums.append(Pacgum(
                sprite=cast(list[rl.Texture], self.textures["pacgum"])[0],
                points=self.config.points_per_pacgum,
                maze=self.maze,
                maze_pos=(x, y + .5),
                screen_pos=self.geometry.maze_to_screen((x, y + .5))
            ))
        if (not cell.left and self._no_pacgum(x - .5, y, pacgums)):
            pacgums.append(Pacgum(
                sprite=cast(list[rl.Texture], self.textures["pacgum"])[0],
                points=self.config.points_per_pacgum,
                maze=self.maze,
                maze_pos=(x - .5, y),
                screen_pos=self.geometry.maze_to_screen((x - .5, y))
            ))
        if (not cell.right and self._no_pacgum(x + .5, y, pacgums)):
            pacgums.append(Pacgum(
                sprite=cast(list[rl.Texture], self.textures["pacgum"])[0],
                points=self.config.points_per_pacgum,
                maze=self.maze,
                maze_pos=(x + .5, y),
                screen_pos=self.geometry.maze_to_screen((x + .5, y))
            ))

    def _is_corner(self, pos: vec2i) -> bool:
        """Return True if pos is one of the four corners of the maze."""
        x, y = pos
        return (
            (x == 0 and y == 0)
            or (x == 0 and y == self.maze.height - 1)
            or (x == self.maze.width - 1 and y == 0)
            or (x == self.maze.width - 1 and y == self.maze.height - 1)
        )

    def start_fright_mode(self) -> None:
        """Activate fright mode: save ghost states and switch all non-eaten ghosts to FRIGHTENED."""
        self.fright = True
        self.fright_time = 0.0

        for ghost in self.ghosts:
            if ghost.state == Ghost.State.EATEN:
                continue

            if not ghost.state & (Ghost.State.FRIGHTENED | Ghost.State.BLINK):
                ghost.save_state()

            ghost.change_state(Ghost.State.FRIGHTENED)
            ghost.update()

    def blink_fright_mode(self) -> None:
        """Transition all frightened ghosts to the blinking BLINK state."""
        for ghost in self.ghosts:
            if ghost.state & Ghost.State.FRIGHTENED:
                ghost.change_state(Ghost.State.BLINK)

    def end_fright_mode(self) -> None:
        """End fright mode and restore all frightened/blinking ghosts to their saved states."""
        self.fright = False
        self.fright_time = 0.0
        for ghost in self.ghosts:
            if ghost.state & (Ghost.State.FRIGHTENED | Ghost.State.BLINK):
                ghost.load_save()
                ghost.update()

    def freeze(self, duration: float) -> None:
        """Pause all entity updates for duration seconds."""
        self.freeze_time = duration

    def collectible_ratio_remaining(self) -> float:
        """Return the fraction of collectibles still on the board (0.0 to 1.0)."""
        if self.initial_collectible_count == 0:
            return 0.0
        return len(self.collectibles) / self.initial_collectible_count

    def resize(self, geometry: "GameGeometry") -> None:
        """Update geometry and recalculate all entity screen positions and velocities."""
        self.geometry = geometry
        self.default_velocity_px = DEFAULT_VELOCITY_CELLS * \
            self.geometry.cell_size
        for c in self.collectibles + self.ghosts + [self.pac_man]:
            c.screen_pos = self.geometry.maze_to_screen(c.maze_pos)
            c.default_velocity_px = self.default_velocity_px
            if (isinstance(c, Ghost)):
                c.update_velocity(c.state)
        self.pac_man.velocity_px = int(self.pac_man.default_velocity_px * .8)
