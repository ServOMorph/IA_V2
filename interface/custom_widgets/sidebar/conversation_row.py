from typing import Callable, Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from config import (
    FONT_SIZE,
    SIDEBAR_ROW_HEIGHT,
    SIDEBAR_ICON_SIZE,
    SIDEBAR_ICON_PADDING,
    MENU_ACTIONS,
    ICON_MORE_PATH,
)
from .icon_button import IconButton


class ConversationRow(BoxLayout):
    """
    Ligne d'une conversation :
    - titre + preview (Label)
    - bouton menu (IconButton) → DropDown avec MENU_ACTIONS
    Gestion du hover (fond léger), cf. Doc §5 et §11.
    """

    title = StringProperty("")
    preview = StringProperty("")
    filename = StringProperty("")
    on_select = ObjectProperty(None, allownone=True)
    on_rename = ObjectProperty(None, allownone=True)
    on_delete = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(SIDEBAR_ROW_HEIGHT)
        self.padding = (dp(10), 0, dp(6), 0)
        self.spacing = dp(8)

        with self.canvas.before:
            self._bg_color = Color(rgba=(1, 1, 1, 0))
            self._bg_rect = RoundedRectangle(radius=[dp(10)])

        # Contenu texte
        text_lbl = Label(
            text=self._compose_text(self.title, self.preview),
            markup=True,
            halign="left",
            valign="middle",
            font_size=FONT_SIZE,
            text_size=(0, None),
            size_hint_x=1,
        )
        self._text_lbl = text_lbl

        # Bouton "..."
        menu_btn = IconButton(
            source=ICON_MORE_PATH,
            size_hint=(None, None),
            size=(dp(SIDEBAR_ICON_SIZE[0]), dp(SIDEBAR_ICON_SIZE[1])),
            padding_x=dp(SIDEBAR_ICON_PADDING[0]),
            padding_y=dp(SIDEBAR_ICON_PADDING[1]),
        )
        menu_btn.bind(on_release=lambda *_: self._open_menu(menu_btn))
        self._menu_btn = menu_btn

        self.add_widget(text_lbl)
        self.add_widget(menu_btn)

        Window.bind(mouse_pos=self._on_mouse_pos)
        self.bind(pos=self._update_bg, size=self._update_bg, title=self._refresh_text, preview=self._refresh_text)

    def on_kv_post(self, *_):
        self._update_bg()

    def on_parent(self, *_):
        # Clean le bind si la ligne disparaît (Doc §4 & §2)
        if self.parent is None:
            try:
                Window.unbind(mouse_pos=self._on_mouse_pos)
            except Exception:
                pass

    # ---- Hover / fond ----
    def _update_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_mouse_pos(self, _window, pos):
        if not self.get_root_window():
            return
        hovered = self.collide_point(*self.to_widget(*pos))
        self._bg_color.rgba = (1, 1, 1, 0.06) if hovered else (1, 1, 1, 0)

    # ---- Texte ----
    def _compose_text(self, title: str, preview: str) -> str:
        # Titre en gras + preview gris
        safe_title = title.replace("[", "\\[").replace("]", "\\]")
        safe_prev = preview.replace("[", "\\[").replace("]", "\\]")
        return f"[b]{safe_title}[/b]  [color=#8e8e93]{safe_prev}[/color]"

    def _refresh_text(self, *_):
        self._text_lbl.text = self._compose_text(self.title, self.preview)

    # ---- Menu actions ----
    def _open_menu(self, anchor_widget):
        dd = DropDown(auto_width=False, width=dp(180))
        for action in MENU_ACTIONS:
            btn = Button(text=action, size_hint_y=None, height=dp(36))
            btn.bind(on_release=lambda b, a=action: self._on_menu_select(a, dd))
            dd.add_widget(btn)
        dd.open(anchor_widget)

    def _on_menu_select(self, action: str, dd: DropDown):
        try:
            dd.dismiss()
        except Exception:
            pass

        if action == MENU_ACTIONS[0]:  # Renommer
            if callable(self.on_rename):
                self.on_rename(self.filename)
            else:
                print(f"[RENOMMER] {self.filename}")
        elif action == MENU_ACTIONS[1]:  # Supprimer
            if callable(self.on_delete):
                self.on_delete(self.filename)
            else:
                print(f"[SUPPRIMER] {self.filename}")

    # ---- Sélection ligne ----
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Si clic hors menu, on sélectionne
            if not self._menu_btn.collide_point(*self._menu_btn.to_widget(*touch.pos)):
                if callable(self.on_select):
                    self.on_select(self.filename)
                return True
        return super().on_touch_down(touch)
