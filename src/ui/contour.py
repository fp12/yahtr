from kivy.graphics import Color, Line

from ui.colored_widget import ColoredWidget


class Contour(ColoredWidget):
    def __init__(self, shape, layout, **kwargs):
        super(Contour, self).__init__(**kwargs)
        self.hex_layout = layout

        edges_points = {}
        for shape_part in shape:
            corners = self.hex_layout.polygon_corners(shape_part, add_margin=True)
            for index, neighbour in enumerate(shape_part.get_neighbours()):
                if neighbour not in shape:
                    corrected_index1 = (index + 4) % 6
                    corrected_index2 = (index + 5) % 6
                    corner1 = corners[corrected_index1] - self.hex_layout.origin
                    corner2 = corners[corrected_index2] - self.hex_layout.origin
                    edges_points.update({corner1: corner2})

        step = 0
        self.lines = []
        current_point = None
        current_line = []
        while len(edges_points) > 0:
            if not current_point:
                if current_line:
                    current_line.append(current_line[0])
                    current_line.append(current_line[1])
                    self.lines.append(current_line)
                p0, current_point = edges_points.popitem()
                current_line = [p0.x, p0.y, current_point.x, current_point.y]
            else:
                current_point = edges_points.pop(current_point, None)
                if current_point:
                    current_line.append(current_point.x)
                    current_line.append(current_point.y)
                else:
                    if current_line:
                        current_line.append(current_line[0])
                        current_line.append(current_line[1])
                        self.lines.append(current_line)
                    p0, current_point = edges_points.popitem()
                    current_line = [p0.x, p0.y, current_point.x, current_point.y]
            step += 1
        if current_line:
            current_line.append(current_line[0])
            current_line.append(current_line[1])
            self.lines.append(current_line)

    def redraw(self):
        self.canvas.clear()
        if self.a == 0:
            return

        with self.canvas:
            Color(r=self.r, g=self.g, b=self.b, a=self.a)
            for line in self.lines:
                points = []
                for i, offset in enumerate(line):
                    if i % 2 == 0:
                        points.append(offset + self.x)
                    else:
                        points.append(offset + self.y)
                Line(points=points, width=3, joint='bevel')

    def on_pos(self, *args):
        if not self.get_root_window():
            return False
        self.redraw()

    def on_a(self, *args):
        if not self.get_root_window():
            return False
        self.redraw()
