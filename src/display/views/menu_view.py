import pyray as rl
from typing import Callable

from .view import View, ViewEvent, ViewEventType


class Button:
    def __init__(
        self, x: int, y: int, label: str, font_size: int, action: Callable
    ):
        self.x = x
        self.y = y
        self.label = label
        self.w = rl.measure_text(self.label, font_size)
        self.h = font_size
        self.action = action
        self.font_size = font_size

    def contains(self, mx: int, my: int) -> bool:
        """Check if the coords (mx, my) are in the button

        Keyword arguments:
        mx -- x coordinate
        my -- y coordinate
        """
        return (
            self.x <= mx < self.x + self.w and
            self.y <= my < self.y + self.h
        )

    def draw(self):
        # rl.draw_rectangle(self.x, self.y, self.w, self.h, rl.PURPLE)
        rl.draw_text(self.label, self.x, self.y, self.font_size, rl.WHITE)


class MenuView(View):
    def __init__(self):
        self.play_btn = Button(1, 25, "PLAY", 40, lambda: None)
        self.exit_btn = Button(1, 45, "EXIT", 40, lambda: None)
        self.play_btn.x = 900 // 2 - self.play_btn.w // 2
        self.play_btn.y = 700 // 2 - self.play_btn.h
        self.exit_btn.x = 900 // 2 - self.exit_btn.w // 2
        self.exit_btn.y = 700 // 2
        self.btns = []

    def draw(self):
        rl.clear_background(rl.BLACK)
        for btn in self.btns:
            btn.draw()
        self.play_btn.draw()
        self.exit_btn.draw()

    def update(self, dt: float) -> ViewEvent:
        mouse = rl.get_mouse_position()
        if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
            for btn in self.btns:
                if (btn.contains(mouse.x, mouse.y)):
                    btn.action()
            if (self.play_btn.contains(mouse.x, mouse.y)):
                return (
                    ViewEvent(type=ViewEventType.CHANGE_VIEW, message="maze")
                )
            if (self.exit_btn.contains(mouse.x, mouse.y)):
                return (ViewEvent(type=ViewEventType.QUIT))

        return (ViewEvent(type=ViewEventType.NONE))

    def close(self) -> None:
        return
