import math

import pyray as rl

from src.display.maze_renderer import MazeRenderer
from src.entity import Collectible, Ghost
from src.gameplay.maze_geometry import MazeGeometry
from src.gameplay.maze_state import MazeState


class MazeSceneRenderer:
    def __init__(
        self,
        maze_state: MazeState,
        geometry: MazeGeometry,
        width: int,
        height: int,
    ) -> None:
        self.state = maze_state
        self.geometry = geometry
        self.width = width
        self.height = height
        self.maze_image = rl.gen_image_color(self.width, self.height, rl.BLACK)
        MazeRenderer(self.maze_image, self.state.maze, self.geometry.cell_size, self.geometry.gap)
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)
        rl.draw_texture(self.maze_texture, 0, 0, rl.WHITE)

        for collectible in self.state.collectibles:
            self._draw_collectible(collectible)
        for ghost in self.state.ghosts:
            self._draw_entity(ghost, self._ghost_sprite(ghost))
        self._draw_entity(self.state.pac_man, self.state.pac_man.sprite)

        rl.draw_text(
            f"Score: {self.state.score} - Timer: {math.floor(self.state.timer)}",
            self.geometry.gap,
            (self.state.maze.height + 1) * (self.geometry.cell_size + self.geometry.gap),
            30,
            rl.WHITE,
        )

    def close(self) -> None:
        rl.unload_texture(self.maze_texture)
        rl.unload_image(self.maze_image)

    def _draw_collectible(self, collectible: Collectible) -> None:
        if not collectible.visible:
            return
        self._draw_entity(collectible, collectible.sprite)

    def _draw_entity(self, entity, sprite: rl.Texture2D) -> None:
        x, y = self.geometry.get_draw_pos(entity.screen_pos)
        rl.draw_texture(sprite, x, y, rl.WHITE)

    def _ghost_sprite(self, ghost: Ghost) -> rl.Texture2D:
        return ghost.sprite
