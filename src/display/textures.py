import pyray as rl


class Textures:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size

    def _load_textures(self) -> dict[str, rl.Texture2D]:
        return ({
            "pacgum": self._load_pacgum_texture(),
            "super_pacgum": self._load_superpacgum_texture(),
            "pac_man": self._load_pacman_texture(),
            "blinky": self._load_blinky_texture(),
            "pinky": self._load_pinky_texture(),
            "inky": self._load_inky_texture(),
            "clyde": self._load_clyde_texture()
        })

    def _load_pacman_texture(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            self.cell_size - 1, self.cell_size - 1, rl.BLACK)
        rl.image_draw_rectangle(
            image, 4, 4, self.cell_size - 8, self.cell_size - 8, rl.YELLOW
        )
        return (rl.load_texture_from_image(image))

    def _load_blinky_texture(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            self.cell_size - 1, self.cell_size - 1, rl.BLACK)
        rl.image_draw_rectangle(
            image, 4, 4, self.cell_size - 8, self.cell_size - 8, rl.RED
        )
        return (rl.load_texture_from_image(image))

    def _load_pinky_texture(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            self.cell_size - 1, self.cell_size - 1, rl.BLACK)
        rl.image_draw_rectangle(
            image, 4, 4, self.cell_size - 8, self.cell_size - 8, rl.PINK
        )
        return (rl.load_texture_from_image(image))

    def _load_inky_texture(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            self.cell_size - 1, self.cell_size - 1, rl.BLACK)
        rl.image_draw_rectangle(
            image, 4, 4, self.cell_size - 8, self.cell_size - 8, rl.SKYBLUE
        )
        return (rl.load_texture_from_image(image))

    def _load_clyde_texture(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            self.cell_size - 1, self.cell_size - 1, rl.BLACK)
        rl.image_draw_rectangle(
            image, 4, 4, self.cell_size - 8, self.cell_size - 8, rl.ORANGE
        )
        return (rl.load_texture_from_image(image))

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
