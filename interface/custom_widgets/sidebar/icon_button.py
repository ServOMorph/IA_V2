from typing import Optional
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class IconButton(ButtonBehavior, Image):
    """
    Petit bouton icône générique.
    - Survole : fond léger arrondi
    - Taille contrôlée par icon_size / padding
    Doc de ref: §4 (séparation), §11 (dimensions), §5 (principes Kivy)
    """
    bg_color = ListProperty([0, 0, 0, 0])  # transparent par défaut
    hover_bg_color = ListProperty([1, 1, 1, 0.06])
    radius = ListProperty([dp(8)])
    padding_x = NumericProperty(dp(6))
    padding_y = NumericProperty(dp(6))
    source = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True
        with self.canvas.before:
            self._color_instr = Color(rgba=self.bg_color)
            self._bg = RoundedRectangle(radius=self.radius)
        self.bind(
            pos=self._update_rect,
            size=self._update_rect,
            bg_color=self._update_bg_color,
            radius=self._update_rect,
        )

    def _update_rect(self, *_):
        self._bg.pos = (self.x - self.padding_x, self.y - self.padding_y)
        self._bg.size = (self.width + 2 * self.padding_x, self.height + 2 * self.padding_y)

    def _update_bg_color(self, *_):
        self._color_instr.rgba = self.bg_color

    def on_enter(self):
        self.bg_color = self.hover_bg_color

    def on_leave(self):
        self.bg_color = [0, 0, 0, 0]

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            self.on_leave()
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_enter()
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.on_leave()
        return super().on_touch_up(touch)
