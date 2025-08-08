from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from ..hover_sidebar_button import HoverSidebarButton
from .icon_button import IconButton


class HoverRow(BoxLayout):
    """
    Ligne horizontale : [ HoverSidebarButton (texte) | IconButton (ico_modifier) ]
    - L’icône est masquée par défaut et s’affiche au survol de la ligne.
    - Un clic sur l’icône ouvre un DropDown (petit menu déroulant) à proximité.

    Le survol est géré via Window.mouse_pos + collide_point (fiable dans une ScrollView).
    """
    def __init__(self, filename: str, btn: HoverSidebarButton, icon_source: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = 32
        self.spacing = 6

        self.filename = filename
        self.btn = btn

        # Icône cliquable (masquée tant que non survolée)
        self.icon = IconButton(
            source=icon_source,
            size_hint=(None, 1),
            width=20,
            opacity=0
        )

        # Menu déroulant (DropDown)
        self.menu = self._build_dropdown()

        # Clic sur l’icône -> ouverture/fermeture du menu
        self.icon.bind(on_release=self._toggle_menu)

        # Assemblage
        self.add_widget(self.btn)
        self.add_widget(self.icon)

        # Abonnement global au mouvement de souris
        Window.bind(mouse_pos=self._on_mouse_pos)
        Clock.schedule_once(self._prime_hover, 0)

    # ----- DropDown -----
    def _build_dropdown(self) -> DropDown:
        dd = DropDown(auto_dismiss=True, max_height=dp(150))
        for action in ("Renommer", "Supprimer"):
            item = Button(
                text=action,
                size_hint_y=None,
                height=dp(32),
                font_size=12,
                halign="left",
                valign="middle"
            )
            item.bind(size=lambda w, *_: setattr(w, "text_size", (w.width - dp(10), None)))
            item.bind(on_release=lambda w, a=action: self._on_menu_action(a))
            dd.add_widget(item)
        return dd

    def _toggle_menu(self, *_):
        if self.menu.attach_to is self.icon:
            try:
                self.menu.dismiss()
            except Exception:
                pass
        else:
            try:
                self.menu.open(self.icon)
            except Exception as e:
                print(f"[Sidebar] Erreur ouverture menu pour '{self.filename}': {e}")

    def _on_menu_action(self, action: str):
        print(f"[Sidebar] Action '{action}' sur conversation: {self.filename}")
        try:
            self.menu.dismiss()
        except Exception:
            pass

    # ----- Hover -----
    def _prime_hover(self, *_):
        self._on_mouse_pos(Window, Window.mouse_pos)

    def _on_mouse_pos(self, _window, pos):
        local_x, local_y = self.to_widget(*pos)
        inside = self.collide_point(local_x, local_y)
        self.icon.opacity = 1 if inside else 0

    def on_parent(self, *args):
        if self.parent is None:
            try:
                Window.unbind(mouse_pos=self._on_mouse_pos)
            except Exception:
                pass
