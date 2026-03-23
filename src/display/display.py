from mazegenerator import MazeGenerator
# from pyray import *
import pyray as rl


class Display:
    def __init__(self):
        self.generator = MazeGenerator()
        self.generator.generate(42)
        self.maze = self.generator.maze
        print(self.maze)
        rl.init_window(1080, 720, "Pac-Man")
        rl.set_target_fps(60)

        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            rl.end_drawing()

        rl.close_window()
