from dataclasses import dataclass
from enum import Enum, auto

from src.entity import Entity, Ghost

from .maze_input import MazeInputState
from .maze_state import MazeState


class MazeActionType(Enum):
    NONE = auto()
    VICTORY = auto()
    GAME_OVER = auto()


@dataclass(slots=True)
class MazeAction:
    type: MazeActionType
    score: int = 0


class MazeController:
    def update(
        self, state: MazeState, dt: float, inputs: MazeInputState
    ) -> MazeAction:
        self._update_timers(state, dt)
        self._apply_input(state, inputs)
        self._update_collectibles(state, dt)
        self._update_pac_man(state, dt)
        self._update_ghosts(state, dt)

        collectible_action = self._resolve_collectible_collisions(state)
        if collectible_action.type != MazeActionType.NONE:
            return collectible_action

        ghost_action = self._resolve_ghost_collisions(state)
        if ghost_action.type != MazeActionType.NONE:
            return ghost_action

        return MazeAction(MazeActionType.NONE)

    def _update_timers(self, state: MazeState, dt: float) -> None:
        state.timer += dt

        if state.fright:
            state.fright_time += dt
            if state.fright_time >= state.fright_duration:
                state.end_fright_mode()
            return

        state.ghost_schedule_time += dt
        next_mode = self._ghost_mode_at(state)
        if next_mode == state.current_ghost_mode:
            return

        state.current_ghost_mode = next_mode
        for ghost in state.ghosts:
            if ghost.state in (Ghost.State.FRIGHTENED, Ghost.State.EATEN):
                ghost.saved_state = next_mode
                continue
            ghost.change_state(next_mode)
            ghost.update()

    def _ghost_mode_at(self, state: MazeState) -> Ghost.State:
        for time_limit, ghost_state in state.ghost_behavior.items():
            if state.ghost_schedule_time <= time_limit:
                return ghost_state
        return Ghost.State.CHASE

    def _apply_input(self, state: MazeState, inputs: MazeInputState) -> None:
        if inputs.direction is not None:
            state.pac_man.input = inputs.direction

    def _update_collectibles(self, state: MazeState, dt: float) -> None:
        for collectible in state.collectibles:
            collectible.update(dt)

    def _update_pac_man(self, state: MazeState, dt: float) -> None:
        pac_man = state.pac_man
        pac_man.update(dt)

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

        pac_man.update()

    def _update_ghosts(self, state: MazeState, dt: float) -> None:
        for ghost in state.ghosts:
            if not ghost.released:
                release_time = state.ghost_release_schedule.get(
                    ghost.identifier, 0.0
                )
                if state.ghost_schedule_time < release_time:
                    continue
                ghost.released = True
                ghost.exiting_house = True
                ghost.direction = (0, 0)
                ghost.origin_cell = None
                ghost.target_cell = None

            if ghost.exiting_house:
                self._update_ghost_house_exit(state, ghost, dt)
                continue

            ghost.update(dt)

            if ghost.target_cell is None:
                continue

            target_screen_pos = state.geometry.maze_to_screen(ghost.target_cell)
            reached = ghost.move_to_target(dt, target_screen_pos)
            if not reached:
                continue

            ghost.screen_pos = target_screen_pos
            ghost.maze_pos = ghost.target_cell
            ghost.origin_cell = None
            ghost.target_cell = None

            if ghost.state == Ghost.State.EATEN and ghost.maze_pos == ghost.house:
                ghost.load_save()

            ghost.update()

    def _update_ghost_house_exit(
        self, state: MazeState, ghost: Ghost, dt: float
    ) -> None:
        if ghost.target_cell is None:
            next_direction = ghost.a_star_direction(ghost.house_exit)
            if next_direction is None:
                ghost.exiting_house = False
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

    def _resolve_collectible_collisions(self, state: MazeState) -> MazeAction:
        for collectible in state.collectibles[:]:
            if not self._collides(state, collectible, state.pac_man):
                continue
            state.collectibles.remove(collectible)
            collectible.on_collect(state)
            if not state.collectibles:
                return self._finish_level(state, MazeActionType.VICTORY)
            return MazeAction(MazeActionType.NONE)
        return MazeAction(MazeActionType.NONE)

    def _resolve_ghost_collisions(self, state: MazeState) -> MazeAction:
        for ghost in state.ghosts:
            if not self._collides(state, ghost, state.pac_man):
                continue
            if ghost.state == Ghost.State.FRIGHTENED:
                ghost.change_state(Ghost.State.EATEN)
                ghost.update()
                state.score += state.config.points_per_ghost
                return MazeAction(MazeActionType.NONE)
            if ghost.state == Ghost.State.EATEN:
                continue
            return self._finish_level(state, MazeActionType.GAME_OVER)
        return MazeAction(MazeActionType.NONE)

    def _finish_level(
        self, state: MazeState, action_type: MazeActionType
    ) -> MazeAction:
        final_score = state.score
        state.reset()
        return MazeAction(type=action_type, score=final_score)

    def _collides(self, state: MazeState, first: Entity, second: Entity) -> bool:
        size: int = state.geometry.cell_size // 2
        return (
            abs(first.screen_pos[0] - second.screen_pos[0]) < size
            and abs(first.screen_pos[1] - second.screen_pos[1]) < size
        )
