from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.properties import ObjectProperty


class EnumDropDown(Widget):
    dropdown = ObjectProperty()

    def __init__(self, enum_class, **kwargs):
        super(EnumDropDown, self).__init__(**kwargs)
        self.dropdown = DropDown()
        self.mainbutton = Button(text='Hello', size_hint=(None, None))
        self.mainbutton.bind(on_release=self.dropdown.open)

        for data in enum_class:
            # When adding widgets, we need to specify the height manually
            # (disabling the size_hint_y) so the dropdown can calculate
            # the area it needs.
            btn = Button(text=f'Value {data.name}', size_hint_y=None, height=44)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))

            # then add the button inside the dropdown
            self.dropdown.add_widget(btn)

        self.dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))

        self.add_widget(self.mainbutton)
