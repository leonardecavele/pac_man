import pyray as rl

from src.display.maze_scene_renderer import MazeSceneRenderer
from src.gameplay import (
    MazeActionType,
    MazeController,
    MazeGeometry,
    MazeInputReader,
    MazeState,
)
from src.maze import Maze
from src.parsing.config import Config

from .view import View, ViewEvent, ViewEventType


class MazeView(View):
    def __init__(
        self,
        maze: Maze,
        config: Config,
        textures: dict[str, rl.Texture2D],
        gap: int,
        cell_size: int,
        width: int = 720,
        height: int = 720,
    ) -> None:
        self.geometry = MazeGeometry(maze=maze, gap=gap, cell_size=cell_size)
        self.state = MazeState(
            maze=maze,
            config=config,
            textures=textures,
            geometry=self.geometry,
            cell_size=cell_size
        )
        self.controller = MazeController()
        self.input_reader = MazeInputReader()
        self.renderer = MazeSceneRenderer(
            maze_state=self.state,
            geometry=self.geometry,
            width=width,
            height=height,
        )

    def draw(self) -> None:
        self.renderer.draw()

    def update(self, dt: float) -> ViewEvent:
        action = self.controller.update(self.state, dt, self.input_reader.read())

        if action.type == MazeActionType.VICTORY:
            return ViewEvent(type=ViewEventType.END, message=f"victory:{action.score}")
        if action.type == MazeActionType.GAME_OVER:
            return ViewEvent(type=ViewEventType.END, message=f"game_over:{action.score}")
        return ViewEvent(type=ViewEventType.NONE)

    def close(self) -> None:
        self.renderer.close()
