from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation  # <-- pour le fade

from ..hover_sidebar_button import HoverSidebarButton
from .icon_button import IconButton


NORMAL_BG = (0.20, 0.20, 0.20, 1)
HOVER_BG  = (0.30, 0.50, 0.80, 1)


class InlineMenu(BoxLayout):
    def __init__(self, on_action, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.spacing = dp(4)
        self.padding = (dp(6), dp(4), dp(6), dp(4))
        self.height = dp(32) * 2 + self.spacing + self.padding[1] + self.padding[3]
        self._buttons = []

        for action in ("Renommer", "Supprimer"):
            btn = Button(
                text=action,
                size_hint_y=None,
                height=dp(32),
                font_size=12,
                halign="left",
                valign="middle",
                background_normal="",
                background_color=NORMAL_BG,
            )
            btn.bind(size=lambda w, *_: setattr(w, "text_size", (w.width - dp(10), None)))
            btn.bind(on_release=lambda w, a=action: on_action(a))
            self.add_widget(btn)
            self._buttons.append(btn)

        Window.bind(mouse_pos=self._on_mouse_pos)
        Clock.schedule_once(lambda *_: self._on_mouse_pos(Window, Window.mouse_pos), 0)

    def _on_mouse_pos(self, _window, pos):
        for b in self._buttons:
            lx, ly = b.to_widget(*pos)
            inside = b.collide_point(lx, ly)
            b.background_color = HOVER_BG if inside else NORMAL_BG

    def on_parent(self, *args):
        if self.parent is None:
            try:
                Window.unbind(mouse_pos=self._on_mouse_pos)
            except Exception:
                pass


class HoverRow(BoxLayout):
    def __init__(self, filename: str, btn: HoverSidebarButton, icon_source: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.filename = filename
        self.btn = btn
        self.rename_callback = None
        self.delete_callback = None
        self.is_selected = False

        # --- HEADER ---
        self.header = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=32,
            spacing=6
        )
        with self.header.canvas.before:
            self._sel_color = Color(*HOVER_BG)
            self._sel_color.a = 0
            self._sel_rect = RoundedRectangle(radius=[0], pos=self.header.pos, size=self.header.size)
        self.header.bind(pos=self._update_header_rect, size=self._update_header_rect)

        self.icon = IconButton(
            source=icon_source,
            size_hint=(None, 1),
            width=20,
            opacity=0
        )
        self.icon.bind(on_release=self._toggle_menu)

        self.header.add_widget(self.btn)
        self.header.add_widget(self.icon)

        # --- MENU CONTAINER ---
        self.menu_container = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=0,
            opacity=0
        )
        self.menu_widget: InlineMenu | None = None

        self.add_widget(self.header)
        self.add_widget(self.menu_container)
        self.height = self.header.height

        Window.bind(mouse_pos=self._on_mouse_pos_header)
        Clock.schedule_once(self._prime_hover, 0)

    def _update_header_rect(self, *_):
        self._sel_rect.pos = self.header.pos
        self._sel_rect.size = self.header.size

    def set_selected(self, selected: bool):
        self.is_selected = selected

        # Animation sur le rectangle
        Animation.cancel_all(self._sel_color)
        anim = Animation(a=1.0 if selected else 0.0, d=0.2)
        anim.start(self._sel_color)

        # Animation sur l'icône
        Animation.cancel_all(self.icon)
        if selected:
            anim_icon = Animation(opacity=1, d=0.2)
        else:
            anim_icon = Animation(opacity=0 if not self._is_hovering_header() else 1, d=0.2)
            self._close_menu()
        anim_icon.start(self.icon)

        self.height = self.header.height + (self.menu_container.height if selected and self.menu_widget else 0)

    def _toggle_menu(self, *_):
        if self.menu_widget:
            self._close_menu()
        else:
            self._open_menu()

    def _open_menu(self):
        if self.menu_widget:
            return
        self.menu_widget = InlineMenu(on_action=self._on_menu_action)
        self.menu_container.clear_widgets()
        self.menu_container.add_widget(self.menu_widget)
        self.menu_container.height = self.menu_widget.height
        self.menu_container.opacity = 1
        self.height = self.header.height + self.menu_container.height

    def _close_menu(self):
        if not self.menu_widget:
            return
        self.menu_container.clear_widgets()
        self.menu_container.height = 0
        self.menu_container.opacity = 0
        self.menu_widget = None
        self.height = self.header.height

    def _on_menu_action(self, action: str):
        if action == "Renommer" and self.rename_callback:
            self.rename_callback(self.filename)
        elif action == "Supprimer" and self.delete_callback:
            self.delete_callback(self.filename)
        self._close_menu()

    def _prime_hover(self, *_):
        self._on_mouse_pos_header(Window, Window.mouse_pos)

    def _is_hovering_header(self):
        lx, ly = self.header.to_widget(*Window.mouse_pos)
        return self.header.collide_point(lx, ly)

    def _on_mouse_pos_header(self, _window, pos):
        if self.is_selected:
            return
        lx, ly = self.header.to_widget(*pos)
        inside = self.header.collide_point(lx, ly)
        Animation.cancel_all(self.icon)
        anim = Animation(opacity=1 if inside else 0, d=0.15)
        anim.start(self.icon)

    def on_parent(self, *args):
        if self.parent is None:
            try:
                Window.unbind(mouse_pos=self._on_mouse_pos_header)
            except Exception:
                pass
