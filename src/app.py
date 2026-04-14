import pyray as rl

from random import randint
from typing import cast

from src.display import Textures
from src.display.views import (
    EndView, GameView, MenuView, View, ViewEventType, InstructionView)
from src.maze import Maze, ClassicMaze, RandomMaze
from src.parsing import Config
from src.sounds import Sounds


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

        rl.set_trace_log_level(rl.LOG_NONE)
        rl.init_window(150, 150, self.title)
        rl.set_exit_key(rl.KEY_NULL)
        rl.init_audio_device()

        monitor: int = rl.get_current_monitor()
        monitor_width: int = rl.get_monitor_width(monitor)
        monitor_height: int = rl.get_monitor_height(monitor)

        initial_width = int(monitor_width * screen_ratio)
        initial_height = int(monitor_height * screen_ratio)

        self.base_width = initial_width
        self.base_height = initial_height
        self.min_width = max(640, self.base_width // 2)
        self.min_height = max(360, self.base_height // 2)

        rl.set_window_size(self.base_width, self.base_height)
        rl.set_window_position(
            monitor_width // 2 - self.base_width // 2,
            monitor_height // 2 - self.base_height // 2
        )
        rl.set_target_fps(self.fps)
        rl.set_window_state(rl.FLAG_WINDOW_RESIZABLE)
        rl.set_window_min_size(self.min_width, self.min_height)

        self.render_texture = rl.load_render_texture(
            self.base_width,
            self.base_height
        )

        tex_type = dict[str, dict[str, list[rl.Texture]] | list[rl.Texture]]
        self.textures: tex_type = Textures(18)._load_textures()
        self.sounds: Sounds = Sounds()

        self.views: dict[str, View] = {
            "main_menu": MenuView(
                width=self.base_width,
                height=self.base_height,
                textures=self.textures,
                sounds=self.sounds
            ),
            "end": EndView(
                width=self.base_width,
                height=self.base_height
            ),
            "instruction": InstructionView(
                width=self.base_width,
                height=self.base_height
            )
        }

        self.current_view: View = self.views["main_menu"]
        self.tick_rate: float = tick_rate
        self.tick_interval: float = 1.0 / self.tick_rate

    def _get_display_rect(self) -> rl.Rectangle:
        window_width = rl.get_screen_width()
        window_height = rl.get_screen_height()

        scale = min(
            window_width / self.base_width,
            window_height / self.base_height
        )

        dest_width = self.base_width * scale
        dest_height = self.base_height * scale
        dest_x = (window_width - dest_width) / 2
        dest_y = (window_height - dest_height) / 2

        return rl.Rectangle(dest_x, dest_y, dest_width, dest_height)

    def _update_mouse_mapping(self) -> None:
        dst = self._get_display_rect()

        rl.set_mouse_offset(int(-dst.x), int(-dst.y))
        rl.set_mouse_scale(
            self.base_width / dst.width,
            self.base_height / dst.height
        )

    def run(self) -> None:
        while not rl.window_should_close():
            self._update_mouse_mapping()

            dt: float = rl.get_frame_time()
            event = self.current_view.update(dt)

            if event.type == ViewEventType.QUIT:
                break

            if event.type == ViewEventType.CHANGE_VIEW:
                self.current_view = self.views[event.message]

            if event.type == ViewEventType.START_GAME:
                if event.message == "random":
                    self.maze = RandomMaze(12, 12, randint(0, 10**9))
                elif event.message == "classic":
                    self.maze = ClassicMaze()

                game_view: View = GameView(
                    maze=self.maze,
                    width=self.base_width,
                    height=self.base_height,
                    config=self.config,
                    textures=self.textures,
                    sounds=self.sounds
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

            rl.begin_texture_mode(self.render_texture)
            rl.clear_background(rl.BLACK)
            self.current_view.draw()
            rl.end_texture_mode()

            rl.begin_drawing()
            rl.clear_background(rl.BLACK)

            src = rl.Rectangle(
                0.0,
                0.0,
                float(self.base_width),
                float(-self.base_height)
            )
            dst = self._get_display_rect()

            rl.draw_texture_pro(
                self.render_texture.texture,
                src,
                dst,
                rl.Vector2(0, 0),
                0.0,
                rl.WHITE
            )

            rl.end_drawing()

        self._close_view()
        rl.unload_render_texture(self.render_texture)
        self.sounds.unload_sounds()
        rl.close_audio_device()
        rl.close_window()

    def _close_view(self) -> None:
        rl.set_window_min_size(0, 0)
        rl.set_mouse_offset(0, 0)
        rl.set_mouse_scale(1.0, 1.0)

        for view in self.views.values():
            view.close()

        if rl.is_window_maximized() or rl.is_window_fullscreen():
            rl.restore_window()

        width = rl.get_screen_width()
        height = rl.get_screen_height()
        anim_pos_x = float(-height)
        anim_timer = 0.0
        anim_time = 1
        anim_frame = 0
        anim_start_x = rl.get_window_position().x
        anim_original_width = width
        image = rl.load_image_from_screen()
        bg = rl.load_texture_from_image(image)
        rl.unload_image(image)

        while anim_timer < anim_time:
            dt = rl.get_frame_time()
            anim_timer += dt
            delta = dt * (width + height) / anim_time
            anim_pos_x += delta
            anim_frame += 1

            if anim_pos_x > 0:
                new_width = max(1, anim_original_width - int(anim_pos_x))
                new_x = int(anim_start_x + anim_pos_x)
                rl.set_window_position(new_x, int(rl.get_window_position().y))
                rl.set_window_size(new_width, height)

            src = rl.Rectangle(0, 0, 32, 32)
            _pac = cast(dict[str, list[rl.Texture]], self.textures["pac_man"])
            texture = _pac["right"][anim_frame // 8 % 2]

            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            bg_offset = -int(anim_pos_x) if anim_pos_x > 0 else 0
            rl.draw_texture(bg, bg_offset, 0, rl.WHITE)
            if anim_pos_x < 0:
                dst = rl.Rectangle(anim_pos_x, 0, height, height)
                rl.draw_rectangle(
                    0,
                    0,
                    int(anim_pos_x) + height // 2,
                    height,
                    rl.BLACK
                )
            else:
                dst = rl.Rectangle(0, 0, height, height)
                rl.draw_rectangle(0, 0, height // 2, height, rl.BLACK)

            rl.draw_texture_pro(
                texture,
                src,
                dst,
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
            rl.end_drawing()
