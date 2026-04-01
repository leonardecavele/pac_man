import math

import pyray as rl

from src.display.views.view import View, ViewEvent, ViewEventType
from src.display.views import EndView, MazeView, MenuView
from src.maze import Maze
from src.type import vec2
from src.display import Textures
from src.parsing.config import Config


class Game:
    def __init__(
        self,
        maze: Maze,
        config: Config,
        width: int = 720,
        height: int = 720,
        title: str = "pac_man",
        fps: int = 60,
        tick_rate: float = 8.0,
    ) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.title = "Pac-Man"
        rl.init_window(self.width, self.height, self.title)
        rl.set_target_fps(self.fps)
        self.maze: Maze = maze
        self.config: Config = config
        self._compute_cell_gap_size()
        self.textures: dict[str, rl.Texture2D] = Textures(
            self.cell_size
        )._load_textures()
        self.views: dict[str, View] = {
            "maze": MazeView(
                maze=maze,
                width=width,
                height=height,
                config=self.config,
                textures=self.textures,
                gap=self.gap,
                cell_size=self.cell_size
            ),
            "main_menu": MenuView(
                width=width,
                height=height
            ),
            "end": EndView(
                width=width,
                height=height
            )
        }
        self.current_view = self.views["main_menu"]
        self.score: int = 0
        self.timer: float = 0.0
        self.fright: bool = False
        self.fright_time: float = 0

        self.tick_rate: float = tick_rate
        self.tick_interval: float = 1.0 / self.tick_rate
        self.tick_accumulator: float = 0.0

    def _compute_cell_gap_size(self) -> None:
        self.gap = 18
        while self.gap >= 0:
            self.cell_size = min(
                (self.width - (self.maze.width + 1) * self.gap)
                // self.maze.width,
                (self.height - (self.maze.height + 1) * self.gap)
                // self.maze.height,
            ) - 1
            if self.gap >= self.cell_size:
                self.gap -= 2
                continue
            break

    def run(self) -> None:
        while not rl.window_should_close():
            dt: float = rl.get_frame_time()
            event = self.current_view.update(dt)
            if (event.type == ViewEventType.QUIT):
                break
            elif (event.type == ViewEventType.CHANGE_VIEW):
                self.current_view = self.views[event.message]
                continue
            elif (event.type == ViewEventType.END):
                action, score = event.message.split(":")
                self.current_view = self.views["end"]
                if (isinstance(self.current_view, EndView)):
                    self.current_view.action = action
                    self.current_view.score = int(score)
                continue
            rl.begin_drawing()
            self.current_view.draw()
            rl.end_drawing()

        self._close_view()
        rl.close_window()

    def _close_view(self):
        for view in self.views.values():
            view.close()
