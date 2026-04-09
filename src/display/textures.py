import pyray as rl


class Textures:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.tile_size = 32
        self.sheet: rl.Image | None = None

    def _load_textures(
        self,
    ) -> dict[str, dict[str, list[rl.Texture2D]] | list[rl.Texture2D]]:
        self.sheet = rl.load_image("assets/Sprite_Sheet.png")
        rl.image_color_replace(
            self.sheet,
            rl.BLACK,
            rl.Color(0, 0, 0, 0)
        )

        textures = {
            "pacgum": self._load_pacgum_textures(),
            "super_pacgum": self._load_superpacgum_textures(),
            "pac_man": self._load_pac_man_textures(),
            "blinky": self._load_blinky_textures(),
            "pinky": self._load_pinky_textures(),
            "inky": self._load_inky_textures(),
            "clyde": self._load_clyde_textures(),
            "fleeing": self._load_fleeing_textures(),
            "eaten": self._load_eaten_textures(),
            "blink": self._load_blink_textures()
        }

        rl.unload_image(self.sheet)
        self.sheet = None
        return textures

    def _get_sprite(self, x: int, y: int) -> rl.Texture2D:
        image = rl.image_from_image(
            self.sheet,
            rl.Rectangle(
                x * self.tile_size,
                y * self.tile_size,
                self.tile_size,
                self.tile_size,
            )
        )
        texture = rl.load_texture_from_image(image)
        rl.set_texture_filter(texture, rl.TEXTURE_FILTER_POINT)
        rl.unload_image(image)
        return texture

    def _load(self, positions: list[tuple[int, int]]) -> list[rl.Texture2D]:
        sprites: list[rl.Texture2D] = []
        for x, y in positions:
            sprites.append(self._get_sprite(x, y))
        return sprites

    def _load_directional_textures(
        self,
        right: list[tuple[int, int]],
        left: list[tuple[int, int]],
        up: list[tuple[int, int]],
        down: list[tuple[int, int]],
    ) -> dict[str, list[rl.Texture2D]]:
        return {
            "right": self._load(right),
            "left": self._load(left),
            "up": self._load(up),
            "down": self._load(down),
        }

    def _load_pac_man_textures(self) -> dict[str, list[rl.Texture2D]]:
        return {
            "right": self._load([(0, 0), (1, 0)]),
            "left": self._load([(0, 1), (1, 1)]),
            "up": self._load([(0, 2), (1, 2)]),
            "down": self._load([(0, 3), (1, 3)]),
            "dying": self._load(
                [
                    (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
                    (7, 0), (8, 0), (9, 0), (10, 0), (11, 0),
                    (12, 0), (13, 0), (13, 0), (13, 0), (13, 1)
                ]
            ),
        }

    def _load_blinky_textures(self) -> dict[str, list[rl.Texture2D]]:
        return self._load_directional_textures(
            right=[(0, 4), (1, 4)],
            left=[(2, 4), (3, 4)],
            up=[(4, 4), (5, 4)],
            down=[(6, 4), (7, 4)],
        )

    def _load_pinky_textures(self) -> dict[str, list[rl.Texture2D]]:
        return self._load_directional_textures(
            right=[(0, 5), (1, 5)],
            left=[(2, 5), (3, 5)],
            up=[(4, 5), (5, 5)],
            down=[(6, 5), (7, 5)],
        )

    def _load_inky_textures(self) -> dict[str, list[rl.Texture2D]]:
        return self._load_directional_textures(
            right=[(0, 6), (1, 6)],
            left=[(2, 6), (3, 6)],
            up=[(4, 6), (5, 6)],
            down=[(6, 6), (7, 6)],
        )

    def _load_clyde_textures(self) -> dict[str, list[rl.Texture2D]]:
        return self._load_directional_textures(
            right=[(0, 7), (1, 7)],
            left=[(2, 7), (3, 7)],
            up=[(4, 7), (5, 7)],
            down=[(6, 7), (7, 7)],
        )

    def _load_fleeing_textures(self) -> list[rl.Texture2D]:
        return self._load([(8, 4), (9, 4)])

    def _load_blink_textures(self) -> list[rl.Texture2D]:
        return self._load([(9, 4), (10, 4), (8, 4), (11, 4)])

    def _load_eaten_textures(self) -> dict[str, list[rl.Texture2D]]:
        return self._load_directional_textures(
            right=[(8, 5)],
            left=[(9, 5)],
            up=[(10, 5)],
            down=[(11, 5)]
        )

    def _load_pacgum_textures(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            128 - 1,
            128 - 1,
            rl.BLACK,
        )
        rl.image_draw_circle(
            image,
            128 // 2,
            128 // 2,
            128 // 12,
            rl.BEIGE,
        )
        texture = rl.load_texture_from_image(image)
        rl.unload_image(image)
        return texture

    def _load_superpacgum_textures(self) -> rl.Texture2D:
        image = rl.gen_image_color(
            128 - 1,
            128 - 1,
            rl.BLACK,
        )
        rl.image_draw_circle(
            image,
            128 // 2,
            128 // 2,
            128 // 5,
            rl.BEIGE,
        )
        texture = rl.load_texture_from_image(image)
        rl.unload_image(image)
        return texture
