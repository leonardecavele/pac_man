from pydantic import BaseModel, Field
from enum import Enum, auto

from src.entity import Entity, Ghost, SuperPacgum
from src.sounds import Sounds

from .input import GameInputState
from .state import GameState


class GameActionType(Enum):
    NONE = auto()
    VICTORY = auto()
    GAME_OVER = auto()


class GameAction(BaseModel):
    type: GameActionType = Field(...)
    score: int = Field(default=0)


class GameController:
    def __init__(self, sounds: Sounds) -> None:
        self.sounds = sounds

    def update(
        self, state: GameState, dt: float, inputs: GameInputState
    ) -> GameAction:
        if state.timer - state.last_pacgum_eat_time > 0.10:
            self.sounds.munch_counter = 0
        if self.sounds.is_playing("start_music"):
            self._apply_input(state, inputs)
            return GameAction(type=GameActionType.NONE)

        if state.freeze_time > 0.0:
            state.freeze_time -= dt
            self._update_collectibles(state, dt)
            self._apply_input(state, inputs)
            return GameAction(type=GameActionType.NONE)

        if state.pac_man.dying:
            state.ghosts = []
            self._update_pac_man(state, dt)
            if not state.pac_man.dying:
                state.start = True
                state.timer = 0
                state.freeze(2)
                if state.HP < 1:
                    return self._finish_level(state, GameActionType.GAME_OVER)
                self._retry_level(state)
            return GameAction(type=GameActionType.NONE)

        self._update_timers(state, dt)
        self._apply_input(state, inputs)
        self._update_pac_man(state, dt)
        self._update_collectibles(state, dt)
        self._update_ghosts(state, dt)
        self._update_ghost_sound(state)

        collectible_action = self._resolve_collectible_collisions(state)
        if collectible_action.type != GameActionType.NONE:
            return collectible_action

        ghost_action = self._resolve_ghost_collisions(state)
        if ghost_action.type != GameActionType.NONE:
            state.pac_man.dying = True
            if not self.sounds.is_playing("dying"):
                self.sounds.play_sound("dying")
            state.HP -= 1

        return GameAction(type=GameActionType.NONE)

    def _update_timers(self, state: GameState, dt: float) -> None:
        state.timer += dt

        if state.fright:
            state.fright_time += dt
            if state.fright_time >= state.fright_duration:
                state.end_fright_mode()
            elif (state.fright_time >= state.fright_duration - 2.25):
                state.blink_fright_mode()
            return

        state.ghost_schedule_time += dt
        next_mode = self._ghost_mode_at(state)
        if next_mode == state.current_ghost_mode:
            return

        state.current_ghost_mode = next_mode
        for ghost in state.ghosts:
            if ghost.state in (
                Ghost.State.FRIGHTENED, Ghost.State.EATEN, Ghost.State.BLINK
            ):
                ghost.saved_state = next_mode
                continue
            ghost.change_state(next_mode)
            ghost.update()

    def _ghost_mode_at(self, state: GameState) -> Ghost.State:
        for time_limit, ghost_state in state.ghost_behavior.items():
            if state.ghost_schedule_time <= time_limit:
                return ghost_state
        return Ghost.State.CHASE

    def _apply_input(self, state: GameState, inputs: GameInputState) -> None:
        if inputs.direction is not None:
            state.pac_man.input = inputs.direction

    def _update_collectibles(self, state: GameState, dt: float) -> None:
        for collectible in state.collectibles:
            collectible.update(dt)

    def _update_pac_man(self, state: GameState, dt: float) -> None:
        pac_man = state.pac_man
        pac_man.animate(dt)
        pac_man.update()

        if pac_man.target_cell is not None:
            pac_man.try_corner(state.geometry.maze_to_screen)

        if pac_man.target_cell is None:
            return

        target_screen_pos = state.geometry.maze_to_screen(pac_man.target_cell)
        reached = pac_man.move_to_target(dt, target_screen_pos)
        if not reached:
            return

        pac_man.screen_pos = target_screen_pos
        pac_man.maze_pos = pac_man.target_cell

        pac_man.origin_cell = None
        pac_man.target_cell = None

    def _update_ghosts(self, state: GameState, dt: float) -> None:
        for ghost in state.ghosts:
            ghost.animate()

            if not ghost.released:
                release_time = state.ghost_release_schedule.get(
                    ghost.identifier, 0.0
                )
                if state.ghost_schedule_time < release_time:
                    continue

                ghost.released = True
                ghost.exiting_house = True
                ghost.origin_cell = None
                ghost.target_cell = None

            if ghost.exiting_house:
                self._update_ghost_house_exit(state, ghost, dt)
                continue

            if ghost.target_cell is None:
                ghost.update()

            if ghost.target_cell is None:
                continue

            target_screen_pos = state.geometry.maze_to_screen(
                ghost.target_cell)
            reached = ghost.move_to_target(dt, target_screen_pos)
            if not reached:
                continue

            ghost.screen_pos = target_screen_pos
            ghost.maze_pos = ghost.target_cell
            ghost.origin_cell = None
            ghost.target_cell = None

            if ghost.state & Ghost.State.EATEN:
                target = ghost.compute_target()
                if target is not None and ghost.maze_pos == target:
                    ghost.load_save()

            ghost.update()

    def _update_ghost_house_exit(
        self, state: GameState, ghost: Ghost, dt: float
    ) -> None:
        if ghost.target_cell is None:
            next_direction = ghost.a_star_direction(ghost.house_exit)

            if next_direction is None:
                ghost.exiting_house = False
                ghost.direction = (0, 0)
                ghost.update()
                return

            ghost.direction = next_direction
            ghost.origin_cell = ghost.maze_pos
            ghost.target_cell = (
                ghost.maze_pos[0] + next_direction[0],
                ghost.maze_pos[1] + next_direction[1],
            )

        target_screen_pos = state.geometry.maze_to_screen(ghost.target_cell)
        reached = ghost.move_to_target(dt, target_screen_pos)
        if not reached:
            return

        ghost.screen_pos = target_screen_pos
        ghost.maze_pos = ghost.target_cell
        ghost.origin_cell = None
        ghost.target_cell = None

        if ghost.maze_pos == ghost.house_exit:
            ghost.exiting_house = False
            ghost.direction = (0, 0)
            ghost.update()

    def _update_elroy_state(self, state: GameState) -> None:
        if not state.ghosts:
            return

        blinky = state.ghosts[0]
        ratio = state.collectible_ratio_remaining()

        if blinky.state in (
            Ghost.State.FRIGHTENED, Ghost.State.EATEN, Ghost.State.BLINK
        ):
            if blinky.state & (Ghost.State.FRIGHTENED | Ghost.State.BLINK):
                if ratio <= 0.10:
                    blinky.saved_state = Ghost.State.ELROY2
                elif ratio <= 0.25:
                    blinky.saved_state = Ghost.State.ELROY1
                else:
                    blinky.saved_state = state.current_ghost_mode
            return

        if ratio <= 0.10:
            blinky.change_state(Ghost.State.ELROY2)
            blinky.update()
        elif ratio <= 0.25:
            blinky.change_state(Ghost.State.ELROY1)
            blinky.update()
        else:
            if blinky.state in (Ghost.State.ELROY1, Ghost.State.ELROY2):
                blinky.change_state(state.current_ghost_mode)
                blinky.update()

    def _resolve_collectible_collisions(self, state: GameState) -> GameAction:
        for collectible in state.collectibles[:]:
            if not self._collides(state, collectible, state.pac_man):
                continue
            state.last_pacgum_eat_time = state.timer
            self.sounds.play_munch(state.pac_man)
            state.collectibles.remove(collectible)
            collectible.on_collect(state)
            self._update_elroy_state(state)
            if isinstance(collectible, SuperPacgum):
                state.freeze(0.05)
            if not state.collectibles:
                return self._finish_level(state, GameActionType.VICTORY)
            return GameAction(type=GameActionType.NONE)
        return GameAction(type=GameActionType.NONE)

    def _resolve_ghost_collisions(self, state: GameState) -> GameAction:
        for ghost in state.ghosts:
            if not self._collides(state, ghost, state.pac_man):
                continue
            self.sounds.stop_sound("eating")
            if ghost.state & (Ghost.State.FRIGHTENED | Ghost.State.BLINK):
                ghost.change_state(Ghost.State.EATEN)
                ghost.update()
                state.score += state.config.points_per_ghost
                self.sounds.play_sound("eating_ghost")
                state.freeze(0.75)
                return GameAction(type=GameActionType.NONE)
            if ghost.state == Ghost.State.EATEN:
                continue
            self.sounds.stop_ghost_sound()
            state.freeze(0.75)
            return GameAction(type=GameActionType.GAME_OVER)
        return GameAction(type=GameActionType.NONE)

    def _retry_level(self, state: GameState) -> None:
        state.entity_reset()

    def _finish_level(
        self, state: GameState, action_type: GameActionType
    ) -> GameAction:
        final_score = state.score
        state.global_reset()
        return GameAction(type=action_type, score=final_score)

    def _collides(
        self, state: GameState, first: Entity, second: Entity
    ) -> bool:
        size: int = state.geometry.cell_size // 2
        return (
            abs(first.screen_pos[0] - second.screen_pos[0]) < size
            and abs(first.screen_pos[1] - second.screen_pos[1]) < size
        )

    def _update_ghost_sound(self, state: GameState) -> None:
        eaten: bool = False
        frightened: bool = False

        for ghost in state.ghosts:
            if ghost.state == Ghost.State.EATEN:
                eaten = True
            elif ghost.state in (Ghost.State.FRIGHTENED, Ghost.State.BLINK):
                frightened = True

        if eaten:
            self.sounds.play_ghost_sound("eaten")
            return

        if frightened:
            self.sounds.play_ghost_sound("frightened")
            return

        ratio = state.collectible_ratio_remaining()
        if ratio <= 0.10:
            self.sounds.play_ghost_sound("ghost_spurt_move_4")
            return
        elif ratio <= 0.25:
            self.sounds.play_ghost_sound("ghost_spurt_move_3")
            return
        elif ratio <= 0.40:
            self.sounds.play_ghost_sound("ghost_spurt_move_2")
            return
        elif ratio <= 0.55:
            self.sounds.play_ghost_sound("ghost_spurt_move_1")
            return
        else:
            self.sounds.play_ghost_sound("ghost_normal_move")
