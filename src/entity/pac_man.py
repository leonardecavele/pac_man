from .entity import Entity
from src.maze import Tile
from src.type import vec2, maze


class Pac_man(Entity):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, maze: maze
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, maze)
        self.input: None | str = None

    # called every tick
    def update(self):
        # check input to update direction
        x, y = self.maze_pos

        if self.input is None:
            return
        elif self.Input.up(self.input) and not self.maze[y][x] & Tile.UP:
            self.direction = (0, -1)
        elif self.Input.right(self.input) and not self.maze[y][x] & Tile.RIGHT:
            self.direction = (1, 0)
        elif self.Input.down(self.input) and not self.maze[y][x] & Tile.DOWN:
            self.direction = (0, 1)
        elif self.Input.left(self.input) and not self.maze[y][x] & Tile.LEFT:
            self.direction = (-1, 0)
        else:
            # invalid key
            self.input = None

    class Input():
        @staticmethod
        def up(input: str) -> bool:
            return input.lower() == 'w' or input.lower() == 'k'

        @staticmethod
        def right(input: str) -> bool:
            return input.lower() == 'd' or input.lower() == 'l'

        @staticmethod
        def down(input: str) -> bool:
            return input.lower() == 's' or input.lower() == 'j'

        @staticmethod
        def left(input: str) -> bool:
            return input.lower() == 'a' or input.lower() == 'h'
