from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock

from config import (
    FONT_SIZE, BORDER_RADIUS, TEXT_COLOR, BUBBLE_PADDING,
    BUBBLE_WIDTH_RATIO, BUBBLE_USER_COLOR, BUBBLE_IA_COLOR
)

from .utils import lighten_color

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

class ImageHoverButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 1.0
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        self.opacity = 0.6 if inside else 1.0

class Bubble(Label):
    def __init__(self, text, is_user, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = FONT_SIZE
        self.color = TEXT_COLOR
        self.markup = True
        self.halign = 'left'
        self.valign = 'top'
        self.padding = BUBBLE_PADDING
        self.is_user = is_user
        self.size_hint = (None, None)
        self.text_size = (Window.width * BUBBLE_WIDTH_RATIO, None)
        self.bind(texture_size=self.setter('size'))

        Clock.schedule_once(self.init_background)

    def init_background(self, *args):
        color = BUBBLE_USER_COLOR if self.is_user else BUBBLE_IA_COLOR

        with self.canvas.before:
            Color(*color)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=BORDER_RADIUS)

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
