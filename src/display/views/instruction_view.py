import pyray as rl

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button
from src.display.maze_renderer import WALL_COLOR


class InstructionView(View):
    """A read-only view that displays game instructions and control bindings."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize the instruction view for the given viewport dimensions."""
        self.width = width
        self.height = height

        self.sections = [
            ("HOW TO PLAY", [
                "Eat all the dots to win.",
                "Avoid ghosts or eat them!",
                "Collect Super Pacgums to frighten ghosts.",
                "Beat the clock before time runs out!",
            ]),
            ("CONTROLS", [
                "Move: Arrow Keys / WASD / HJKL",
                "Pause / Return: ESC",
            ]),
        ]

        self._update_layout()

    def _update_layout(self) -> None:
        """Recompute panel dimensions, font sizes, and button position for the current viewport."""
        self.font_size = min(self.width // 20, self.height // 20)
        self.title_size = self.font_size
        self.text_size = int(self.font_size * 0.8)

        self.panel_w = self.width * 2 // 3
        self.panel_h = self.height * 7 // 10
        self.panel_x = self.width // 2 - self.panel_w // 2
        self.panel_y = self.height // 2 - self.panel_h // 2

        self.panel_padding_x = self.panel_w // 10
        self.panel_padding_y = self.panel_h // 12

        self.exit_btn = Button(
            0,
            0,
            "Menu",
            self.text_size,
            lambda: None
        )
        self._set_exit_btn_position()

    def _set_exit_btn_position(self) -> None:
        """Position the exit button above the top-left corner of the content panel."""
        self.exit_btn.font_size = self.text_size
        self.exit_btn.w = rl.measure_text(self.exit_btn.label, self.text_size)
        self.exit_btn.h = self.text_size

        hud_padding = self.panel_w // 20
        hud_y = self.panel_y - self.text_size - 5

        self.exit_btn.x = self.panel_x + hud_padding
        self.exit_btn.y = hud_y

    def _wrap_text(
        self,
        text: str,
        font_size: int,
        max_width: int
    ) -> list[str]:
        """Split text into lines that fit within max_width at the given font size."""
        words = text.split()
        if not words:
            return [""]

        lines: list[str] = []
        current = words[0]

        for word in words[1:]:
            test_line = current + " " + word
            if rl.measure_text(test_line, font_size) <= max_width:
                current = test_line
            else:
                lines.append(current)
                current = word

        lines.append(current)
        return lines

    def _draw_panel(self) -> None:
        background = rl.Color(0, 0, 0, 255)
        border = WALL_COLOR

        rl.draw_rectangle(
            self.panel_x,
            self.panel_y,
            self.panel_w,
            self.panel_h,
            background
        )

        rl.draw_rectangle_lines_ex(
            rl.Rectangle(
                float(self.panel_x),
                float(self.panel_y),
                float(self.panel_w),
                float(self.panel_h)
            ),
            3.0,
            border
        )

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)
        self._draw_panel()
        self.exit_btn.draw()

        title_to_content_gap = max(16, self.font_size // 2)
        line_gap = max(8, self.font_size // 4)
        section_gap = max(20, self.font_size)

        content_left = self.panel_x + self.panel_padding_x
        content_right = self.panel_x + self.panel_w - self.panel_padding_x
        content_width = content_right - content_left

        total_height = 0
        for idx, (_, content) in enumerate(self.sections):
            total_height += self.title_size
            total_height += title_to_content_gap

            section_lines_height = 0
            for line in content:
                wrapped_lines = self._wrap_text(
                    line,
                    self.text_size,
                    content_width
                )
                section_lines_height += len(wrapped_lines) * self.text_size
                section_lines_height += (len(wrapped_lines) - 1) * line_gap

            if content:
                section_lines_height += (len(content) - 1) * line_gap

            total_height += section_lines_height

            if idx < len(self.sections) - 1:
                total_height += section_gap

        start_y = self.panel_y + self.panel_h // 2 - total_height // 2

        for idx, (title, content) in enumerate(self.sections):
            title_w = rl.measure_text(title, self.title_size)
            title_x = self.panel_x + self.panel_w // 2 - title_w // 2

            rl.draw_text(
                title,
                title_x,
                start_y,
                self.title_size,
                rl.YELLOW
            )

            rl.draw_rectangle(
                title_x - self.font_size // 4,
                start_y + self.title_size - self.font_size // 8,
                title_w + self.font_size // 2,
                max(2, self.font_size // 10),
                rl.WHITE
            )

            start_y += self.title_size + title_to_content_gap

            for line_idx, line in enumerate(content):
                wrapped_lines = self._wrap_text(
                    line,
                    self.text_size,
                    content_width
                )

                for wrapped_idx, wrapped_line in enumerate(wrapped_lines):
                    line_w = rl.measure_text(wrapped_line, self.text_size)
                    line_x = self.panel_x + self.panel_w // 2 - line_w // 2

                    rl.draw_text(
                        wrapped_line,
                        line_x,
                        start_y,
                        self.text_size,
                        rl.WHITE
                    )

                    start_y += self.text_size
                    if wrapped_idx < len(wrapped_lines) - 1:
                        start_y += line_gap

                if line_idx < len(content) - 1:
                    start_y += line_gap

            if idx < len(self.sections) - 1:
                start_y += section_gap

    def update(self, dt: float) -> ViewEvent:
        if rl.is_key_pressed(rl.KEY_ESCAPE):
            return ViewEvent(
                type=ViewEventType.CHANGE_VIEW,
                message="main_menu"
            )

        mouse = rl.get_mouse_position()
        if self.exit_btn.contains(mouse.x, mouse.y):
            if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                return ViewEvent(
                    type=ViewEventType.CHANGE_VIEW,
                    message="main_menu"
                )
            self.exit_btn.color = rl.Color(255, 255, 255, 128)
        else:
            self.exit_btn.color = rl.WHITE

        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        pass

    def resize(self) -> None:
        self.width = rl.get_screen_width()
        self.height = rl.get_screen_height()
        self._update_layout()
