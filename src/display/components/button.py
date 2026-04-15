import pyray as rl
from typing import Callable


class Button:
    """A clickable text label with an associated action callback."""

    def __init__(
        self, x: int, y: int, label: str, font_size: int, action: Callable,
        color: rl.Color = rl.WHITE
    ) -> None:
        """
        Initialize the button.

        x         -- left edge position in pixels
        y         -- top edge position in pixels
        label     -- text displayed on the button
        font_size -- text size in pixels (also used as button height)
        action    -- callable invoked when the button is activated
        color     -- text colour (default white)
        """
        self.x = x
        self.y = y
        self.label = label
        self.w = rl.measure_text(self.label, font_size)
        self.h = font_size
        self.action = action
        self.font_size = font_size
        self.color = color

    def contains(self, mx: float, my: float) -> bool:
        """Return True if the pixel coordinates (mx, my) fall within the button bounds."""
        return (
            self.x <= mx < self.x + self.w and
            self.y <= my < self.y + self.h
        )

    def draw(self, offset_x: int = 0) -> None:
        """Draw the button label, shifted left by offset_x pixels."""
        rl.draw_text(self.label, self.x - offset_x,
                     self.y, self.font_size, self.color)
