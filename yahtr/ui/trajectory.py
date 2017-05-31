from kivy.graphics import Line, Color

from yahtr.ui.base_widgets import ColoredWidget


class Trajectory(ColoredWidget):
    def __init__(self, **kwargs):
        super(Trajectory, self).__init__(color=[0, 0, 0, 0], **kwargs)
        self.steps = []

    # override
    def hide(self, do_hide=True):
        if do_hide:
            self.canvas.clear()

    def set(self, steps, points):
        self.steps = steps
        self.canvas.clear()
        with self.canvas:
            Color(self.r, self.g, self.b, self.a)
            Line(points=points, width=10, joint='bevel')
