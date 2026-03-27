# PACMAN

## BRAIN STORM

original pacman assets
Config file in .cache
move -> wasd (handle other keyboards types) / hjkl / arrows
different ghots behaviours (like original or maybe custom)
cheat feature: auto win (pacman eats everything and sped up time)
cheat feature: increase remaining time
maze generated harder and harder
maybe fake crash at level 256 in reference of the original pacman
secret input combination in pause menu to enable cheat
RAYLIB
maybe online score leaderboard (dont forget not internet)
Dijkstra mc-like
60 FPS
interpolation pour mouvement fluide

Coord reel/ecran: -> Centre de l'entité

- affichage
- Determiner la tuile sur laquelle l'entité se trouve

Coord maze/logique:

- Collisions
- Calcul de pathfinding
- Autorisation de mouvement pacman

Loop:

- Faire les updates fantome toutes les nouvelles cases (x frames)
- Faire les updates pacman tous les ticks
- Deplacement des entité pixel par pixel (x pixel par tick) tous les ticks

## LEONARD

- Project setup
  - [X] Makefile
  - [ ] Build .exe

- Entity
  (method .init())
  (method .update())

  - [ ] Player
  - [X] Ghosts
  - [ ] Entity list (coordinates.. etc)

- Networking

  - [ ] Multiplayer online
  - [ ] (Online leaderboard)

- Game Mechanics

  - [ ] Score

- Front
  - [ ] Input
  - [ ] Sound

## REMI

- [ ] Parsing
- Display

  - [ ] Maze module integration
      - [ ] Precompute map shader
  - [ ] Menu
  - [ ] HUD
  - [ ] Pause
  - [ ] Cheat
  - [ ] Animation

- User Data

  - [ ] Highscore

- Architecture

  - [ ] Level scaling
