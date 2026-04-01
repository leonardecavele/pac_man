import pyray as rl

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button


class MenuView(View):
    def __init__(self, width: int, height: int):
        self.play_btn = Button(1, 25, "PLAY", 40, lambda: None)
        self.exit_btn = Button(1, 45, "EXIT", 40, lambda: None)
        self.play_btn.x = width // 2 - self.play_btn.w // 2
        self.play_btn.y = height // 2 - self.play_btn.h
        self.exit_btn.x = width // 2 - self.exit_btn.w // 2
        self.exit_btn.y = height // 2
        self.btns: list[Button] = []

    def draw(self):
        rl.clear_background(rl.BLACK)
        for btn in self.btns:
            btn.draw()
        self.play_btn.draw()
        self.exit_btn.draw()

    def update(self, dt: float) -> ViewEvent:
        if (rl.is_key_pressed(rl.KEY_ENTER)):
            return (
                ViewEvent(type=ViewEventType.CHANGE_VIEW, message="maze")
            )
        mouse = rl.get_mouse_position()
        if (self.play_btn.contains(mouse.x, mouse.y)):
            self.play_btn.color = rl.YELLOW
        else:
            self.play_btn.color = rl.WHITE
        if (self.exit_btn.contains(mouse.x, mouse.y)):
            self.exit_btn.color = rl.RED
        else:
            self.exit_btn.color = rl.WHITE
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
