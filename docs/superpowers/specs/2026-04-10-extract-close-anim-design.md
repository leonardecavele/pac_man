# Extract Close Animation — Design Spec

**Date:** 2026-04-10

## Goal

Play the pac-man close animation whenever the main app loop exits, regardless of which view is active or why the loop stopped (QUIT event, window close button, etc.).

## Current State

The close animation (`CLOSE_ANIM` state) lives entirely inside `MenuView`. It only plays when the user clicks the EXIT button from the menu. If the app closes from any other view or via the window close button, no animation plays.

## Design

### `app._close_view()` — inline the animation

Replace the current no-op `_close_view()` with a mini raylib draw loop that runs the close animation directly. The method has access to `self.textures` and can read window dimensions via `rl.get_screen_width/height()`.

Animation logic (ported from `MenuView._draw_close_anim` and `_update_anim`):
- Pac-man starts off-screen left at `x = -height`
- Each frame, pac-man moves right; once `x > 0`, the window starts shrinking from the left
- Loop exits when `anim_timer >= anim_time` (currently `1` second)

### `MenuView` — remove `CLOSE_ANIM`

- Remove `State.CLOSE_ANIM` from the `State` enum
- Remove `_draw_close_anim()` method
- Remove `CLOSE_ANIM`-specific instance variables: `anim_start_x`, `anim_original_width`, `anim_width`, `anim_offset`
- EXIT button click: trigger `BTN_ANIM` as today, then `pending_event = ViewEvent(type=ViewEventType.QUIT)` — the animation now happens at app level
- Remove `CLOSE_ANIM` branch from `resize()` guard

## Flow After Change

```
Any cause of loop exit
  └─► app._close_view()  — plays pac-man window-shrink animation
  └─► rl.close_window()
```

## Files Changed

- `src/app.py` — `_close_view()` rewritten with animation loop
- `src/display/views/menu_view.py` — `CLOSE_ANIM` state and related code removed
