import pyray as rl

from .view import View, ViewEvent, ViewEventType
from src.display.components import Button


class MenuView(View):
    def __init__(self, width: int, height: int, textures):
        self.textures = textures
        self.width = width
        self.height = height
        self.col1 = width // 20
        self.font_size = self.height // 16
        self.classic_btn = Button(
            self.col1, 45, "CLASSIC", self.font_size, lambda: None)
        self.random_btn = Button(
            self.col1, 45, "RANDOM", self.font_size, lambda: None)
        self.inst_btn = Button(self.col1, 45, "INSTRUCTIONS",
                               self.font_size, lambda: None)
        self.exit_btn = Button(self.col1, 45, "EXIT",
                               self.font_size, lambda: None)

        btn_h = self.classic_btn.h
        start_y = (height - 3 * btn_h) // 2
        self.classic_btn.y = start_y
        self.random_btn.y = start_y + btn_h
        self.inst_btn.y = start_y + 2 * btn_h
        self.exit_btn.y = start_y + 3 * btn_h

    def draw(self):
        rl.clear_background(rl.BLACK)
        font_size = self.font_size * 3
        title = "PAC-MAN"
        x = self.width // 2 - rl.measure_text(title, font_size) // 2
        y = font_size // 4
        rl.draw_text(title, x, y, font_size, rl.YELLOW)
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
        src = rl.Rectangle(0, 0, 32, 32)

        # color
        if (self.classic_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.classic_btn.y,
                               self.font_size, self.font_size)
            self.classic_btn.color = rl.BLUE
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
        else:
            self.classic_btn.color = rl.WHITE

        if (self.random_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.random_btn.y,
                               self.font_size, self.font_size)
            self.random_btn.color = rl.PINK
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
        else:
            self.random_btn.color = rl.WHITE

        if (self.inst_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.inst_btn.y,
                               self.font_size, self.font_size)
            self.inst_btn.color = rl.ORANGE
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
        else:
            self.inst_btn.color = rl.WHITE

        if (self.exit_btn.contains(mouse.x, mouse.y)):
            dst = rl.Rectangle(self.col1 // 4, self.exit_btn.y,
                               self.font_size, self.font_size)
            self.exit_btn.color = rl.RED
            rl.draw_texture_pro(self.textures["pac_man"]["right"][1],
                                src, dst, rl.Vector2(0, 0), 0, rl.WHITE)
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
