from kivy.properties import NumericProperty
from kivy.animation import Animation

from yahtr.ui.hex_widget import HexWidget


class Selector(HexWidget):
    margin = NumericProperty(2)

    def setup(self, q, r, layout, radius=None):
        super(Selector, self).setup(q, r, layout, radius)
        self.margin = radius or self.hex_layout.margin
        self.animate()

    def animate(self, *args):
        Animation.cancel_all(self)
        target_margin = self.margin * 1.3
        anim = Animation(margin=target_margin,
                         duration=2,
                         t='out_cubic')
        anim += Animation(margin=self.margin,
                          duration=3)
        anim.bind(on_complete=self.animate)
        anim.start(self)
