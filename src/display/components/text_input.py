import pyray as rl


class TextInput:
    """A single-line text field that accepts letter input and supports backspace."""

    def __init__(self, x: int, y: int, font_size: int,
                 max_char: int = 10) -> None:
        """
        Initialize the text input widget.

        x         -- left edge position in pixels
        y         -- top edge position in pixels
        font_size -- text size in pixels
        max_char  -- maximum number of characters allowed
        """
        self.x = x
        self.y = y
        self.w = rl.measure_text("O", font_size) * (max_char + 2)
        self.h = font_size + 6
        self.font_size = font_size
        self.value = ""
        self.max_char = max_char
        self.a = 97
        self.z = 122
        self.A = 65
        self.Z = 90
        self.SPACE = 32
        self.tick_acumulator = 0.0
        self.animation_tick = 60

    def handle_input(self) -> None:
        """Process keyboard events to append characters or remove the last one."""
        rl.draw_rectangle_lines(self.x, self.y, self.w, self.h, rl.WHITE)
        input = rl.get_char_pressed()
        if (((input >= self.a and input <= self.z) or
                (input >= self.A and input <= self.Z))
                and len(self.value) < self.max_char):
            self.value += chr(input).upper()
        if (rl.is_key_pressed(rl.KEY_BACKSPACE) and len(self.value)):
            self.value = self.value[:-1]

    def draw(self) -> None:
        """Render the current value with a blinking cursor animation."""
        self.tick_acumulator += 1
        if (self.tick_acumulator < self.animation_tick
                and len(self.value) < self.max_char):
            rl.draw_text(self.value + "_", self.x + 5,
                         self.y + 4, self.font_size, rl.WHITE)
        else:
            rl.draw_text(self.value, self.x + 5, self.y +
                         4, self.font_size, rl.WHITE)
        if (self.tick_acumulator > self.animation_tick * 2):
            self.tick_acumulator = 0
