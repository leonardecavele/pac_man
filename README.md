*This project has been created as part of the 42 curriculum by ldecavel and relaforg.*

# Pac-Man

## Description

The **Pac-Man** project goal is to recreate a pacman game using an extern
maze generator package from the 42 **A-Maze_Ing** project.

## Instructions

### Requirements

- Python 3.12+
- `make`

### Installation & Run

```sh
make run
```

This sets up a virtual environment, installs all dependencies via Poetry, and launches the game with the default `config.json`.

To use a custom config file:

```sh
make run ARGS=path/to/config.json
```

### Build (standalone binary)

```sh
make build
```

Produces a single `pac-man` executable in `dist/` via Nuitka.

### Other targets

| Command | Description |
|---------|-------------|
| `make install` | Install runtime dependencies only |
| `make lint` | Run flake8 + mypy |
| `make clean` | Remove venv and caches |

## Resources

- [The Pacman Dossier](https://pacman.holenet.info)
- [Online Pacman game](https://pacman.live)
- [Claude](https://claude.ai)
- [Chatgpt](https://chatgpt.com)
- [Pacman wiki](https://pacman.fandom.com/wiki/)
- [Raylib Docs](https://electronstudio.github.io/raylib-python-cffi/pyray.html)
- [Google pacman](https://www.google.com/logos/2010/pacman10-i.html)
- [Pacman live](https://pacman.live/)

## Configuration

The config file is a custom JSON with comments file.
It support python-like (#) and C-like (//) comments, the syntax is otherwise the
exact same as a classic JSON.

Example:

```JSON
{
    # This is a comment
    // This also is a comment
    "lives": 2,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "level_max_time": 90
}
```

>[!NOTE]
> There is no default values

## Highscore

Highscores are saved at the end of a game, and linked to a chosen username.
Usernames are not unique, as you can play the game multiple times.
They are saved in a persistant file located in ~/.local/share/pacman.
Then on the main menu only the 10 bests score are displayed.

## Maze Generation

The **mazegenerator-00001-py3-none-any.whl** is installed and imported to generate
random maze to play Pac-Man on. It is made by 42 central based on the 42 A_Maze_ing
project (cf. [relaforg's a_maze_ing](https://github.com/relaforg/a_maze_ing), [ldecavel's a_maze_ing](https://github.com/parad0xe/a-maze-ing)... etc.)

## Implementation

The game is written in **Python 3.12+** using **raylib** (via the `pyray` bindings)
for rendering and audio. Maze data comes from the **mazegenerator** wheel, and game
configuration is parsed from a custom JSON-with-comments format validated by
**pydantic**.

The game loop runs at 60 FPS with a fixed tick rate for entity movement. Ghost AI
follows the original Pac-Man behaviour: scatter/chase cycles, per-ghost release
timers, and fright mode triggered by super-pacgums. Both a classic mode (original
maze) and a random mode (procedurally generated maze) are supported.

Quality is enforced with **mypy** for static typing and **flake8** for style,
both run automatically via a GitHub Actions CI pipeline on every push.

## General Software Architecture

The project is split into four main modules:

- **`src/entity/`** — Game entities: `Entity` base class, `Pac_man`, `Ghost`
  (subclassed into `Blinky`, `Pinky`, `Inky`, `Clyde`), and `Collectible`
  (pacgums and super-pacgums).
- **`src/gameplay/`** — Game logic: `GameState` holds all runtime state,
  `Controller` drives the game loop (movement, collisions, ghost AI),
  `InputHandler` maps key presses to directions, and `GeometryHelper` converts
  between maze coordinates and screen pixels.
- **`src/display/`** — Rendering: `Textures` generates all sprites procedurally,
  `MazeRenderer` draws the maze image once at load time, and the `views/` subpackage
  contains `MenuView`, `GameView`, and `EndView`, each implementing a common `View`
  interface consumed by `App`.
- **`src/parsing/`** — Config and maze file parsing, using pydantic for validation.

`App` (in `src/app.py`) wires everything together: it owns the views, the game
state, and the main loop, and handles view transitions (menu → game → end).

## Project Management

The project was managed collaboratively * using GitHub flow: features developed
on dedicated branches and merged into `dev` via pull requests, then merged to
`main` for stable releases.
