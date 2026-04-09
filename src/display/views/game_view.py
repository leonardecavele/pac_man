import pyray as rl
from enum import Enum, auto

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
from src.display.components import Button
from src.parsing import Config

from .view import View, ViewEvent, ViewEventType


class State(Enum):
    RUNNING = auto()
    PAUSE = auto()


class GameView(View):
    def __init__(
        self,
        maze: Maze,
        config: Config,
        textures: dict[str, rl.Texture2D],
        width: int = 720,
        height: int = 720,
    ) -> None:
        self.gamestate = State.RUNNING
        self.maze = maze
        self.config = config
        self.textures = textures
        self.width = width
        self.height = height
        self.geometry = GameGeometry(
            width=width, height=height, maze=maze)
        self.state = GameState(
            maze=maze,
            config=config,
            textures=textures,
            geometry=self.geometry
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
        self.pause_btns = [
            Button(0, 0, "RESUME", self.font_size, lambda: None),
            Button(0, 0, "QUIT", self.font_size, lambda: None),
        ]
        self._set_pause_btn_positions()

    def draw(self) -> None:
        self._draw_running()
        if (self.gamestate == State.PAUSE):
            self._draw_pause()

    def _set_pause_btn_positions(self) -> None:
        menu_height = self.height // 10 * 7
        menu_top = self.height // 2 - menu_height // 2
        for btn in self.pause_btns:
            btn.font_size = self.font_size
            btn.w = rl.measure_text(btn.label, self.font_size)
            btn.h = self.font_size
        self.pause_btns[0].x = self.width // 2 - self.pause_btns[0].w // 2
        self.pause_btns[0].y = menu_top + menu_height * 55 // 100
        self.pause_btns[1].x = self.width // 2 - self.pause_btns[1].w // 2
        self.pause_btns[1].y = menu_top + menu_height * 70 // 100

    def _draw_pause(self) -> None:
        menu_width = self.width // 3
        menu_height = self.height // 10 * 7
        rl.draw_rectangle(self.width // 2 - menu_width // 2,
                          self.height // 2 - menu_height // 2,
                          menu_width, menu_height, rl.BLACK)
        rl.draw_text("PAUSE", menu_width + menu_width // 2 -
                     rl.measure_text("PAUSE", self.font_size) // 2,
                     menu_height // 10 * 3, self.font_size, rl.WHITE)
        for btn in self.pause_btns:
            btn.draw()

    def _draw_running(self) -> None:
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
        if (self.gamestate == State.RUNNING):
            return (self._update_running(dt))
        elif (self.gamestate == State.PAUSE):
            return (self._update_pause(dt))
        return ViewEvent(type=ViewEventType.NONE)

    def _update_pause(self, dt: float) -> ViewEvent:
        if (rl.is_key_pressed(rl.KEY_ESCAPE)):
            self.gamestate = State.RUNNING
            return ViewEvent(type=ViewEventType.NONE)
        if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
            mouse = rl.get_mouse_position()
            if self.pause_btns[0].contains(mouse.x, mouse.y):
                self.gamestate = State.RUNNING
            elif self.pause_btns[1].contains(mouse.x, mouse.y):
                return ViewEvent(type=ViewEventType.CHANGE_VIEW, message="main_menu")
        return ViewEvent(type=ViewEventType.NONE)

    def _update_running(self, dt: float) -> ViewEvent:
        if (rl.is_key_pressed(rl.KEY_ESCAPE)):
            self.gamestate = State.PAUSE
            return ViewEvent(type=ViewEventType.NONE)
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
        self.width = rl.get_screen_width()
        self.height = rl.get_screen_height()
        self.geometry = GameGeometry(
            width=self.width, height=self.height, maze=self.maze)
        self.state.resize(self.geometry)
        self.maze_pixel_w = (self.state.maze.width *
                             (self.geometry.cell_size + self.geometry.gap)
                             + self.geometry.gap)
        self.maze_pixel_h = (self.state.maze.height
                             * (self.geometry.cell_size + self.geometry.gap)
                             + self.geometry.gap)
        self.margin = (self.width // 2 - self.maze_pixel_w // 2,
                       self.height // 2 - self.maze_pixel_h // 2)
        self.font_size = self.margin[1] // 2
        self.maze_image = rl.gen_image_color(
            self.width - 50, self.height - 50, rl.BLACK)
        MazeRenderer(self.maze_image, self.state.maze,
                     self.geometry.cell_size, self.geometry.gap)
        self.maze_texture = rl.load_texture_from_image(self.maze_image)
        self._set_pause_btn_positions()
