from __future__ import annotations

import pyray as rl


class Sounds:
    SOUND_PATHS: dict[str, str] = {
        "credit_sound": "assets/01. Credit Sound.flac",
        "start_music": "assets/02. Start Music.flac",
        "eating": "assets/03. PAC-MAN - Eating The Pac-dots.flac",
        "eating_corning": "assets/04. PAC-MAN - Turning The Corner While Eating The Pac-dots.flac",
        "extend_sound": "assets/05. Extend Sound.flac",
        "ghost_normal_move": "assets/06. Ghost - Normal Move.flac",
        "ghost_spurt_move_1": "assets/07. Ghost - Spurt Move #1.flac",
        "ghost_spurt_move_2": "assets/08. Ghost - Spurt Move #2.flac",
        "ghost_spurt_move_3": "assets/09. Ghost - Spurt Move #3.flac",
        "ghost_spurt_move_4": "assets/10. Ghost - Spurt Move #4.flac",
        "pac_man_eating_the_fruit": "assets/11. PAC-MAN - Eating The Fruit.flac",
        "ghost_turn_to_blue": "assets/12. Ghost - Turn to Blue.flac",
        "pac_man_eating_the_ghost": "assets/13. PAC-MAN - Eating The Ghost.flac",
        "ghost_return_to_home": "assets/14. Ghost - Return to Home.flac",
        "coffee_break_music": "assets/16. Coffee Break Music.flac",
        "game_play": "assets/17. Game Play.flac",
    }

    def __init__(self) -> None:
        self.sounds: dict[str, rl.Sound] = {}
        self._load_sounds()

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
