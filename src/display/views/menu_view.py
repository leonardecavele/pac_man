import pyray as rl

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button


class MenuView(View):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        col1 = width // 20
        self.font_size = self.height // 16
        self.classic_btn = Button(
            col1, 45, "CLASSIC", self.font_size, lambda: None)
        self.random_btn = Button(
            col1, 45, "RANDOM", self.font_size, lambda: None)
        self.inst_btn = Button(col1, 45, "INSTRUCTIONS",
                               self.font_size, lambda: None)
        self.exit_btn = Button(col1, 45, "EXIT", self.font_size, lambda: None)

        btn_h = self.classic_btn.h
        start_y = (height - 3 * btn_h) // 2
        self.classic_btn.y = start_y
        self.random_btn.y = start_y + btn_h
        self.inst_btn.y = start_y + 2 * btn_h
        self.exit_btn.y = start_y + 3 * btn_h

    def draw(self):
        rl.clear_background(rl.BLACK)
        self.classic_btn.draw()
        self.random_btn.draw()
        self.inst_btn.draw()
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
            self.classic_btn.color = rl.BLUE
        else:
            self.classic_btn.color = rl.WHITE

        if (self.random_btn.contains(mouse.x, mouse.y)):
            self.random_btn.color = rl.PINK
        else:
            self.random_btn.color = rl.WHITE

        if (self.inst_btn.contains(mouse.x, mouse.y)):
            self.inst_btn.color = rl.ORANGE
        else:
            self.inst_btn.color = rl.WHITE

        if (self.exit_btn.contains(mouse.x, mouse.y)):
            self.exit_btn.color = rl.RED
        else:
            self.exit_btn.color = rl.WHITE

        # button pressed
        if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
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
