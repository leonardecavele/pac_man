import pyray as rl

from enum import Enum, auto
from random import randint
from typing import cast

from src.gameplay import (
    GameActionType,
    GameController,
    GameGeometry,
    GameInputReader,
    GameState
)
from src.entity import Collectible, Entity, Ghost, Blinky, Inky, Pinky, Clyde
from src.display import MazeRenderer
from src.maze import Maze, RandomMaze
from src.display.components import Button
from src.parsing import Config
from src.display.maze_renderer import WALL_COLOR
from src.sounds import Sounds

from .view import View, ViewEvent, ViewEventType


CHEAT_MODE_COMB = [263, 262, 263, 262, 265, 265, 265, rl.KEY_SPACE]
CHEAT_MODE_COMB2 = [
    rl.KEY_H, rl.KEY_L, rl.KEY_H, rl.KEY_L, rl.KEY_K,
    rl.KEY_K, rl.KEY_K, rl.KEY_SPACE
]
CHEAT_MODE_COMB3 = [
    rl.KEY_A, rl.KEY_D, rl.KEY_A, rl.KEY_D, rl.KEY_W,
    rl.KEY_W, rl.KEY_W, rl.KEY_SPACE
]


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

        self.pause_selected_index = 0
        self.cheat_selected_index = 0
        self.selected_panel = "pause"

        self.maze_texture: rl.Texture | None = None
        self.maze_image: rl.Image | None = None

        self.timer = 1.0
        self.comb_idx = 0
        self.cheat_mode = False
        self.game_over_timer = 0.0
        self.game_over_delay = 2.0
        self.win_timer = 0.0
        self.win_delay = 2.0

        self.font_size = 24

        self.pause_btns = [
            Button(0, 0, "RESUME", self.font_size, lambda: None),
            Button(0, 0, "QUIT", self.font_size, lambda: None),
        ]

        self.cheat_btns = [
            Button(
                0, 0, "ADD 1 LIVE", self.font_size,
                lambda: setattr(self.state, 'HP', self.state.HP + 1)
            ),
            Button(
                0, 0, "REMOVE 1 LIVE", self.font_size,
                lambda: setattr(self.state, 'HP', self.state.HP - 1)
            ),
            Button(
                0, 0, "RESET TIMER", self.font_size,
                lambda: setattr(self.state, 'timer', 0)
            ),
            Button(
                0, 0, "SHOW TARGETS", self.font_size,
                lambda: setattr(
                    self.state,
                    'show_ghost_path',
                    not self.state.show_ghost_path
                )
            ),
            Button(
                0, 0, "CHEAT OFF", self.font_size, self._disable_cheat_mode
            ),
        ]

        self._load_maze(self.maze)

    def _load_maze(self, maze: Maze) -> None:
        self.maze = maze

        self.geometry = GameGeometry(
            width=self.width,
            height=self.height,
            maze=self.maze
        )

        self.state = GameState(
            maze=self.maze,
            config=self.config,
            textures=self.textures,
            sounds=self.sounds,
            geometry=self.geometry
        )

        self.maze_pixel_w = (
            self.state.maze.width
            * (self.geometry.cell_size + self.geometry.gap)
            + self.geometry.gap
        )
        self.maze_pixel_h = (
            self.state.maze.height
            * (self.geometry.cell_size + self.geometry.gap)
            + self.geometry.gap
        )
        self.margin = (
            self.width // 2 - self.maze_pixel_w // 2,
            self.height // 2 - self.maze_pixel_h // 2
        )
        self.font_size = self.margin[1] // 2
        self.controller = GameController(self.sounds)
        self.input_reader = GameInputReader()

        if self.maze_texture is not None:
            rl.unload_texture(self.maze_texture)
        if self.maze_image is not None:
            rl.unload_image(self.maze_image)

        self.maze_image = rl.gen_image_color(
            self.width - 50,
            self.height - 50,
            rl.BLACK
        )
        MazeRenderer(
            self.maze_image,
            self.state.maze,
            self.geometry.cell_size,
            self.geometry.gap
        )
        self.maze_texture = rl.load_texture_from_image(self.maze_image)

        self._set_pause_btn_positions()
        self._set_cheat_btn_positions()

    def _disable_cheat_mode(self) -> None:
        self.cheat_mode = False
        self.selected_panel = "pause"
        self._set_pause_btn_positions()
        self._set_cheat_btn_positions()

    def _get_pause_panels_layout(self) -> tuple[int, int, int, int, int]:
        panel_width = self.width // 3
        panel_height = self.height // 10 * 7
        gap = self.width // 40

        if self.cheat_mode:
            total_width = panel_width * 2 + gap
            left_x = self.width // 2 - total_width // 2
            cheat_x = left_x
            pause_x = left_x + panel_width + gap
        else:
            pause_x = self.width // 2 - panel_width // 2
            cheat_x = pause_x - panel_width - gap

        top_y = self.height // 2 - panel_height // 2
        return cheat_x, pause_x, top_y, panel_width, panel_height

    def _layout_panel_buttons(
        self,
        buttons: list[Button],
        panel_left: int,
        panel_top: int,
        panel_width: int,
        panel_height: int,
        *,
        title_height_ratio: float = 0.28,
        top_gap_ratio: float = 0.08,
        bottom_gap_ratio: float = 0.12,
        gap: int | None = None,
    ) -> None:
        if gap is None:
            gap = self.font_size // 2

        for btn in buttons:
            btn.font_size = self.font_size
            btn.w = rl.measure_text(btn.label, self.font_size)
            btn.h = self.font_size

        content_top = panel_top + int(panel_height * title_height_ratio)
        content_top += int(panel_height * top_gap_ratio)
        content_bottom = (
            panel_top
            + panel_height
            - int(panel_height * bottom_gap_ratio)
        )

        total_h = len(buttons) * self.font_size + (
            len(buttons) - 1
        ) * gap
        area_h = content_bottom - content_top
        start_y = content_top + max(0, (area_h - total_h) // 2)

        for i, btn in enumerate(buttons):
            btn.x = panel_left + panel_width // 2 - btn.w // 2
            btn.y = start_y + i * (self.font_size + gap)

    def draw(self) -> None:
        self._draw_running()
        if self.gamestate == State.PAUSE:
            self._draw_pause()

    def _set_cheat_btn_positions(self) -> None:
        cheat_x, _, menu_top, menu_width, menu_height = \
            self._get_pause_panels_layout()

        self._layout_panel_buttons(
            self.cheat_btns,
            cheat_x,
            menu_top,
            menu_width,
            menu_height,
            title_height_ratio=0.28,
            top_gap_ratio=0.08,
            bottom_gap_ratio=0.12,
            gap=self.font_size // 2
        )

    def _set_pause_btn_positions(self) -> None:
        _, pause_x, menu_top, menu_width, menu_height = \
            self._get_pause_panels_layout()

        self._layout_panel_buttons(
            self.pause_btns,
            pause_x,
            menu_top,
            menu_width,
            menu_height,
            title_height_ratio=0.28,
            top_gap_ratio=0.08,
            bottom_gap_ratio=0.12,
            gap=self.font_size // 2
        )

    def _draw_panel(
        self,
        menu_left: int,
        menu_top: int,
        menu_width: int,
        menu_height: int,
        title: str,
    ) -> None:
        outer_rect = rl.Rectangle(
            menu_left - 1,
            menu_top - 1,
            menu_width + 2,
            menu_height + 2
        )
        inner_rect = rl.Rectangle(
            menu_left,
            menu_top,
            menu_width,
            menu_height
        )

        rl.draw_rectangle_rounded(
            outer_rect,
            0.15,
            256,
            rl.Color(0, 0, 0, 160)
        )

        for i in range(3):
            border = rl.Rectangle(
                inner_rect.x + i,
                inner_rect.y + i,
                inner_rect.width - i * 2,
                inner_rect.height - i * 2
            )
            rl.draw_rectangle_rounded_lines(border, 0.15, 256, WALL_COLOR)

        title_w = rl.measure_text(title, self.font_size)
        title_x = menu_left + menu_width // 2 - title_w // 2
        title_y = menu_top + menu_height // 6

        rl.draw_text(title, title_x, title_y, self.font_size, rl.YELLOW)

        rl.draw_rectangle(
            title_x - self.font_size // 4,
            title_y + self.font_size - self.font_size // 8,
            title_w + self.font_size // 2,
            max(2, self.font_size // 10),
            rl.WHITE
        )

    def _draw_pause(self) -> None:
        cheat_x, pause_x, menu_top, menu_width, menu_height = \
            self._get_pause_panels_layout()

        if self.cheat_mode:
            self._draw_panel(
                cheat_x,
                menu_top,
                menu_width,
                menu_height,
                "CHEATS"
            )

        self._draw_panel(
            pause_x,
            menu_top,
            menu_width,
            menu_height,
            "PAUSE"
        )

        for i, btn in enumerate(self.pause_btns):
            if (
                self.selected_panel == "pause"
                and i == self.pause_selected_index
            ):
                if btn.label == "RESUME":
                    btn.color = rl.YELLOW
                elif btn.label == "QUIT":
                    btn.color = rl.RED
            btn.draw()

        if self.cheat_mode:
            for i, btn in enumerate(self.cheat_btns):
                if (
                    self.selected_panel == "cheat"
                    and i == self.cheat_selected_index
                ):
                    btn.color = rl.Color(255, 255, 255, 128)
                btn.draw()

    def _draw_texts(self) -> None:
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

        if self.state.start_time > 0.0:
            x, y = self.state.pac_man_spawn
            y -= 2
            spawn_x, spawn_y = self.geometry.maze_to_screen((x, y))
            spawn_x += self.margin[0]
            spawn_y += self.margin[1]

            text = "READY!"

            font_size = int(self.geometry.cell_size * 0.5)
            text_w = rl.measure_text(text, font_size)

            center_x = spawn_x + self.geometry.cell_size
            text_y = int(
                spawn_y - (font_size / 2)
            )

            text_x = int(center_x - text_w)

            padding_x = 8
            padding_y = 6

            box_x = text_x - padding_x
            box_y = text_y - padding_y
            box_w = text_w + padding_x * 2
            box_h = font_size + padding_y * 2

            rl.draw_rectangle(box_x, box_y, box_w, box_h, rl.BLACK)
            rl.draw_text(text, text_x, text_y, font_size, rl.YELLOW)

        if self.state.game_win:
            x, y = self.state.pac_man_spawn
            y -= 2
            center_x, center_y = self.geometry.maze_to_screen((x, y))
            center_x += self.margin[0]
            center_y += self.margin[1]

            text = "NEXT LEVEL!"

            font_size = int(self.geometry.cell_size * 0.5)
            text_w = rl.measure_text(text, font_size)

            text_x = int(center_x - text_w / 2)
            text_y = int(center_y - font_size / 2)

            padding_x = 8
            padding_y = 6

            box_x = text_x - padding_x
            box_y = text_y - padding_y
            box_w = text_w + padding_x * 2
            box_h = font_size + padding_y * 2

            rl.draw_rectangle(box_x, box_y, box_w, box_h, rl.BLACK)
            rl.draw_text(text, text_x, text_y, font_size, rl.YELLOW)

    def _draw_running(self) -> None:
        rl.clear_background(rl.BLACK)
        if self.maze_texture is not None:
            rl.draw_texture(
                self.maze_texture,
                self.margin[0],
                self.margin[1],
                rl.WHITE
            )

        if self.state.show_ghost_path and self.cheat_mode:
            self._draw_ghost_targets()

        if self.cheat_mode:
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

        if self.timer > 0.75:
            self._draw_entity(self.state.pac_man, self.state.pac_man.sprite)
        else:
            x, y = self.geometry.get_draw_pos(self.state.pac_man.screen_pos)
            x += self.margin[0]
            y += self.margin[1]
            rl.draw_text(
                str(self.state.config.points_per_ghost),
                x,
                y,
                int(self.geometry.cell_size * .75),
                rl.WHITE
            )

        rl.draw_text(
            str(self.state.score),
            self.margin[0] + self.maze_pixel_w // 10,
            self.margin[1] - self.font_size - 5,
            self.font_size,
            rl.WHITE
        )
        rl.draw_text(
            str(self.state.config.level_max_time - int(self.state.timer)),
            self.margin[0] + self.maze_pixel_w // 10 * 9,
            self.margin[1] - self.font_size - 5,
            self.font_size,
            rl.WHITE
        )

        src = rl.Rectangle(0, 0, 32, 32)
        for i in range(self.state.HP):
            dst = rl.Rectangle(
                self.margin[0] + self.maze_pixel_w // 20
                + i * self.geometry.cell_size,
                self.margin[1] + self.maze_pixel_h + 5,
                self.geometry.cell_size,
                self.geometry.cell_size
            )
            _pac = cast(dict[str, list[rl.Texture]], self.textures["pac_man"])
            rl.draw_texture_pro(
                _pac["left"][1], src, dst,
                rl.Vector2(0, 0), 0.0, rl.WHITE
            )

        self._draw_texts()

    def update(self, dt: float) -> ViewEvent:
        if self.gamestate == State.RUNNING:
            return self._update_running(dt)
        elif self.gamestate == State.PAUSE:
            return self._update_pause(dt)
        return ViewEvent(type=ViewEventType.NONE)

    def _update_cheat(self, dt: float) -> None:
        mouse = rl.get_mouse_position()
        mx, my = mouse.x, mouse.y
        for i, btn in enumerate(self.cheat_btns):
            if btn.contains(mx, my):
                self.selected_panel = "cheat"
                self.cheat_selected_index = i
                if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                    btn.action()
                else:
                    btn.color = rl.Color(255, 255, 255, 128)
            else:
                btn.color = rl.WHITE

    def _activate_pause_selection(self) -> ViewEvent:
        selected_btn = self.pause_btns[self.pause_selected_index]

        if selected_btn.label == "RESUME":
            self.gamestate = State.RUNNING
            self.sounds.resume_all_sounds()
            return ViewEvent(type=ViewEventType.NONE)

        if selected_btn.label == "QUIT":
            return ViewEvent(
                type=ViewEventType.CHANGE_VIEW,
                message="main_menu"
            )

        return ViewEvent(type=ViewEventType.NONE)

    def _activate_cheat_selection(self) -> ViewEvent:
        selected_btn = self.cheat_btns[self.cheat_selected_index]
        selected_btn.action()
        return ViewEvent(type=ViewEventType.NONE)

    def _update_pause(self, dt: float) -> ViewEvent:
        if self.cheat_mode:
            self._update_cheat(dt)

        key = rl.get_key_pressed()
        if (
            not self.cheat_mode
            and (
                key == CHEAT_MODE_COMB[self.comb_idx]
                or key == CHEAT_MODE_COMB2[self.comb_idx]
                or key == CHEAT_MODE_COMB3[self.comb_idx]
            )
        ):
            self.comb_idx += 1
        elif key != 0:
            self.comb_idx = 0

        if self.comb_idx >= len(CHEAT_MODE_COMB):
            self.cheat_mode = True
            self.selected_panel = "pause"
            self.comb_idx = 0
            self._set_pause_btn_positions()
            self._set_cheat_btn_positions()

        if rl.is_key_pressed(rl.KEY_ESCAPE):
            self.gamestate = State.RUNNING
            self.sounds.resume_all_sounds()
            return ViewEvent(type=ViewEventType.NONE)

        if (
            rl.is_key_pressed(rl.KEY_UP)
            or rl.is_key_pressed(rl.KEY_K)
            or rl.is_key_pressed(rl.KEY_W)
        ):
            if self.selected_panel == "pause":
                self.pause_selected_index = (
                    self.pause_selected_index - 1
                ) % len(self.pause_btns)
            elif self.cheat_mode:
                self.cheat_selected_index = (
                    self.cheat_selected_index - 1
                ) % len(self.cheat_btns)

        if (
            rl.is_key_pressed(rl.KEY_DOWN)
            or rl.is_key_pressed(rl.KEY_J)
            or rl.is_key_pressed(rl.KEY_S)
        ):
            if self.selected_panel == "pause":
                self.pause_selected_index = (
                    self.pause_selected_index + 1
                ) % len(self.pause_btns)
            elif self.cheat_mode:
                self.cheat_selected_index = (
                    self.cheat_selected_index + 1
                ) % len(self.cheat_btns)

        if (
            rl.is_key_pressed(rl.KEY_LEFT)
            or rl.is_key_pressed(rl.KEY_H)
            or rl.is_key_pressed(rl.KEY_A)
        ):
            self.selected_panel = "cheat"

        if (
            rl.is_key_pressed(rl.KEY_RIGHT)
            or rl.is_key_pressed(rl.KEY_L)
            or rl.is_key_pressed(rl.KEY_D)
        ):
            self.selected_panel = "pause"

        if (
            rl.is_key_pressed(rl.KEY_ENTER)
            or rl.is_key_pressed(rl.KEY_KP_ENTER)
        ):
            if self.selected_panel == "pause":
                return self._activate_pause_selection()
            if self.cheat_mode and self.selected_panel == "cheat":
                return self._activate_cheat_selection()

        mouse = rl.get_mouse_position()

        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            if self.pause_btns[0].contains(mouse.x, mouse.y):
                self.selected_panel = "pause"
                self.pause_selected_index = 0
                self.gamestate = State.RUNNING
                self.sounds.resume_all_sounds()
            elif self.pause_btns[1].contains(mouse.x, mouse.y):
                self.selected_panel = "pause"
                self.pause_selected_index = 1
                return ViewEvent(
                    type=ViewEventType.CHANGE_VIEW,
                    message="main_menu"
                )

        for i, btn in enumerate(self.pause_btns):
            if btn.contains(mouse.x, mouse.y):
                self.selected_panel = "pause"
                self.pause_selected_index = i

        if self.pause_selected_index == 0 and self.selected_panel == "pause":
            self.pause_btns[0].color = rl.YELLOW
        else:
            self.pause_btns[0].color = rl.WHITE

        if self.pause_selected_index == 1 and self.selected_panel == "pause":
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
                self._load_maze(RandomMaze(12, 12, randint(0, 10**9)))
                self.state.start_time = 2.0
                self.win_timer = 0.0
            return ViewEvent(type=ViewEventType.NONE)

        if rl.is_key_pressed(rl.KEY_ESCAPE):
            self.sounds.pause_all_sounds()
            self.gamestate = State.PAUSE
            self.selected_panel = "pause"
            self.pause_selected_index = 0
            return ViewEvent(type=ViewEventType.NONE)

        action = self.controller.update(
            self.state,
            dt,
            self.input_reader.read()
        )

        if action.type == GameActionType.VICTORY:
            self.state.game_win = True
            self.win_timer = 0.0
            return ViewEvent(type=ViewEventType.NONE)

        if action.type == GameActionType.GAME_OVER:
            self.state.game_over = True
            self.game_over_timer = 0.0
            return ViewEvent(type=ViewEventType.NONE)

        if action.type == GameActionType.EAT:
            self.timer = 0

        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        if self.maze_texture is not None:
            rl.unload_texture(self.maze_texture)
        if self.maze_image is not None:
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
        dest = rl.Rectangle(
            x,
            y,
            self.geometry.cell_size - 1,
            self.geometry.cell_size - 1
        )

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
        self._load_maze(self.maze)
        self.state.freeze(0.1)

    def _draw_ghost_targets(self) -> None:
        for ghost in self.state.ghosts:
            if ghost.target is None:
                continue

            center_x, center_y = self.geometry.maze_to_screen(ghost.target)
            center_x += self.margin[0]
            center_y += self.margin[1]

            x = center_x - self.geometry.cell_size // 2
            y = center_y - self.geometry.cell_size // 2

            if isinstance(ghost, Blinky):
                color_rgba = (255, 0, 0, 255)
            elif isinstance(ghost, Pinky):
                color_rgba = (255, 105, 180, 255)
            elif isinstance(ghost, Inky):
                color_rgba = (43, 255, 255, 255)
            elif isinstance(ghost, Clyde):
                color_rgba = (255, 165, 0, 255)
            else:
                color_rgba = (255, 255, 255, 255)

            r, g, b, a = color_rgba

            color = rl.Color(r, g, b, a)
            transparent_color = rl.Color(r, g, b, 60)

            rect = rl.Rectangle(
                x,
                y,
                self.geometry.cell_size,
                self.geometry.cell_size
            )

            rl.draw_rectangle_rec(rect, transparent_color)
            rl.draw_rectangle_lines_ex(rect, 3.0, color)
