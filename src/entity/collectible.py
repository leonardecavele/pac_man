from typing import TYPE_CHECKING
import pyray as rl

from .entity import Entity

from src.maze import Maze
from src.type import vec2i, vec2f
from typing import cast

if TYPE_CHECKING:
    from src.gameplay import MazeState


class Collectible(Entity):
    """A static item that Pac-Man can collect to earn points."""

    def __init__(
        self,
        screen_pos: vec2f,
        maze_pos: vec2f,
        sprite: rl.Texture,
        maze: Maze,
        points: int,
        default_velocity_px: int = 0
    ) -> None:
        """
        Initialize the collectible.

        screen_pos          -- pixel position on screen
        maze_pos            -- sub-cell position in the maze grid (floats for mid-cell items)
        sprite              -- texture to render
        maze                -- reference to the game maze
        points              -- score awarded on collection
        default_velocity_px -- velocity (always 0 for collectibles)
        """
        super().__init__(
            screen_pos,
            cast(vec2i, (int(maze_pos[0]), int(maze_pos[1]))),
            sprite, maze, default_velocity_px
        )
        self.maze_pos: vec2f = maze_pos  # type: ignore[assignment]
        self.points = points
        self.visible: bool = True

    def update(self, dt: float = 0.0) -> None:
        """No-op; collectibles are static and do not change state on their own."""
        return

    def on_collect(self, state: "MazeState") -> None:
        """Add this collectible's point value to the game score."""
        state.score += self.points


class Pacgum(Collectible):
    """A standard dot that Pac-Man eats to score points."""

    def update(self, dt: float = 0.0) -> None:
        """Ensure the pacgum is always visible."""
        self.visible = True


class SuperPacgum(Collectible):
    """A large blinking dot that triggers ghost fright mode when eaten."""

    def __init__(
        self,
        screen_pos: vec2f,
        maze_pos: vec2f,
        sprite: rl.Texture,
        maze: Maze,
        points: int,
        default_velocity_px: int = 0
    ) -> None:
        """Initialize the super pacgum with blinking animation state."""
        super().__init__(screen_pos, maze_pos, sprite, maze, points,
                         default_velocity_px)
        self.blink_interval: float = 0.15
        self._elapsed: float = 0.0

    def update(self, dt: float = 0.0) -> None:
        """Toggle visibility on each blink interval to create a flashing effect."""
        self._elapsed += dt
        if self._elapsed < self.blink_interval:
            return
        self.visible = not self.visible
        self._elapsed = 0.0

    def on_collect(self, state: "MazeState") -> None:
        """Award points and activate fright mode for all active ghosts."""
        super().on_collect(state)
        state.start_fright_mode()
