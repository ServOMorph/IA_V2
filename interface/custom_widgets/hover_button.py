from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window

from config import BORDER_RADIUS
from interface.utils import lighten_color


class HoverButton(Button):
    def __init__(self, base_color=(0.4, 0.4, 0.4, 1), radius=BORDER_RADIUS, **kwargs):
        super().__init__(**kwargs)
        self.base_color = base_color
        self.radius = radius
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = kwargs.get("font_size", 14)

        with self.canvas.before:
            Color(*self.base_color)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

        self.bind(pos=self.update_bg, size=self.update_bg)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            new_color = lighten_color(self.base_color, 0.1)
        else:
            new_color = self.base_color
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*new_color)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
