from __future__ import annotations

import pyray as rl

from src.entity import Pac_man


class Sounds:
    SOUND_PATHS: dict[str, str] = {
        "dying": "assets/sounds/dying.flac",
        "ghost_normal_move": "assets/sounds/ghost_move.flac",
        "ghost_spurt_move_1": "assets/sounds/ghost_spurt_move_1.flac",
        "ghost_spurt_move_2": "assets/sounds/ghost_spurt_move_2.flac",
        "ghost_spurt_move_3": "assets/sounds/ghost_spurt_move_3.flac",
        "ghost_spurt_move_4": "assets/sounds/ghost_spurt_move_4.flac",
        "frightened": "assets/sounds/frightened.flac",
        "eating_ghost": "assets/sounds/eating_ghost.flac",
        "start_music": "assets/sounds/start_music.flac",
        "eaten": "assets/sounds/eaten.flac",
        "coffee_break_music": "assets/sounds/coffee_break_music.flac",
        "munch1": "assets/sounds/munch1.flac",
        "munch2": "assets/sounds/munch2.flac",
        "munch_corner": "assets/sounds/munch_corner.flac",
    }

    def __init__(self) -> None:
        self.sounds: dict[str, rl.Sound] = {}
        self._load_sounds()
        self.munch_counter: int = 0
        self.current_ghost_sound: str | None = None
        self.paused_sounds: set[str] = set()

    def _load_sounds(self) -> None:
        for name, path in self.SOUND_PATHS.items():
            self.sounds[name] = rl.load_sound(path)

    def play_sound(self, name: str) -> None:
        sound: rl.Sound | None = self.sounds.get(name)
        if sound is None:
            return
        rl.play_sound(sound)

    def stop_sound(self, name: str) -> None:
        sound: rl.Sound | None = self.sounds.get(name)
        if sound is None:
            return
        rl.stop_sound(sound)

    def unload_sounds(self) -> None:
        for sound in self.sounds.values():
            rl.unload_sound(sound)
        self.sounds.clear()

    def is_playing(self, name: str) -> bool:
        sound: rl.Sound | None = self.sounds.get(name)
        if sound is None:
            return False
        return rl.is_sound_playing(sound)

    def pause_all_sounds(self) -> None:
        self.paused_sounds.clear()

        for name, sound in self.sounds.items():
            if rl.is_sound_playing(sound):
                rl.pause_sound(sound)
                self.paused_sounds.add(name)

    def resume_all_sounds(self) -> None:
        for name in self.paused_sounds:
            sound: rl.Sound | None = self.sounds.get(name)
            if sound is None:
                continue
            rl.resume_sound(sound)

        self.paused_sounds.clear()

    def play_munch(self, pac_man: Pac_man) -> None:
        # working corner munch implementation but we dislike it

        # is_turning: bool = (
        #     pac_man.prev_direction != pac_man.direction
        #     and pac_man.prev_direction != (0, 0)
        # )
        #
        # if is_turning:
        #     self.stop_sound("munch1")
        #     self.stop_sound("munch2")
        #     if not self.is_playing("munch_corner"):
        #         self.play_sound("munch_corner")
        #         self.munch_counter += 1
        #     return

        if self.munch_counter % 2 == 0:
            munch: str = "munch1"
        else:
            munch = "munch2"

        if (
            not self.is_playing("munch1")
            and not self.is_playing("munch2")
            and not self.is_playing("munch_corner")
        ):
            self.play_sound(munch)
            self.munch_counter += 1

    def play_ghost_sound(self, name: str) -> None:
        if self.current_ghost_sound == name:
            if not self.is_playing(name):
                self.play_sound(name)
            return

        if self.current_ghost_sound is not None:
            self.stop_sound(self.current_ghost_sound)

        self.play_sound(name)
        self.current_ghost_sound = name

    def stop_ghost_sound(self) -> None:
        if self.current_ghost_sound is None:
            return

        self.stop_sound(self.current_ghost_sound)
        self.current_ghost_sound = None
