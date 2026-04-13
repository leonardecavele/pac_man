import pyray as rl

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button


class InstructionView(View):
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.font_size = min(self.width // 20, self.height // 20)
        self.sections = [
            ("HOW TO PLAY", [
                "Eat all the dots to win.",
                "Avoid ghosts — or eat them!",
                "Collect Power Pellets to frighten ghosts.",
                "Beat the clock before time runs out!",
            ]),
            ("CONTROLS", [
                "Move:   Arrow Keys / WASD / ZQSD / HJKL",
                "Pause:  ESC",
            ]),
        ]
        self.exit_btn = Button(5, 5, "[ESC] Menu", int(
            self.font_size * .8), lambda: None)

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)
        self.exit_btn.draw()
        nb_line = len(self.sections) - 1
        for i in self.sections:
            nb_line += 1 + len(i[1])
        start_y = self.height // 2 - self.font_size * (nb_line // 2)
        for (title, content) in self.sections:
            x = self.width // 2 - rl.measure_text(title, self.font_size) // 2
            rl.draw_text(title, x, start_y, self.font_size, rl.WHITE)
            rl.draw_rectangle(x - self.font_size // 4,
                              start_y + self.font_size - self.font_size // 8,
                              rl.measure_text(
                                  title, self.font_size) + self.font_size // 2,
                              self.font_size // 10,
                              rl.WHITE)
            start_y += self.font_size
            for line in content:
                x = self.width // 2 - \
                    rl.measure_text(line, int(self.font_size * .8)) // 2
                rl.draw_text(line, x, start_y, int(
                    self.font_size * .8), rl.WHITE)
                start_y += self.font_size
            start_y += self.font_size

    def update(self, dt: float) -> ViewEvent:
        if rl.is_key_pressed(rl.KEY_ESCAPE):
            return ViewEvent(type=ViewEventType.CHANGE_VIEW,
                             message="main_menu")
        mouse = rl.get_mouse_position()
        if (self.exit_btn.contains(mouse.x, mouse.y)):
            if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
                return ViewEvent(type=ViewEventType.CHANGE_VIEW,
                                 message="main_menu")
            self.exit_btn.color = rl.Color(255, 255, 255, 128)
        else:
            self.exit_btn.color = rl.WHITE

        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        pass

    def resize(self) -> None:
        self.width = rl.get_screen_width()
        self.height = rl.get_screen_height()
        self.font_size = min(self.width // 20, self.height // 20)
        self.exit_btn = Button(5, 5, "[ESC] Menu", int(
            self.font_size * .8), lambda: None)
