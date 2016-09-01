from kivy.graphics import Line, Color

from ui.colored_widget import ColoredWidget


class Trajectory(ColoredWidget):
    def __init__(self, **kwargs):
        super(Trajectory, self).__init__(**kwargs)
        self.hex_coords = []

    # override
    def hide(self, do_hide=True):
        if do_hide:
            self.canvas.clear()

    def set(self, hex_coords, points):
        self.hex_coords = hex_coords
        self.canvas.clear()
        with self.canvas:
            Color(self.r, self.g, self.b, self.a)
            Line(points=points, width=10, joint='bevel')
