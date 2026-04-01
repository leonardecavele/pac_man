import pyray as rl

from .view import View, ViewEvent, ViewEventType


class EndView(View):
    def __init__(self, width: int, height: int):
        self.score = 0
        self.action = "game_over"
        self.width = width
        self.height = height
        self.font_size = 40

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)
        rl.draw_text(self.action, self.width // 2 -
                     rl.measure_text(self.action, self.font_size) // 2, 10, self.font_size, rl.WHITE)
        rl.draw_text(f"Score: {self.score}", self.width // 2 -
                     rl.measure_text(str(f"Score: {self.score}"), self.font_size) // 2, 20 + self.font_size, self.font_size, rl.WHITE)

    def update(self, dt: float) -> ViewEvent:
        return (ViewEvent(type=ViewEventType.NONE))

    def close(self) -> None:
        return
