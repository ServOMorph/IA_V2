from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button

from ..hover_sidebar_button import HoverSidebarButton
from .icon_button import IconButton


NORMAL_BG = (0.20, 0.20, 0.20, 1)   # gris sombre par défaut
HOVER_BG  = (0.30, 0.50, 0.80, 1)   # bleu/gris au survol


class InlineMenu(BoxLayout):
    """
    Menu inline intégré DANS la ligne (HoverRow), sous le header.
    Ajoute un vrai effet hover en écoutant Window.mouse_pos.
    """
    def __init__(self, on_action, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.spacing = dp(4)
        self.padding = (dp(6), dp(4), dp(6), dp(4))

        # Hauteur = 2 actions (32dp) + spacing + padding vertical
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
                background_normal="",        # désactive l'image par défaut
                background_color=NORMAL_BG,  # couleur initiale
            )
            # Texte bien aligné/ellipsé si besoin
            btn.bind(size=lambda w, *_: setattr(w, "text_size", (w.width - dp(10), None)))
            # Action au clic
            btn.bind(on_release=lambda w, a=action: on_action(a))

            self.add_widget(btn)
            self._buttons.append(btn)

        # Hover global (passif) : on écoute la souris et on colorise les boutons
        Window.bind(mouse_pos=self._on_mouse_pos)
        # Prime le survol après insertion dans l'UI
        Clock.schedule_once(lambda *_: self._on_mouse_pos(Window, Window.mouse_pos), 0)

    def _on_mouse_pos(self, _window, pos):
        # Met à jour la couleur de fond en fonction du survol réel
        any_inside = False
        for b in self._buttons:
            # Convertit les coords fenêtre -> coords locales du bouton
            lx, ly = b.to_widget(*pos)
            inside = b.collide_point(lx, ly)
            any_inside = any_inside or inside
            b.background_color = HOVER_BG if inside else NORMAL_BG
        return any_inside

    def on_parent(self, *args):
        # Nettoyage du bind quand le menu est retiré (évite fuites)
        if self.parent is None:
            try:
                Window.unbind(mouse_pos=self._on_mouse_pos)
            except Exception:
                pass


class HoverRow(BoxLayout):
    """
    Ligne de conversation avec menu inline.
    Structure:
      HoverRow (vertical, height dynamique)
        ├─ header (horizontal, height=32) : [ HoverSidebarButton | IconButton (modifier) ]
        └─ menu_container (vertical, height=0 fermé / height>0 ouvert)

    - L’icône apparaît au survol du header.
    - Clic sur l’icône → ouvre/ferme le menu inline sous la ligne.
    - Les callbacks `rename_callback` et `delete_callback` sont injectés par SidebarConversations.
    """
    def __init__(self, filename: str, btn: HoverSidebarButton, icon_source: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, None)

        self.filename = filename
        self.btn = btn

        # Callbacks assignés par SidebarConversations
        self.rename_callback = None
        self.delete_callback = None

        # --- HEADER ---
        self.header = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=32,
            spacing=6
        )

        self.icon = IconButton(
            source=icon_source,
            size_hint=(None, 1),
            width=20,
            opacity=0  # visible au hover
        )
        self.icon.bind(on_release=self._toggle_menu)

        self.header.add_widget(self.btn)
        self.header.add_widget(self.icon)

        # --- MENU CONTAINER (repliable) ---
        self.menu_container = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=0,
            opacity=0
        )
        self.menu_widget: InlineMenu | None = None

        # --- Assemblage ---
        self.add_widget(self.header)
        self.add_widget(self.menu_container)

        # Hauteur initiale = header
        self.height = self.header.height

        # Hover sur le header uniquement (évite clignotement pendant scroll)
        Window.bind(mouse_pos=self._on_mouse_pos_header)
        Clock.schedule_once(self._prime_hover, 0)

    # ----- Ouverture / Fermeture du menu inline -----
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

        # Déploie le conteneur
        self.menu_container.height = self.menu_widget.height
        self.menu_container.opacity = 1

        # Ajuste la hauteur totale de la ligne
        self.height = self.header.height + self.menu_container.height

    def _close_menu(self):
        if not self.menu_widget:
            return
        # Libère correctement le menu (il débind lui-même Window.mouse_pos dans on_parent)
        self.menu_container.clear_widgets()
        self.menu_container.height = 0
        self.menu_container.opacity = 0
        self.menu_widget = None
        # Retour à la hauteur du header seul
        self.height = self.header.height

    # ----- Actions du menu -----
    def _on_menu_action(self, action: str):
        if action == "Renommer" and self.rename_callback:
            self.rename_callback(self.filename)
        elif action == "Supprimer" and self.delete_callback:
            self.delete_callback(self.filename)
        self._close_menu()

    # ----- Hover header (affichage de l’icône modifier) -----
    def _prime_hover(self, *_):
        self._on_mouse_pos_header(Window, Window.mouse_pos)

    def _on_mouse_pos_header(self, _window, pos):
        # Effet hover uniquement sur le header
        lx, ly = self.header.to_widget(*pos)
        inside = self.header.collide_point(lx, ly)
        self.icon.opacity = 1 if inside else 0

    def on_parent(self, *args):
        if self.parent is None:
            try:
                Window.unbind(mouse_pos=self._on_mouse_pos_header)
            except Exception:
                pass
