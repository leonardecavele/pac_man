import pyray as rl


class Textures:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size

    def _load_textures(self) -> dict[str, rl.Texture2D]:
        return ({
            "pacgum": self._load_pacgum_texture(),
            "super_pacgum": self._load_superpacgum_texture()
        })

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
