from inspect import cleandoc

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


Builder.load_file('yahtr/ui/kv/credits.kv')


class Credits(Screen):
    credits_text = StringProperty(cleandoc("""
        [b]Developer[/b]
        fp12 (Fabien Poupineau) [ref=https://twitter.com/fp12gaming][color=0000ff]@fp12gaming[/color][/ref]

        [b]Beta testers[/b]
        Jim & Juju

        [b]Software[/b]
        Python 3.6
        Kivy 10.10
        """))
