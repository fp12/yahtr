from kivy.properties import NumericProperty, StringProperty
from kivy.uix.scatter import Scatter

from ui.base_widgets import AngledWidget, AngledColoredWidget

from utils import Color
import skill


default_action_arrow_color = Color.red
default_unit_move_color = Color(0.05, 0.05, 0.85)
default_enemy_move_color = Color(0.85, 0.05, 0.05)


class ActionArrow(Scatter):
    source = StringProperty(None)

    img_mapping = {skill.Effect.damage: '../data/img/red_arrow.png',
                   skill.Effect.heal: '../data/img/green_arrow.png'}

    def __init__(self, hit, **kwargs):
        source = ActionArrow.img_mapping[hit.effects[0]]
        super(ActionArrow, self).__init__(source=source, rotation=hit.direction.angle, scale=.4, **kwargs)


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
                arrow = ActionArrow(hit, center=pos.tup)
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
