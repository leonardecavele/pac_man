import pyray as rl

from src.gameplay import (
    GameActionType,
    GameController,
    GameGeometry,
    GameInputReader,
    GameState
)
from src.entity import Collectible
from src.display import MazeRenderer
from src.maze import Maze
from src.parsing import Config

from .view import View, ViewEvent, ViewEventType


class GameView(View):
    def __init__(
        self,
        maze: Maze,
        config: Config,
        textures: dict[str, rl.Texture2D],
        width: int = 720,
        height: int = 720,
    ) -> None:
        self.textures = textures
        self.width = width
        self.height = height
        self.geometry = GameGeometry(
            width=width, height=height, maze=maze)
        self.state = GameState(
            maze=maze,
            config=config,
            textures=textures,
            geometry=self.geometry,
            cell_size=self.geometry.cell_size
        )
        self.maze_pixel_w = (self.state.maze.width *
                             (self.geometry.cell_size + self.geometry.gap)
                             + self.geometry.gap)
        self.maze_pixel_h = (self.state.maze.height
                             * (self.geometry.cell_size + self.geometry.gap)
                             + self.geometry.gap)
        self.margin = (self.width // 2 - self.maze_pixel_w // 2,
                       self.height // 2 - self.maze_pixel_h // 2)
        self.font_size = self.margin[1] // 2
        self.controller = GameController()
        self.input_reader = GameInputReader()
        self.maze_image = rl.gen_image_color(
            self.width - 50, self.height - 50, rl.BLACK)
        MazeRenderer(self.maze_image, self.state.maze,
                     self.geometry.cell_size, self.geometry.gap)
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)
        rl.draw_texture(self.maze_texture, self.margin[0], self.margin[1],
                        rl.WHITE)

        for collectible in self.state.collectibles:
            self._draw_collectible(collectible)
        for ghost in self.state.ghosts:
            self._draw_entity(ghost, ghost.sprite)
        self._draw_entity(self.state.pac_man, self.state.pac_man.sprite)
        rl.draw_text(
            str(self.state.score),
            self.margin[0] + self.maze_pixel_w // 10,
            self.margin[1] - self.font_size - 5,
            self.font_size, rl.WHITE)
        rl.draw_text(
            str(self.state.config.level_max_time - int(self.state.timer)),
            self.margin[0] + self.maze_pixel_w // 10 * 9,
            self.margin[1] - self.font_size - 5,
            self.font_size, rl.WHITE)
        src = rl.Rectangle(0, 0, 32, 32)
        for i in range(self.state.HP):
            dst = rl.Rectangle(self.margin[0] + self.maze_pixel_w // 20
                               + i * self.geometry.cell_size,
                               self.margin[1] + self.maze_pixel_h + 5,
                               self.geometry.cell_size, self.geometry.cell_size)
            rl.draw_texture_pro(
                self.textures["pac_man"]["left"][1],
                src,
                dst,
                rl.Vector2(0, 0),
                0.0,
                rl.WHITE
            )

    def update(self, dt: float) -> ViewEvent:
        action = self.controller.update(
            self.state, dt, self.input_reader.read())

        if action.type == GameActionType.VICTORY:
            return ViewEvent(
                type=ViewEventType.END, message=f"victory:{action.score}"
            )
        if action.type == GameActionType.GAME_OVER:
            return ViewEvent(
                type=ViewEventType.END, message=f"game_over:{action.score}"
            )
        if action.type == GameActionType.GAME_OVER:
            return ViewEvent(
                type=ViewEventType.END, message=f"game_over:{action.score}"
            )
        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        rl.unload_texture(self.maze_texture)
        rl.unload_image(self.maze_image)

    def _draw_collectible(self, collectible: Collectible) -> None:
        if not collectible.visible:
            return
        self._draw_entity(collectible, collectible.sprite)

    def _draw_entity(self, entity, sprite: rl.Texture2D) -> None:
        x, y = self.geometry.get_draw_pos(entity.screen_pos)
        x += self.margin[0]
        y += self.margin[1]

        source = rl.Rectangle(0, 0, sprite.width, sprite.height)
        dest = rl.Rectangle(x, y, self.geometry.cell_size -
                            1, self.geometry.cell_size - 1)

        rl.draw_texture_pro(
            sprite,
            source,
            dest,
            rl.Vector2(0, 0),
            0.0,
            rl.WHITE,
        )

    def resize(self) -> None:
        return
