import pyray as rl

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button


class MenuView(View):
    def __init__(self, width: int, height: int):
        self.classic_btn = Button(1, 45, "CLASSIC", 40, lambda: None)
        self.classic_btn.x = width // 2 - self.classic_btn.w // 2
        self.classic_btn.y = (height // 2) - self.classic_btn.h

        self.random_btn = Button(1, 45, "RANDOM", 40, lambda: None)
        self.random_btn.x = width // 2 - self.random_btn.w // 2
        self.random_btn.y = (height // 2)

        self.exit_btn = Button(1, 45, "EXIT", 40, lambda: None)
        self.exit_btn.x = width // 2 - self.exit_btn.w // 2
        self.exit_btn.y = (height // 2) + self.classic_btn.h

        self.btns: list[Button] = []

    def draw(self):
        rl.clear_background(rl.BLACK)
        for btn in self.btns:
            btn.draw()
        self.classic_btn.draw()
        self.random_btn.draw()
        self.exit_btn.draw()

    def update(self, dt: float) -> ViewEvent:
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

        # color
        if (self.classic_btn.contains(mouse.x, mouse.y)):
            self.classic_btn.color = rl.YELLOW
        else:
            self.classic_btn.color = rl.WHITE

        if (self.random_btn.contains(mouse.x, mouse.y)):
            self.random_btn.color = rl.BLUE
        else:
            self.random_btn.color = rl.WHITE
        if (self.exit_btn.contains(mouse.x, mouse.y)):
            self.exit_btn.color = rl.RED
        else:
            self.exit_btn.color = rl.WHITE

        # button pressed
        if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
            for btn in self.btns:
                if (btn.contains(mouse.x, mouse.y)):
                    btn.action()
            if (self.classic_btn.contains(mouse.x, mouse.y)):
                return (
                    ViewEvent(
                        type=ViewEventType.START_GAME, message="classic"
                    )
                )
            if (self.random_btn.contains(mouse.x, mouse.y)):
                return (
                    ViewEvent(
                        type=ViewEventType.START_GAME, message="random"
                    )
                )
            if (self.exit_btn.contains(mouse.x, mouse.y)):
                return (ViewEvent(type=ViewEventType.QUIT))

        return (ViewEvent(type=ViewEventType.NONE))

    def close(self) -> None:
        return
