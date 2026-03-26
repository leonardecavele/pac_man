from .entity import Entity

from src.maze import Maze
from src.type import vec2


class Pac_man(Entity):
    def __init__(
        self, screen_pos: vec2, maze_pos: vec2, sprite: str, m: Maze
    ) -> None:
        super().__init__(screen_pos, maze_pos, sprite, m)
        self.input: None | str = None

    # called every tick
    def update(self):
        # check input to update direction
        x, y = self.maze_pos

        if self.input is None:
            return
        elif (
            self.Input.up(self.input)
            and not self.maze.maze[y][x].top
        ):
            self.direction = Maze.Direction.TOP.value
        elif (
            self.Input.right(self.input)
            and not self.maze.maze[y][x].right
        ):
            self.direction = Maze.Direction.RIGHT.value
        elif (
            self.Input.down(self.input)
            and not self.maze.maze[y][x].bot
        ):
            self.direction = Maze.Direction.BOT.value
        elif (
            self.Input.left(self.input)
            and not self.maze.maze[y][x].left
        ):
            self.direction = Maze.Direction.LEFT.value
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
