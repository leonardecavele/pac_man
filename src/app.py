import pyray as rl

from src.display import Textures
from src.display.views import EndView, GameView, MenuView, View, ViewEventType
from src.maze import Maze, ClassicMaze, RandomMaze
from src.parsing import Config


class App:
    def __init__(
        self,
        config: Config,
        screen_ratio: float = 0.20,
        title: str = "pac_man",
        fps: int = 60,
        tick_rate: float = 8.0,
    ) -> None:
        self.maze: Maze
        self.title = title
        self.fps = fps
        self.config: Config = config

        rl.init_window(150, 150, self.title)

        monitor: int = rl.get_current_monitor()
        monitor_width: int = rl.get_monitor_width(monitor)
        monitor_height: int = rl.get_monitor_height(monitor)

        self.width = int(monitor_width * screen_ratio)
        self.height = int(monitor_height * screen_ratio)

        rl.set_window_size(self.width, self.height)
        rl.set_window_position(monitor_width // 2 - self.width // 2,
                               monitor_height // 2 - self.height // 2)
        rl.set_target_fps(self.fps)
        rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)

        self.textures: dict[str, rl.Texture2D] = Textures(
            18
        )._load_textures()
        self.views: dict[str, View] = {
            "main_menu": MenuView(
                width=self.width, height=self.height, textures=self.textures),
            "end": EndView(width=self.width, height=self.height),
        }

        self.current_view: View = self.views["main_menu"]
        self.tick_rate: float = tick_rate
        self.tick_interval: float = 1.0 / self.tick_rate

    def _compute_cell_gap_size(self) -> None:
        self.gap = 18
        margin = int(self.height * 0.2)
        while self.gap >= 0:
            self.cell_size = min(
                (self.width - margin - (self.maze.width + 1)
                 * self.gap) // self.maze.width,
                (self.height - margin - (self.maze.height + 1)
                 * self.gap) // self.maze.height,
            ) - 1
            if self.gap >= self.cell_size:
                self.gap -= 2
                continue
            break

    def run(self) -> None:
        while not rl.window_should_close():
            if (rl.is_window_resized()):
                self.current_view.resize()
            dt: float = rl.get_frame_time()
            event = self.current_view.update(dt)

            if event.type == ViewEventType.QUIT:
                break
            if (event.type == ViewEventType.CHANGE_VIEW):
                self.current_view = self.views[event.message]
            if event.type == ViewEventType.START_GAME:
                if event.message == "random":
                    self.maze = RandomMaze(12, 12, 13)
                elif event.message == "classic":
                    self.maze = ClassicMaze()
                self._compute_cell_gap_size()
                game_view: View = GameView(
                    maze=self.maze,
                    width=self.width,
                    height=self.height,
                    config=self.config,
                    textures=self.textures,
                    gap=self.gap,
                    cell_size=self.cell_size
                )
                self.views[event.message] = game_view
                self.current_view = self.views[event.message]
                continue
            if event.type == ViewEventType.END:
                action, score = event.message.split(":")
                self.current_view = self.views["end"]
                if isinstance(self.current_view, EndView):
                    self.current_view.action = action
                    self.current_view.score = int(score)
                continue

            rl.begin_drawing()
            self.current_view.draw()
            rl.end_drawing()

        self._close_view()
        rl.close_window()

    def _close_view(self) -> None:
        for view in self.views.values():
            view.close()
