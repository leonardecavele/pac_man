import pyray as rl

from .view import View, ViewEvent, ViewEventType
from src.display.components import TextInput, Button


class EndView(View):
    def __init__(self, width: int, height: int):
        self.score = -1
        self.action = ""
        self.width = width
        self.height = height
        self.font_size = 40
        self.text_input = TextInput(100, 100, 40)
        self.text_input.x = self.width // 2 - self.text_input.w // 2
        self.text_input.y = self.height // 2 - self.text_input.h // 2
        self.submit_btn = Button(1, 1, "SUBMIT", 40, lambda: None)
        self.submit_btn.x = width // 2 - self.submit_btn.w // 2
        self.submit_btn.y = height // 2 + self.text_input.h

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)
        rl.draw_text(self.action,
                     self.width // 2 -
                     rl.measure_text(self.action, self.font_size) // 2,
                     10, self.font_size, rl.WHITE)
        rl.draw_text(f"Score: {self.score}",
                     self.width // 2 -
                     rl.measure_text(str(f"Score: {self.score}"),
                                     self.font_size) // 2,
                     20 + self.font_size, self.font_size, rl.WHITE)
        self.text_input.draw()
        self.submit_btn.draw()

    def update(self, dt: float) -> ViewEvent:
        self.text_input.handle_input()
        # if (rl.is_key_down(rl.KEY_ENTER)):
        #     self._save_score()
        #     return (
        #         ViewEvent(type=ViewEventType.CHANGE_VIEW,
        #                   message="main_menu")
        #     )
        if (rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)):
            mouse = rl.get_mouse_position()
            if (self.submit_btn.contains(mouse.x, mouse.y)):
                self._save_score()
                return (
                    ViewEvent(type=ViewEventType.CHANGE_VIEW,
                              message="main_menu")
                )
        return (ViewEvent(type=ViewEventType.NONE))

    def close(self) -> None:
        return

    def _save_score(self):
        try:
            if (not len(self.text_input.value)):
                return
            with open("leaderboard.pm", "a") as file:
                file.write(f"{self.text_input.value}:{self.score}\n")
            self.text_input.value = ""
        except (FileNotFoundError, PermissionError):
            return
