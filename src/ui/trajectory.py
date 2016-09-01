from kivy.graphics import Line, Color

from ui.colored_widget import ColoredWidget


class Trajectory(ColoredWidget):
    # override
    def hide(self, do_hide=True):
        if do_hide:
            self.canvas.clear()
        
    def set(self, points):
        self.canvas.clear()
        with self.canvas:
            Color(self.r, self.g, self.b, self.a)
            Line(points=points, width=10, joint='bevel')