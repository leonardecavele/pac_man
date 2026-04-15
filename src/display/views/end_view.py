import pyray as rl
from pathlib import Path

from .view import View, ViewEvent, ViewEventType
from src.display.components import TextInput, Button


class EndView(View):
    """Screen shown after a game ends; lets the player enter a name and save
    their score."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize the end view for the given viewport dimensions."""
        self.score = -1
        self.width = width
        self.height = height
        self.title = "GAME OVER"
        self.name_max_chars = 10

        self.text_input = TextInput(0, 0, 40)
        self.submit_btn = Button(0, 0, "SUBMIT", 40, lambda: None)

        self.font_size = 40
        self.score_font_size = 28
        self.title_x = 0
        self.title_y = 0
        self.score_y = 0

        self._set_positions()

    def _set_positions(self) -> None:
        """Recompute font sizes and widget positions based on the current
        viewport size."""
        self.font_size = max(28, self.height // 14)
        self.score_font_size = max(22, self.font_size // 2)

        self.text_input.font_size = max(24, self.font_size // 2)
        self.submit_btn.font_size = max(24, self.font_size // 2)

        char_w = rl.measure_text("W", self.text_input.font_size)

        self.text_input.w = self.name_max_chars * (char_w + char_w // 5)
        self.text_input.h = self.text_input.font_size

        button_text_w = rl.measure_text(
            self.submit_btn.label,
            self.submit_btn.font_size
        )

        self.submit_btn.w = button_text_w
        self.submit_btn.h = self.submit_btn.font_size

        spacing = max(18, self.font_size // 2)

        total_h = (
            self.font_size
            + spacing
            + self.score_font_size
            + spacing * 2
            + self.text_input.h
            + spacing
            + self.submit_btn.h
        )

        start_y = self.height // 2 - total_h // 2

        self.title_x = (
            self.width // 2
            - rl.measure_text(self.title, self.font_size) // 2
        )
        self.title_y = start_y

        self.score_y = self.title_y + self.font_size + spacing // 2

        self.text_input.x = self.width // 2 - self.text_input.w // 2
        self.text_input.y = self.score_y + self.score_font_size + spacing * 2

        self.submit_btn.x = self.width // 2 - self.submit_btn.w // 2
        self.submit_btn.y = (
            self.text_input.y + self.text_input.h + spacing // 2
        )

    def draw(self) -> None:
        rl.clear_background(rl.BLACK)

        rl.draw_text(
            self.title,
            self.title_x,
            self.title_y,
            self.font_size,
            rl.RED
        )

        score_text = f"Score: {self.score}"

        rl.draw_text(
            score_text,
            self.width // 2
            - rl.measure_text(score_text, self.score_font_size) // 2,
            self.score_y,
            self.score_font_size,
            rl.WHITE
        )

        mouse = rl.get_mouse_position()
        is_hovered = self.submit_btn.contains(mouse.x, mouse.y)
        has_name = len(self.text_input.value) > 0

        if is_hovered and has_name:
            self.submit_btn.color = rl.Color(255, 255, 255, 128)
        else:
            self.submit_btn.color = rl.WHITE

        self.text_input.draw()
        self.submit_btn.draw()

    def update(self, dt: float) -> ViewEvent:
        self.text_input.handle_input()

        should_submit = False

        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            mouse = rl.get_mouse_position()
            if self.submit_btn.contains(mouse.x, mouse.y):
                should_submit = True

        if rl.is_key_pressed(rl.KEY_ENTER):
            should_submit = True

        if should_submit:
            if not self._save_score():
                return ViewEvent(type=ViewEventType.NONE)
            return ViewEvent(
                type=ViewEventType.CHANGE_VIEW,
                message="main_menu"
            )

        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        return

    def resize(self) -> None:
        self.width = rl.get_screen_width()
        self.height = rl.get_screen_height()
        self._set_positions()

    def _save_score(self) -> bool:
        """Append the player name and score to the leaderboard file.

        Return True on success, False if the input is empty or the file
        cannot be written.
        """
        try:
            if not len(self.text_input.value):
                return False
            cache_dir = Path.home() / ".local" / "share" / "pacman"
            cache_dir.mkdir(parents=True, exist_ok=True)
            with open(cache_dir / "leaderboard.pm", "a") as file:
                file.write(f"{self.text_input.value}:{self.score}\n")
            self.text_input.value = ""
        except (FileNotFoundError, PermissionError):
            return False
        return True
