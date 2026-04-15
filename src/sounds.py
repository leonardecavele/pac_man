from __future__ import annotations

import pyray as rl


class Sounds:
    """Manage loading, playing, pausing, and unloading all game sounds."""

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
        """Load all sounds from SOUND_PATHS and initialize playback state."""
        self.sounds: dict[str, rl.Sound] = {}
        self._load_sounds()
        self.munch_counter: int = 0
        self.current_ghost_sound: str | None = None
        self.paused_sounds: set[str] = set()

    def _load_sounds(self) -> None:
        """Load every sound declared in SOUND_PATHS into self.sounds."""
        for name, path in self.SOUND_PATHS.items():
            self.sounds[name] = rl.load_sound(path)

    def play_sound(self, name: str) -> None:
        """Play the sound identified by name, or do nothing if it does not exist."""
        sound: rl.Sound | None = self.sounds.get(name)
        if sound is None:
            return
        rl.play_sound(sound)

    def stop_sound(self, name: str) -> None:
        """Stop the sound identified by name, or do nothing if it does not exist."""
        sound: rl.Sound | None = self.sounds.get(name)
        if sound is None:
            return
        rl.stop_sound(sound)

    def unload_sounds(self) -> None:
        """Unload all sounds from GPU memory and clear the internal dictionary."""
        for sound in self.sounds.values():
            rl.unload_sound(sound)
        self.sounds.clear()

    def is_playing(self, name: str) -> bool:
        """Return True if the sound identified by name is currently playing."""
        sound: rl.Sound | None = self.sounds.get(name)
        if sound is None:
            return False
        return rl.is_sound_playing(sound)

    def pause_all_sounds(self) -> None:
        """Pause every currently playing sound and record them for later resume."""
        self.paused_sounds.clear()

        for name, sound in self.sounds.items():
            if rl.is_sound_playing(sound):
                rl.pause_sound(sound)
                self.paused_sounds.add(name)

    def resume_all_sounds(self) -> None:
        """Resume all sounds that were previously paused by pause_all_sounds."""
        for name in self.paused_sounds:
            sound: rl.Sound | None = self.sounds.get(name)
            if sound is None:
                continue
            rl.resume_sound(sound)

        self.paused_sounds.clear()

    def play_munch(self) -> None:
        """Play the next munch sound (alternating munch1/munch2) if none is active."""
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
        """Switch the active ghost ambient sound to name, stopping the previous one."""
        if self.current_ghost_sound == name:
            if not self.is_playing(name):
                self.play_sound(name)
            return

        if self.current_ghost_sound is not None:
            self.stop_sound(self.current_ghost_sound)

        self.play_sound(name)
        self.current_ghost_sound = name

    def stop_ghost_sound(self) -> None:
        """Stop the currently playing ghost ambient sound, if any."""
        if self.current_ghost_sound is None:
            return

        self.stop_sound(self.current_ghost_sound)
        self.current_ghost_sound = None
