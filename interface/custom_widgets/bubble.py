from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock

from config import (
    FONT_SIZE, TEXT_COLOR, BUBBLE_PADDING, BUBBLE_WIDTH_RATIO,
    BUBBLE_USER_COLOR, BUBBLE_IA_COLOR, BORDER_RADIUS
)


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
