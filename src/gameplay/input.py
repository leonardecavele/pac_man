from pydantic import BaseModel, Field

import pyray as rl

from src.maze import Maze
from src.type import vec2i, Direction


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


class GameInputState(BaseModel):
    direction: vec2i | None = Field(default=None)


class GameInputReader:
    def read(self) -> GameInputState:
        if any(rl.is_key_down(key) for key in UP_KEYS):
            return GameInputState(direction=Direction.TOP.value)
        if any(rl.is_key_down(key) for key in RIGHT_KEYS):
            return GameInputState(direction=Direction.RIGHT.value)
        if any(rl.is_key_down(key) for key in DOWN_KEYS):
            return GameInputState(direction=Direction.BOT.value)
        if any(rl.is_key_down(key) for key in LEFT_KEYS):
            return GameInputState(direction=Direction.LEFT.value)
        return GameInputState()
