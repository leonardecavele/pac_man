import pyray as rl
import math
from enum import Enum, auto
from pathlib import Path

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button


class State(Enum):
    NORMAL = auto()
    BTN_ANIM = auto()


class MenuView(View):
    def __init__(self, width: int, height: int, textures):
        self.textures = textures
        self.width = width
        self.height = height
        self.classic_btn = Button(0, 45, "CLASSIC", 0, lambda: None)
        self.random_btn = Button(0, 45, "RANDOM", 0, lambda: None)
        self.inst_btn = Button(0, 45, "INSTRUCTIONS", 0, lambda: None)
        self.exit_btn = Button(0, 45, "EXIT", 0, lambda: None)

        self.state = State.NORMAL
        self.anim_pos = [0.0, 0.0]
        self.anim_time = 1
        self.pending_event: ViewEvent
        self.anim_size = 0
        self.anim_timer = 0.0
        self.anim_frame = 0
        self._position_btns()

    def _position_btns(self):
        tmp = [self.classic_btn, self.random_btn, self.inst_btn, self.exit_btn]
        self.col1 = self.width // 20
        self.font_size = self.height // 16
        start_y = (self.height - 3 * self.font_size) // 2
        for (i, btn) in enumerate(tmp):
            btn.x = self.col1
            btn.font_size = self.font_size
            btn.h = self.font_size
            btn.y = start_y + btn.h * i
            btn.w = rl.measure_text(btn.label, self.font_size)

    def _get_leaderboard(self) -> None:
        self.leaderboard: list[tuple[str, int]] = []
        try:
            cache_dir = Path.home() / ".cache" / "pacman"
            with open(cache_dir / "leaderboard.pm", "r") as file:
                for line in file:
                    user, score = line.split(":")
                    self.leaderboard.append((user, int(score)))
        except (FileNotFoundError, PermissionError):
            return
        self.leaderboard.sort(key=lambda c: c[1], reverse=True)

    def draw(self):
        rl.clear_background(rl.BLACK)
        font_size = self.font_size * 3
        title = "PAC-MAN"
        x = self.width // 2 - rl.measure_text(title, font_size) // 2
        y = font_size // 4
        rl.draw_text(title, x, y, font_size, rl.YELLOW)
        self.classic_btn.draw()
        self.random_btn.draw()
        self.inst_btn.draw()
        self.exit_btn.draw()
        if (len(self.leaderboard)):
            tmp = self.font_size // 2
            x = self.width - rl.measure_text(
                "O" * (10 + len(str(self.leaderboard[0][1])) + 1), tmp)
            y = self.height // 2 - (len(self.leaderboard) // 2) * tmp
            for i in range(min(10, len(self.leaderboard))):
                rl.draw_text(f"{self.leaderboard[i][0]}: {self.leaderboard[i][1]}",
                             x, y + tmp * i, tmp, rl.WHITE)
        if self.state == State.BTN_ANIM:
            self._draw_btn_anim()

    def _draw_btn_anim(self):
        src = rl.Rectangle(0, 0, 32, 32)
        dst = rl.Rectangle(
            self.anim_pos[0], self.anim_pos[1], self.font_size, self.font_size)
        texture = self.textures["pac_man"]["right"][self.anim_frame // 8 % 2]
        rl.draw_rectangle(
            0, int(self.anim_pos[1]),
            int(self.anim_pos[0]) + self.font_size // 2, self.font_size,
            rl.BLACK)
        rl.draw_texture_pro(texture, src, dst, rl.Vector2(0, 0), 0, rl.WHITE)

    def update(self, dt: float) -> ViewEvent:
        self._get_leaderboard()
        match self.state:
            case State.NORMAL:
                return (self._update_normal(dt))
            case State.BTN_ANIM:
                return (self._update_anim(dt))
        return (ViewEvent(type=ViewEventType.NONE))

    def _update_anim(self, dt: float) -> ViewEvent:
        self.anim_frame += 1
        self.anim_timer += dt
        if (self.anim_timer >= self.anim_time):
            self.state = State.NORMAL
            return (self.pending_event)
        delta = dt * (self.anim_size +
                      self.font_size) / self.anim_time
        self.anim_pos[0] += delta
        return (ViewEvent(type=ViewEventType.NONE))

    def _update_normal(self, dt: float) -> ViewEvent:
        if (rl.is_key_pressed(rl.KEY_C)):
            return (
                ViewEvent(type=ViewEventType.START_GAME, message="classic")
            )
        if (rl.is_key_pressed(rl.KEY_R)):
            return (
                ViewEvent(type=ViewEventType.START_GAME, message="random")
            )
        if (rl.is_key_pressed(rl.KEY_E)):
            return (ViewEvent(type=ViewEventType.QUIT))

        mouse = rl.get_mouse_position()
        src = rl.Rectangle(0, 0, 32, 32)

        # color
        if (self.classic_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.classic_btn.y,
                               self.font_size, self.font_size)
            self.classic_btn.color = rl.BLUE
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
        else:
            self.classic_btn.color = rl.WHITE

        if (self.random_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.random_btn.y,
                               self.font_size, self.font_size)
            self.random_btn.color = rl.PINK
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
        else:
            self.random_btn.color = rl.WHITE

        if (self.inst_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.inst_btn.y,
                               self.font_size, self.font_size)
            self.inst_btn.color = rl.ORANGE
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
        else:
            self.inst_btn.color = rl.WHITE

        if (self.exit_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.exit_btn.y,
                               self.font_size, self.font_size)
            self.exit_btn.color = rl.RED
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
        else:
            self.exit_btn.color = rl.WHITE

        # button pressed
        if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
            if (self.classic_btn.contains(mouse.x, mouse.y)):
                self.anim_timer = 0
                self.state = State.BTN_ANIM
                self.anim_pos = [dst.x, dst.y]
                self.anim_size = rl.measure_text(
                    self.classic_btn.label, self.classic_btn.font_size)
                self.anim_frame = 0
                self.pending_event = ViewEvent(
                    type=ViewEventType.START_GAME, message="classic"
                )
                return (ViewEvent(type=ViewEventType.NONE))
            if (self.random_btn.contains(mouse.x, mouse.y)):
                self.anim_timer = 0
                self.state = State.BTN_ANIM
                self.anim_pos = [dst.x, dst.y]
                self.anim_size = rl.measure_text(
                    self.random_btn.label, self.random_btn.font_size)
                self.anim_frame = 0
                self.pending_event = ViewEvent(
                    type=ViewEventType.START_GAME, message="classic"
                )
                return (ViewEvent(type=ViewEventType.NONE))
            if (self.inst_btn.contains(mouse.x, mouse.y)):
                self.anim_timer = 0
                self.state = State.BTN_ANIM
                self.anim_pos = [dst.x, dst.y]
                self.anim_size = rl.measure_text(
                    self.inst_btn.label, self.inst_btn.font_size)
                self.anim_frame = 0
                self.pending_event = ViewEvent(type=ViewEventType.NONE)
                return (ViewEvent(type=ViewEventType.NONE))
            if (self.exit_btn.contains(mouse.x, mouse.y)):
                return (ViewEvent(type=ViewEventType.QUIT))

        return (ViewEvent(type=ViewEventType.NONE))

    def close(self) -> None:
        return

    def resize(self) -> None:
        self.width = rl.get_screen_width()
        self.height = rl.get_screen_height()
        self._position_btns()
