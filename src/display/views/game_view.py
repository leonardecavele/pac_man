import pyray as rl
from enum import Enum, auto
from typing import cast

from src.gameplay import (
    GameActionType,
    GameController,
    GameGeometry,
    GameInputReader,
    GameState
)
from src.entity import Collectible, Entity, Ghost
from src.display import MazeRenderer
from src.maze import Maze
from src.display.components import Button
from src.parsing import Config
from src.display.maze_renderer import WALL_COLOR
from src.sounds import Sounds

from .view import View, ViewEvent, ViewEventType


CHEAT_MODE_COMB = [263, 262, 263, 262, 265, 265, 265, 257]


class State(Enum):
    RUNNING = auto()
    PAUSE = auto()


class GameView(View):
    def __init__(
        self,
        maze: Maze,
        config: Config,
        textures: dict[str, dict[str, list[rl.Texture]] | list[rl.Texture]],
        sounds: Sounds,
        width: int = 720,
        height: int = 720,
    ) -> None:
        self.gamestate = State.RUNNING
        self.maze = maze
        self.config = config
        self.textures = textures
        self.sounds = sounds
        self.width = width
        self.height = height
        self.geometry = GameGeometry(
            width=width, height=height, maze=maze
        )
        self.state = GameState(
            maze=maze,
            config=config,
            textures=textures,
            sounds=self.sounds,
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
        self.controller = GameController(self.sounds)
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
        self.cheat_btns = [
            Button(0, 0, "ADD 1 LIVE", self.font_size,
                   lambda: setattr(self.state, 'HP', self.state.HP + 1)),
            Button(0, 0, "REMOVE 1 LIVE", self.font_size,
                   lambda: setattr(self.state, 'HP', self.state.HP - 1)),
            Button(0, 0, "RESET TIMER", self.font_size,
                   lambda: setattr(self.state, 'timer', 0)),
            Button(
                0, 0, "SHOW GHOSTS TARGETS", self.font_size,
                lambda: setattr(
                    self.state, 'show_ghost_path',
                    not self.state.show_ghost_path
                )
            ),
            Button(0, 0, "CHEAT OFF", self.font_size,
                   lambda: setattr(self, 'cheat_mode', False)),
        ]
        self._set_cheat_btn_positions()
        self.timer = 1.0
        self.comb_idx = 0
        self.cheat_mode = False
        self.game_over_timer = 0.0
        self.game_over_delay = 2.0
        self.win_timer = 0.0
        self.win_delay = 2.0

    def draw(self) -> None:
        self._draw_running()
        if (self.gamestate == State.PAUSE):
            self._draw_pause()

    def _set_cheat_btn_positions(self) -> None:
        menu_width = self.width // 4
        margin = (self.width // 3 - menu_width) // 2
        menu_height = self.height // 10 * 7
        menu_top = self.height // 2 - menu_height // 2
        for btn in self.cheat_btns:
            btn.font_size = self.font_size
            btn.w = rl.measure_text(btn.label, self.font_size)
            btn.h = self.font_size
        gap = self.font_size // 2
        main_btns = self.cheat_btns[:-1]
        last_btn = self.cheat_btns[-1]
        total_h = len(main_btns) * self.font_size + (len(main_btns) - 1) * gap
        start_y = menu_top + (menu_height - total_h) // 2
        for i, btn in enumerate(main_btns):
            btn.x = margin + menu_width // 2 - btn.w // 2
            btn.y = start_y + i * (self.font_size + gap)
        last_btn.x = margin + menu_width // 2 - last_btn.w // 2
        last_btn.y = menu_top + menu_height - self.font_size - gap

    def _set_pause_btn_positions(self) -> None:
        menu_height = self.height // 10 * 7
        menu_top = self.height // 2 - menu_height // 2
        for btn in self.pause_btns:
            btn.font_size = self.font_size
            btn.w = rl.measure_text(btn.label, self.font_size)
            btn.h = self.font_size
        self.pause_btns[0].x = self.width // 2 - self.pause_btns[0].w // 2
        self.pause_btns[0].y = menu_top + menu_height * 50 // 100
        self.pause_btns[1].x = self.width // 2 - self.pause_btns[1].w // 2
        self.pause_btns[1].y = menu_top + menu_height * 65 // 100

    def _draw_pause(self) -> None:
        menu_width = self.width // 3
        menu_height = self.height // 10 * 7
        bg = rl.Rectangle(self.width // 2 - menu_width // 2 - 1,
                          self.height // 2 - menu_height // 2 - 1,
                          menu_width + 2, menu_height + 2)
        rl.draw_rectangle_rounded(bg, .15, 256, rl.Color(0, 0, 0, 200))
        bg = rl.Rectangle(self.width // 2 - menu_width // 2,
                          self.height // 2 - menu_height // 2,
                          menu_width, menu_height)
        rl.draw_rectangle_rounded_lines(bg, .15, 256, WALL_COLOR)
        rl.draw_text("PAUSE", menu_width + menu_width // 2 -
                     rl.measure_text("PAUSE", self.font_size) // 2,
                     menu_height // 10 * 4, self.font_size, rl.WHITE)
        for btn in self.pause_btns:
            btn.draw()
        if (self.cheat_mode):
            self._draw_cheat()

    def _draw_cheat(self) -> None:
        menu_width = self.width // 4
        margin = (self.width // 3 - menu_width) // 2
        menu_height = self.height // 10 * 7
        bg = rl.Rectangle(margin - 1,
                          self.height // 2 - menu_height // 2 - 1,
                          menu_width + 2, menu_height + 2)
        rl.draw_rectangle_rounded(bg, .15, 256, rl.Color(0, 0, 0, 200))
        bg = rl.Rectangle(margin,
                          self.height // 2 - menu_height // 2,
                          menu_width, menu_height)
        rl.draw_rectangle_rounded_lines(bg, .15, 256, WALL_COLOR)
        for btn in self.cheat_btns:
            btn.draw()

    def _draw_running(self) -> None:
        rl.clear_background(rl.BLACK)
        rl.draw_texture(self.maze_texture, self.margin[0], self.margin[1],
                        rl.WHITE)

        if (self.cheat_mode):
            hud_bottom_y = self.margin[1] + self.maze_pixel_h + 5
            hud_padding = self.maze_pixel_w // 20
            cheat_text = "CHEAT ON"
            cheat_x = (
                self.margin[0]
                + self.maze_pixel_w
                - hud_padding
                - rl.measure_text(cheat_text, self.font_size)
            )

            rl.draw_text(
                cheat_text,
                cheat_x,
                hud_bottom_y,
                self.font_size,
                rl.WHITE
            )
        for collectible in self.state.collectibles:
            self._draw_collectible(collectible)

        for ghost in self.state.ghosts:
            if (
                (self.timer > 0.75 or not ghost.state == Ghost.State.EATEN)
                and self.state.music_hide <= 0.0
                and not self.state.game_win
            ):
                self._draw_entity(ghost, ghost.sprite)
        if (self.timer > 0.75):
            self._draw_entity(self.state.pac_man, self.state.pac_man.sprite)
        else:
            x, y = self.geometry.get_draw_pos(self.state.pac_man.screen_pos)
            x += self.margin[0]
            y += self.margin[1]
            rl.draw_text(str(self.state.config.points_per_ghost),
                         x,
                         y,
                         int(self.geometry.cell_size * .75),
                         rl.WHITE)
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
                               self.geometry.cell_size,
                               self.geometry.cell_size)
            _pac = cast(dict[str, list[rl.Texture]], self.textures["pac_man"])
            rl.draw_texture_pro(
                _pac["left"][1], src, dst,
                rl.Vector2(0, 0), 0.0, rl.WHITE
            )

        if self.state.game_over:
            spawn_x, spawn_y = self.geometry.maze_to_screen(
                self.state.pac_man_spawn
            )
            spawn_x += self.margin[0]
            spawn_y += self.margin[1]

            text1 = "GAME"
            text2 = "OVER"

            font_size = int(self.geometry.cell_size * 0.5)
            text1_w = rl.measure_text(text1, font_size)
            text2_w = rl.measure_text(text2, font_size)

            center_x = spawn_x + self.geometry.cell_size
            text_y = int(
                spawn_y + self.geometry.cell_size / 2 - (font_size * 1.5)
            )

            game_x = int(center_x - (self.geometry.cell_size * 1.5) - text1_w)
            over_x = int(center_x + self.geometry.cell_size - text2_w)

            padding_x = 8
            padding_y = 6

            box_x = game_x - padding_x
            box_y = text_y - padding_y
            box_w = (over_x + text2_w) - game_x + padding_x * 2
            box_h = font_size + padding_y * 2

            rl.draw_rectangle(box_x, box_y, box_w, box_h, rl.BLACK)

            rl.draw_text(text1, game_x, text_y, font_size, rl.RED)
            rl.draw_text(text2, over_x, text_y, font_size, rl.RED)

        if (self.state.start_time > 0.0
                or self.sounds.is_playing("start_music")):
            spawn_x, spawn_y = self.geometry.maze_to_screen(
                self.state.pac_man_spawn
            )
            spawn_x += self.margin[0]

            text = "READY!"
            font_size = int(self.geometry.cell_size * 0.5)
            text_w = rl.measure_text(text, font_size)
            text_y = int(spawn_y - self.geometry.cell_size * 1)
            text_x = int(spawn_x - text_w / 2)

            padding_x = 8
            padding_y = 6

            box_x = text_x - padding_x
            box_y = text_y - padding_y
            box_w = text_w + padding_x * 2
            box_h = font_size + padding_y * 2

            rl.draw_rectangle(box_x, box_y, box_w, box_h, rl.BLACK)
            rl.draw_text(text, text_x, text_y, font_size, rl.YELLOW)

        if self.state.game_win:
            spawn_x, spawn_y = self.geometry.maze_to_screen(
                self.state.pac_man_spawn
            )
            spawn_x += self.margin[0]

            text = "NEXT LEVEL!"
            font_size = int(self.geometry.cell_size * 0.5)
            text_w = rl.measure_text(text, font_size)
            text_y = int(spawn_y - self.geometry.cell_size * 1)
            text_x = int(spawn_x - text_w / 2)

            padding_x = 8
            padding_y = 6

            box_x = text_x - padding_x
            box_y = text_y - padding_y
            box_w = text_w + padding_x * 2
            box_h = font_size + padding_y * 2

            rl.draw_rectangle(box_x, box_y, box_w, box_h, rl.BLACK)
            rl.draw_text(text, text_x, text_y, font_size, rl.YELLOW)

    def update(self, dt: float) -> ViewEvent:
        if (self.gamestate == State.RUNNING):
            return (self._update_running(dt))
        elif (self.gamestate == State.PAUSE):
            return (self._update_pause(dt))
        return ViewEvent(type=ViewEventType.NONE)

    def _update_cheat(self, dt: float) -> None:
        mouse = rl.get_mouse_position()
        mx, my = mouse.x, mouse.y
        for btn in self.cheat_btns:
            if (btn.contains(mx, my)):
                if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
                    btn.action()
                else:
                    btn.color = rl.Color(255, 255, 255, 128)
            else:
                btn.color = rl.WHITE

    def _update_pause(self, dt: float) -> ViewEvent:
        if (self.cheat_mode):
            self._update_cheat(dt)
        key = rl.get_key_pressed()
        if (not self.cheat_mode and key == CHEAT_MODE_COMB[self.comb_idx]):
            self.comb_idx += 1
        elif (key != 0):
            self.comb_idx = 0
        if (self.comb_idx >= len(CHEAT_MODE_COMB)):
            self.cheat_mode = True
            self.comb_idx = 0
        if (rl.is_key_pressed(rl.KEY_ESCAPE)):
            self.gamestate = State.RUNNING
            self.sounds.resume_all_sounds()
            return ViewEvent(type=ViewEventType.NONE)
        mouse = rl.get_mouse_position()

        # click
        if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
            if self.pause_btns[0].contains(mouse.x, mouse.y):
                self.gamestate = State.RUNNING
                self.sounds.resume_all_sounds()
            elif self.pause_btns[1].contains(mouse.x, mouse.y):
                return ViewEvent(
                    type=ViewEventType.CHANGE_VIEW, message="main_menu"
                )

        # hover
        if self.pause_btns[0].contains(mouse.x, mouse.y):
            self.pause_btns[0].color = rl.YELLOW
        else:
            self.pause_btns[0].color = rl.WHITE
        if self.pause_btns[1].contains(mouse.x, mouse.y):
            self.pause_btns[1].color = rl.RED
        else:
            self.pause_btns[1].color = rl.WHITE
        return ViewEvent(type=ViewEventType.NONE)

    def _update_running(self, dt: float) -> ViewEvent:
        self.timer += dt

        if self.state.music_hide > 0.0:
            self.state.music_hide -= dt

        if self.state.game_over:
            self.game_over_timer += dt
            if self.game_over_timer >= self.game_over_delay:
                score: int = self.state.score
                self.state.global_reset()
                return ViewEvent(
                    type=ViewEventType.END,
                    message=f"game_over:{score}"
                )
            return ViewEvent(type=ViewEventType.NONE)

        if self.state.game_win:
            self.win_timer += dt
            if self.win_timer >= self.win_delay:
                self.state.entity_reset()
                self.state.collectible_reset()
                self.state.timer = 0.0
                self.state.start_time = 2.0
                self.state.game_win = False
                self.win_timer = 0.0
            return ViewEvent(type=ViewEventType.NONE)

        if (rl.is_key_pressed(rl.KEY_ESCAPE)):
            self.sounds.pause_all_sounds()
            self.gamestate = State.PAUSE
            return ViewEvent(type=ViewEventType.NONE)

        action = self.controller.update(
            self.state, dt, self.input_reader.read()
        )
        if action.type == GameActionType.VICTORY:
            self.state.game_win = True
            self.win_timer = 0.0
            return ViewEvent(type=ViewEventType.NONE)
        if action.type == GameActionType.GAME_OVER:
            self.state.game_over = True
            self.game_over_timer = 0.0
            return ViewEvent(type=ViewEventType.NONE)
        if (action.type == GameActionType.EAT):
            self.timer = 0

        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        rl.unload_texture(self.maze_texture)
        rl.unload_image(self.maze_image)

    def _draw_collectible(self, collectible: Collectible) -> None:
        if not collectible.visible:
            return

        x, y = self.geometry.get_draw_pos(collectible.screen_pos)
        x += self.margin[0]
        y += self.margin[1]

        source = rl.Rectangle(
            0, 0, collectible.sprite.width, collectible.sprite.height
        )
        offset = 10
        dest = rl.Rectangle(
            x + offset, y + offset,
            self.geometry.cell_size - 20, self.geometry.cell_size - 20
        )

        rl.draw_texture_pro(
            collectible.sprite,
            source,
            dest,
            rl.Vector2(0, 0),
            0.0,
            rl.WHITE,
        )

    def _draw_entity(self, entity: Entity, sprite: rl.Texture) -> None:
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
        self._set_cheat_btn_positions()
