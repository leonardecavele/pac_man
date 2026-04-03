import pyray as rl


class Textures:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.tile_size = 32

    def _load_textures(self) -> dict[str, list[rl.Texture2D]]:
        self.sheet = rl.load_image("assets/Sprite_Sheet.png")
        textures = {
            "pacgum": self._load_pacgum_texture(),
            "super_pacgum": self._load_superpacgum_texture(),
            "pac_man_right": self._load_pacman_texture_right(),
            "pac_man_left": self._load_pacman_texture_left(),
            "pac_man_up": self._load_pacman_texture_up(),
            "pac_man_down": self._load_pacman_texture_down(),
            "blinky_right": self._load_blinky_texture_right(),
            "blinky_left": self._load_blinky_texture_left(),
            "blinky_up": self._load_blinky_texture_up(),
            "blinky_down": self._load_blinky_texture_down(),
            "pinky_right": self._load_pinky_texture_right(),
            "pinky_left": self._load_pinky_texture_left(),
            "pinky_up": self._load_pinky_texture_up(),
            "pinky_down": self._load_pinky_texture_down(),
            "inky_right": self._load_inky_texture_right(),
            "inky_left": self._load_inky_texture_left(),
            "inky_up": self._load_inky_texture_up(),
            "inky_down": self._load_inky_texture_down(),
            "clyde_right": self._load_clyde_texture_right(),
            "clyde_left": self._load_clyde_texture_left(),
            "clyde_up": self._load_clyde_texture_up(),
            "clyde_down": self._load_clyde_texture_down(),
            "fleeing": self._load_fleeing_texture()
        }
        rl.unload_image(self.sheet)
        return (textures)

    def _get_sprite(self, x: int, y: int) -> rl.Texture2D:
        image = rl.image_from_image(self.sheet, rl.Rectangle(
            x * self.tile_size, y * self.tile_size,
            self.tile_size, self.tile_size
        ))
        return (rl.load_texture_from_image(image))

    # -- PACMAN --
    def _load_pacman_texture_right(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 0),
                self._get_sprite(1, 0)
            ]
        )

    def _load_pacman_texture_left(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 1),
                self._get_sprite(1, 1)
            ]
        )

    def _load_pacman_texture_up(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 2),
                self._get_sprite(1, 2)
            ]
        )

    def _load_pacman_texture_down(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 3),
                self._get_sprite(1, 3)
            ]
        )

    # -- BLINKY --
    def _load_blinky_texture_right(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 4),
                self._get_sprite(1, 4)
            ]
        )

    def _load_blinky_texture_left(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(2, 4),
                self._get_sprite(3, 4)
            ]
        )

    def _load_blinky_texture_up(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(4, 4),
                self._get_sprite(5, 4)
            ]
        )

    def _load_blinky_texture_down(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(6, 4),
                self._get_sprite(7, 4)
            ]
        )

    # -- PINKY --
    def _load_pinky_texture_right(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 5),
                self._get_sprite(1, 5)
            ]
        )

    def _load_pinky_texture_left(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(2, 5),
                self._get_sprite(3, 5)
            ]
        )

    def _load_pinky_texture_up(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(4, 5),
                self._get_sprite(5, 5)
            ]
        )

    def _load_pinky_texture_down(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(6, 5),
                self._get_sprite(7, 5)
            ]
        )

    # -- INKY --
    def _load_inky_texture_right(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 6),
                self._get_sprite(1, 6)
            ]
        )

    def _load_inky_texture_left(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(2, 6),
                self._get_sprite(3, 6)
            ]
        )

    def _load_inky_texture_up(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(4, 6),
                self._get_sprite(5, 6)
            ]
        )

    def _load_inky_texture_down(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(6, 6),
                self._get_sprite(7, 6)
            ]
        )

    # -- CLYDE --
    def _load_clyde_texture_right(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(0, 7),
                self._get_sprite(1, 7)
            ]
        )

    def _load_clyde_texture_left(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(2, 7),
                self._get_sprite(3, 7)
            ]
        )

    def _load_clyde_texture_up(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(4, 7),
                self._get_sprite(5, 7)
            ]
        )

    def _load_clyde_texture_down(self) -> list[rl.Texture2D]:
        return (
            [
                self._get_sprite(6, 7),
                self._get_sprite(7, 7)
            ]
        )

    def _load_fleeing_texture(self) -> rl.Texture2D:
        return (
            [
                self._get_sprite(8, 4),
                self._get_sprite(9, 4),
            ]
        )

    def _load_pacgum_texture(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            self.cell_size - 1, self.cell_size - 1, rl.BLACK)
        rl.image_draw_circle(image, self.cell_size // 2, self.cell_size //
                             2, self.cell_size // 10, rl.WHITE)
        return (rl.load_texture_from_image(image))

    def _load_superpacgum_texture(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            self.cell_size - 1, self.cell_size - 1, rl.BLACK)
        rl.image_draw_circle(image, self.cell_size // 2, self.cell_size //
                             2, self.cell_size // 5, rl.WHITE)
        return (rl.load_texture_from_image(image))
