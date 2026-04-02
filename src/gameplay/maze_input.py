from dataclasses import dataclass

import pyray as rl

from src.maze import Maze
from src.type import vec2i


UP_KEYS: list[int] = [
    rl.KEY_UP,
    rl.KEY_W,
    rl.KEY_Z,
    rl.KEY_K,
]

RIGHT_KEYS: list[int] = [
    rl.KEY_RIGHT,
    rl.KEY_D,
    rl.KEY_L,
]

DOWN_KEYS: list[int] = [
    rl.KEY_DOWN,
    rl.KEY_S,
    rl.KEY_J,
]

LEFT_KEYS: list[int] = [
    rl.KEY_LEFT,
    rl.KEY_A,
    rl.KEY_Q,
    rl.KEY_H,
]


@dataclass(slots=True)
class MazeInputState:
    direction: vec2i | None = None


class MazeInputReader:
    def read(self) -> MazeInputState:
        if any(rl.is_key_down(key) for key in UP_KEYS):
            return MazeInputState(direction=Maze.Direction.TOP.value)
        if any(rl.is_key_down(key) for key in RIGHT_KEYS):
            return MazeInputState(direction=Maze.Direction.RIGHT.value)
        if any(rl.is_key_down(key) for key in DOWN_KEYS):
            return MazeInputState(direction=Maze.Direction.BOT.value)
        if any(rl.is_key_down(key) for key in LEFT_KEYS):
            return MazeInputState(direction=Maze.Direction.LEFT.value)
        return MazeInputState()
