import pyray as rl
from typing import Callable


class Button:
    def __init__(
        self, x: int, y: int, label: str, font_size: int, action: Callable,
        color: rl.Color = rl.WHITE
    ) -> None:
        self.x = x
        self.y = y
        self.label = label
        self.w = rl.measure_text(self.label, font_size)
        self.h = font_size
        self.action = action
        self.font_size = font_size
        self.color = color

    def contains(self, mx: float, my: float) -> bool:
        """Check if the coords (mx, my) are in the button

        Keyword arguments:
        mx -- x coordinate
        my -- y coordinate
        """
        return (
            self.x <= mx < self.x + self.w and
            self.y <= my < self.y + self.h
        )

    def draw(self, offset_x: int = 0) -> None:
        rl.draw_text(self.label, self.x - offset_x,
                     self.y, self.font_size, self.color)
