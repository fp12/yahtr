from kivy.properties import NumericProperty

from ui.base_widgets import AngledWidget, AngledColoredWidget

from utils import Color


default_action_arrow_color = Color.red
default_unit_move_color = Color(0.05, 0.05, 0.85)
default_enemy_move_color = Color(0.85, 0.05, 0.05)


class ActionArrow(AngledColoredWidget):
    def __init__(self, color=default_action_arrow_color, **kwargs):
        super(ActionArrow, self).__init__(size_hint=(None, None), color=color, **kwargs)


class ActionUnitMove(AngledColoredWidget):
    pass


class ActionNMIMove(AngledColoredWidget):
    origin_x = NumericProperty()
    origin_y = NumericProperty()


class ActionBuilder(AngledWidget):
    def __init__(self, rk_skill, hex_coords, hex_layout, **kwargs):
        super(ActionBuilder, self).__init__(**kwargs)
        self.rk_skill = rk_skill
        self.hex_coords = hex_coords
        self.hex_layout = hex_layout
        self.build()

    def build(self):
        """ /!\ Spawning widgets NOT taking piece orientation into account !!! """
        for hun in self.rk_skill.skill.huns:
            for hit in hun.H:
                pos = self.hex_layout.get_mid_edge_position(hit.direction.origin, hit.direction.destination)
                pos -= self.hex_layout.origin
                pos += self.pos
                arrow = ActionArrow(angle=hit.direction.angle, pos=pos.tup)
                self.add_widget(arrow)

            if hun.U:
                if hun.U.move:
                    end_coords = self.hex_coords + hun.U.move.destination
                    pos = self.hex_layout.hex_to_pixel(end_coords).tup
                else:
                    pos = self.pos

                move_color = default_unit_move_color  # changed with checks
                move_indic = ActionUnitMove(angle=hun.U.orientation.angle,
                                            pos=pos,
                                            color=move_color,
                                            size=(self.hex_layout.size.x / 2, self.hex_layout.size.y / 2))
                self.add_widget(move_indic)

            for move_info in hun.N:
                origin_coords = self.hex_coords + move_info.move.origin
                origin_pos = self.hex_layout.hex_to_pixel(origin_coords)
                end_coords = self.hex_coords + move_info.move.destination
                end_pos = self.hex_layout.hex_to_pixel(end_coords)

                move_color = default_enemy_move_color  # changed with checks
                move_indic = ActionNMIMove(angle=0,
                                           pos=end_pos.tup,
                                           origin_x=origin_pos.x, origin_y=origin_pos.y,
                                           color=move_color,
                                           size=(self.hex_layout.size.x / 2, self.hex_layout.size.y / 2))
                self.add_widget(move_indic)
