import pyray as rl
from enum import Enum, auto
from pathlib import Path

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button
from src.display.maze_renderer import WALL_COLOR
from src.sounds import Sounds


class State(Enum):
    NORMAL = auto()
    BTN_ANIM = auto()


class MenuView(View):
    def __init__(
        self,
        width: int,
        height: int,
        textures: dict[str, dict[str, list[rl.Texture]] | list[rl.Texture]],
        sounds: Sounds
    ) -> None:
        self.textures = textures
        self.sounds = sounds
        self.width = width
        self.height = height

        self.classic_btn = Button(0, 0, "CLASSIC", 0, lambda: None)
        self.random_btn = Button(0, 0, "RANDOM", 0, lambda: None)
        self.inst_btn = Button(0, 0, "INSTRUCTIONS", 0, lambda: None)
        self.exit_btn = Button(0, 0, "EXIT", 0, lambda: None)

        self.buttons = [
            self.classic_btn,
            self.random_btn,
            self.inst_btn,
            self.exit_btn
        ]
        self.selected_index = 0

        self.state = State.NORMAL
        self.anim_pos = [0.0, 0.0]
        self.anim_time = 0.5
        self.pending_event: ViewEvent
        self.anim_size = 0
        self.anim_timer = 0.0
        self.anim_frame = 0

        self.font_size = 0
        self.title_size = 0
        self.score_font_size = 0

        self.title = "PAC-MAN"
        self.title_x = 0
        self.title_y = 0
        self.title_w = 0
        self.title_h = 0

        self.panel_x = 0
        self.panel_y = 0
        self.panel_w = 0
        self.panel_h = 0
        self.panel_padding_x = 0
        self.panel_padding_y = 0

        self.left_col_x = 0
        self.right_col_x = 0
        self.content_top_y = 0
        self.btn_spacing = 0

        self.leaderboard: list[tuple[str, int]] = []

        self._position_btns()

    def _get_top_scores(self) -> list[tuple[str, int]]:
        return self.leaderboard[:10]

    def _get_longest_score_width(self) -> int:
        visible_scores = self._get_top_scores()
        if not visible_scores:
            return 0

        max_line_width = 0
        for name, score in visible_scores:
            line = f"{name}: {score}"
            line_width = rl.measure_text(line, self.score_font_size)
            if line_width > max_line_width:
                max_line_width = line_width
        return max_line_width

    def _position_btns(self) -> None:
        self.font_size = max(28, self.height // 18)
        self.title_size = self.font_size * 2
        self.score_font_size = max(18, self.font_size // 2)

        self.btn_spacing = max(12, self.font_size // 3)

        self.title_w = rl.measure_text(self.title, self.title_size)
        self.title_h = self.title_size

        for btn in self.buttons:
            btn.font_size = self.font_size
            btn.h = self.font_size
            btn.w = rl.measure_text(btn.label, self.font_size)

        button_col_w = 0
        for btn in self.buttons:
            if btn.w > button_col_w:
                button_col_w = btn.w

        score_col_w = max(
            self._get_longest_score_width(),
            rl.measure_text("00: 000000", self.score_font_size)
        )

        col_gap = max(60, self.width // 18)
        self.panel_padding_x = max(self.font_size + 10, self.width // 40)
        self.panel_padding_y = max(24, self.height // 32)

        buttons_h = (
            len(self.buttons) * self.font_size
            + (len(self.buttons) - 1) * self.btn_spacing
        )

        visible_scores = self._get_top_scores()
        score_block_h = max(
            buttons_h,
            len(visible_scores) * (
                self.score_font_size if visible_scores else buttons_h
            )
        )

        content_w = button_col_w + col_gap + score_col_w
        content_h = self.title_h + max(24, self.font_size) + score_block_h

        self.panel_w = content_w + self.panel_padding_x * 2
        self.panel_h = content_h + self.panel_padding_y * 2

        self.panel_x = self.width // 2 - self.panel_w // 2
        self.panel_y = self.height // 2 - self.panel_h // 2

        self.left_col_x = self.panel_x + self.panel_padding_x
        self.right_col_x = self.left_col_x + button_col_w + col_gap

        content_left = self.left_col_x
        content_right = self.right_col_x + score_col_w
        content_center = (content_left + content_right) / 2

        self.title_x = int(content_center - self.title_w / 2)
        self.title_y = self.panel_y + self.panel_padding_y

        self.content_top_y = self.title_y + self.title_h + max(
            24, self.font_size
        )

        for i, btn in enumerate(self.buttons):
            btn.x = self.left_col_x
            btn.y = self.content_top_y + i * (
                self.font_size + self.btn_spacing
            )

    def _get_leaderboard(self) -> None:
        self.leaderboard = []
        try:
            cache_dir = Path.home() / ".local" / "share" / "pacman"
            with open(cache_dir / "leaderboard.pm", "r") as file:
                for line in file:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue

                    user, score = line.split(":", 1)
                    user = user.strip()
                    score = score.strip()

                    if not user:
                        continue

                    try:
                        score_value = int(score)
                    except ValueError:
                        continue

                    self.leaderboard.append((user, score_value))
        except (FileNotFoundError, PermissionError):
            return

        self.leaderboard.sort(key=lambda c: c[1], reverse=True)

    def _draw_panel(self) -> None:
        background = rl.Color(0, 0, 0, 255)
        border = WALL_COLOR

        rl.draw_rectangle(
            self.panel_x,
            self.panel_y,
            self.panel_w,
            self.panel_h,
            background
        )

        rl.draw_rectangle_lines_ex(
            rl.Rectangle(
                float(self.panel_x),
                float(self.panel_y),
                float(self.panel_w),
                float(self.panel_h)
            ),
            3.0,
            border
        )

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)

        self._draw_panel()

        rl.draw_text(
            self.title,
            self.title_x,
            self.title_y,
            self.title_size,
            rl.YELLOW
        )

        mouse = rl.get_mouse_position()
        mx, my = int(mouse.x), int(mouse.y)

        for i, btn in enumerate(self.buttons):
            if btn.contains(mx, my):
                self.selected_index = i
                break

        src = rl.Rectangle(0, 0, 32, 32)

        for i, btn in enumerate(self.buttons):
            hovered = btn.contains(mx, my)
            selected = i == self.selected_index

            if (hovered or selected) and self.state != State.BTN_ANIM:
                if btn is self.classic_btn:
                    btn.color = rl.Color(43, 255, 255, 255)
                elif btn is self.random_btn:
                    btn.color = rl.PINK
                elif btn is self.inst_btn:
                    btn.color = rl.ORANGE
                elif btn is self.exit_btn:
                    btn.color = rl.RED

                if isinstance(self.textures["pac_man"], dict):
                    dst = rl.Rectangle(
                        btn.x - self.font_size,
                        btn.y,
                        self.font_size,
                        self.font_size
                    )
                    rl.draw_texture_pro(
                        self.textures["pac_man"]["right"][1],
                        src,
                        dst,
                        rl.Vector2(0, 0),
                        0,
                        rl.WHITE
                    )
            else:
                btn.color = rl.WHITE

            btn.draw()

        visible_scores = self._get_top_scores()
        if visible_scores:
            score_block_h = len(visible_scores) * self.score_font_size
            score_start_y = self.content_top_y

            if score_block_h < (
                len(self.buttons) * self.font_size
                + (len(self.buttons) - 1) * self.btn_spacing
            ):
                button_block_h = (
                    len(self.buttons) * self.font_size
                    + (len(self.buttons) - 1) * self.btn_spacing
                )
                score_start_y = self.content_top_y + (
                    button_block_h - score_block_h
                ) // 2

            for i, (name, score) in enumerate(visible_scores):
                rl.draw_text(
                    f"{name}: {score}",
                    self.right_col_x,
                    score_start_y + i * self.score_font_size,
                    self.score_font_size,
                    rl.WHITE
                )

        if self.state == State.BTN_ANIM:
            self._draw_btn_anim()

    def _draw_btn_anim(self) -> None:
        if not isinstance(self.textures["pac_man"], dict):
            return

        src = rl.Rectangle(0, 0, 32, 32)
        dst = rl.Rectangle(
            self.anim_pos[0],
            self.anim_pos[1],
            self.font_size,
            self.font_size
        )

        texture = self.textures["pac_man"]["right"][self.anim_frame // 8 % 2]

        rl.draw_rectangle(
            self.panel_x + self.font_size // 2,
            int(self.anim_pos[1]),
            int(self.anim_pos[0] - self.panel_x),
            self.font_size,
            rl.Color(0, 0, 0, 255)
        )

        rl.draw_texture_pro(texture, src, dst, rl.Vector2(0, 0), 0, rl.WHITE)

    def update(self, dt: float) -> ViewEvent:
        self._get_leaderboard()
        self._position_btns()

        match self.state:
            case State.NORMAL:
                return self._update_normal(dt)
            case State.BTN_ANIM:
                return self._update_anim(dt)

    def _update_anim(self, dt: float) -> ViewEvent:
        self.anim_frame += 1
        self.anim_timer += dt

        if self.anim_timer >= self.anim_time:
            self.state = State.NORMAL
            return self.pending_event

        delta = dt * (self.anim_size + self.font_size) / self.anim_time

        if self.anim_frame % 4 == 0:
            self.sounds.play_munch()

        self.anim_pos[0] += delta
        return ViewEvent(type=ViewEventType.NONE)

    def _start_anim(self, btn: Button, event: ViewEvent) -> None:
        self.anim_timer = 0
        self.sounds.munch_counter = 0
        self.state = State.BTN_ANIM
        self.anim_pos = [btn.x - self.font_size, btn.y]
        self.anim_size = rl.measure_text(btn.label, btn.font_size)
        self.anim_frame = 0
        self.pending_event = event

    def _activate_selected_button(self) -> ViewEvent:
        selected_btn = self.buttons[self.selected_index]

        if selected_btn is self.classic_btn:
            self._start_anim(
                self.classic_btn,
                ViewEvent(type=ViewEventType.START_GAME, message="classic")
            )
            return ViewEvent(type=ViewEventType.NONE)

        if selected_btn is self.random_btn:
            self._start_anim(
                self.random_btn,
                ViewEvent(type=ViewEventType.START_GAME, message="random")
            )
            return ViewEvent(type=ViewEventType.NONE)

        if selected_btn is self.inst_btn:
            self._start_anim(
                self.inst_btn,
                ViewEvent(
                    type=ViewEventType.CHANGE_VIEW,
                    message="instruction"
                )
            )
            return ViewEvent(type=ViewEventType.NONE)

        if selected_btn is self.exit_btn:
            return ViewEvent(type=ViewEventType.QUIT)

        return ViewEvent(type=ViewEventType.NONE)

    def _update_normal(self, dt: float) -> ViewEvent:
        mouse = rl.get_mouse_position()
        mx, my = int(mouse.x), int(mouse.y)

        if rl.is_key_pressed(rl.KEY_UP):
            self.selected_index = (self.selected_index - 1) % len(self.buttons)

        if rl.is_key_pressed(rl.KEY_DOWN):
            self.selected_index = (self.selected_index + 1) % len(self.buttons)

        if (
            rl.is_key_pressed(rl.KEY_ENTER)
            or rl.is_key_pressed(rl.KEY_KP_ENTER)
        ):
            return self._activate_selected_button()

        if rl.is_key_pressed(rl.KEY_C):
            self.selected_index = 0
            self._start_anim(
                self.classic_btn,
                ViewEvent(type=ViewEventType.START_GAME, message="classic")
            )
            return ViewEvent(type=ViewEventType.NONE)

        if rl.is_key_pressed(rl.KEY_R):
            self.selected_index = 1
            self._start_anim(
                self.random_btn,
                ViewEvent(type=ViewEventType.START_GAME, message="random")
            )
            return ViewEvent(type=ViewEventType.NONE)

        if rl.is_key_pressed(rl.KEY_I):
            self.selected_index = 2
            self._start_anim(
                self.inst_btn,
                ViewEvent(
                    type=ViewEventType.CHANGE_VIEW,
                    message="instruction"
                )
            )
            return ViewEvent(type=ViewEventType.NONE)

        if rl.is_key_pressed(rl.KEY_E):
            self.selected_index = 3
            return ViewEvent(type=ViewEventType.QUIT)

        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            if self.classic_btn.contains(mx, my):
                self.selected_index = 0
                self._start_anim(
                    self.classic_btn,
                    ViewEvent(type=ViewEventType.START_GAME, message="classic")
                )
                return ViewEvent(type=ViewEventType.NONE)

            if self.random_btn.contains(mx, my):
                self.selected_index = 1
                self._start_anim(
                    self.random_btn,
                    ViewEvent(type=ViewEventType.START_GAME, message="random")
                )
                return ViewEvent(type=ViewEventType.NONE)

            if self.inst_btn.contains(mx, my):
                self.selected_index = 2
                self._start_anim(
                    self.inst_btn,
                    ViewEvent(
                        type=ViewEventType.CHANGE_VIEW,
                        message="instruction"
                    )
                )
                return ViewEvent(type=ViewEventType.NONE)

            if self.exit_btn.contains(mx, my):
                self.selected_index = 3
                return ViewEvent(type=ViewEventType.QUIT)

        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        return

    def resize(self) -> None:
        self.width = rl.get_screen_width()
        self.height = rl.get_screen_height()
        self._position_btns()
