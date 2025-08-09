from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock
import os

from config import FONT_SIZE, ICON_PLUS_PATH, SIDEBAR_ICON_SIZE
from conversations.conversation_manager import (
    list_conversations,
    read_conversation,
    rename_conversation_file,
    delete_conversation_file,
    create_new_conversation   # ✅ ajout pour créer une nouvelle conversation
)
from ..hover_sidebar_button import HoverSidebarButton
from ..image_hover_button import ImageHoverButton
from .conversation_row import HoverRow


class SidebarConversations(BoxLayout):
    """Conteneur principal de la barre latérale des conversations (sélection exclusive)."""
    def __init__(self, on_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (0.25, 1)
        self.padding = 8
        self.spacing = 6
        self.on_select_callback = on_select_callback

        # Suivi des lignes pour gérer la sélection exclusive
        self._rows_by_filename: dict[str, HoverRow] = {}
        self._current_selected: HoverRow | None = None

        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = RoundedRectangle(radius=[0], pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)
        self.build_list()

    def build_list(self):
        """Reconstruit la liste des conversations."""
        self.clear_widgets()
        self._rows_by_filename.clear()
        self._current_selected = None  # la sélection sera réappliquée si besoin

        # ---------- En-tête avec titre + icône plus ----------
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=36, spacing=8, padding=(0, 0))
        title = Label(
            text="[b]Conversations[/b]",
            markup=True,
            font_size=14,
            size_hint=(1, 1),
            halign="left",
            valign="middle"
        )
        title.bind(size=title.setter("text_size"))

        plus_btn = ImageHoverButton(
            source=ICON_PLUS_PATH,
            size_hint=(None, None),
            size=(dp(SIDEBAR_ICON_SIZE[0]), dp(SIDEBAR_ICON_SIZE[1])),
            allow_stretch=True,
            keep_ratio=True
        )
        plus_btn.bind(on_press=self.on_plus_click)

        header.add_widget(title)
        header.add_widget(plus_btn)
        self.add_widget(header)

        # ---------- Liste défilante des conversations ----------
        scroll = ScrollView(size_hint=(1, 1))
        layout = GridLayout(cols=1, spacing=4, size_hint_y=None, padding=(0, 5))
        layout.bind(minimum_height=layout.setter('height'))

        for filename in list_conversations():
            label = self.extract_preview(filename)
            btn = HoverSidebarButton(
                text=label,
                size_hint=(1, 1),
                font_size=12,
                halign="left",
                valign="middle",
                text_size=(dp(160), None),
                shorten=True,
                max_lines=1,
                color=(1, 1, 1, 1),
            )
            btn.bind(on_press=lambda instance, name=filename: self.select_conversation(name))

            row = HoverRow(
                filename=filename,
                btn=btn,
                icon_source="Assets/ico_modifier.png",
                size_hint=(1, None),
                height=32
            )
            row.rename_callback = self.rename_conversation
            row.delete_callback = self.delete_conversation

            self._rows_by_filename[filename] = row
            layout.add_widget(row)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def extract_preview(self, filename):
        try:
            contenu = read_conversation(f"{filename}")
            lignes = contenu.strip().split("\n")
            for ligne in lignes:
                if "]" in ligne and "USER:" in ligne.upper():
                    try:
                        _, reste = ligne.split("]", 1)
                        role, message = reste.strip().split(":", 1)
                        if role.strip().upper() == "USER":
                            return message.strip().capitalize()
                    except:
                        continue
        except Exception:
            pass
        return filename

    # ---------- Sélection exclusive ----------
    def _apply_selection(self, filename: str):
        if self._current_selected and (self._current_selected.filename != filename):
            self._current_selected.set_selected(False)
            self._current_selected = None

        new_row = self._rows_by_filename.get(filename)
        if new_row:
            new_row.set_selected(True)
            self._current_selected = new_row

    def select_conversation(self, filename):
        self._apply_selection(filename)
        if self.on_select_callback:
            self.on_select_callback(filename)

    # ---------- Bouton PLUS ----------
    def on_plus_click(self, *_):
        """Crée une nouvelle conversation et la sélectionne."""
        new_filepath = create_new_conversation()
        if new_filepath and os.path.exists(new_filepath):
            filename = os.path.basename(new_filepath)
            self.build_list()
            self._apply_selection(filename)
            if self.on_select_callback:
                self.on_select_callback(filename)
        else:
            popup = Popup(
                title="Erreur",
                content=Label(text="Impossible de créer une nouvelle conversation."),
                size_hint=(0.5, 0.3)
            )
            popup.open()
    # ---------- Renommer / Supprimer ----------
    def rename_conversation(self, filename):
        base_name = filename[:-4] if filename.lower().endswith(".txt") else filename
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        input_name = TextInput(text=base_name, multiline=False)
        content.add_widget(input_name)

        def focus_and_select(_popup):
            input_name.focus = True
            input_name.select_all()
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
        btn_ok = Button(text="Valider")
        btn_cancel = Button(text="Annuler")
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)

        popup = Popup(title="Renommer la conversation", content=content, size_hint=(0.5, 0.3))
        popup.bind(on_open=focus_and_select)

        def valider(_):
            new_name = input_name.text.strip() + ".txt"
            success, msg = rename_conversation_file(filename, new_name)
            if success:
                popup.dismiss()
                self.build_list()
                self._apply_selection(new_name)
            else:
                popup.title = f"Erreur : {msg}"

        btn_ok.bind(on_release=valider)
        btn_cancel.bind(on_release=lambda _: popup.dismiss())
        popup.open()

    def delete_conversation(self, filename):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=f"Supprimer la conversation '{filename}' ?", halign="center"))

        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
        btn_yes = Button(text="Oui")
        btn_no = Button(text="Non")
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
        content.add_widget(btn_layout)

        popup = Popup(title="Confirmation", content=content, size_hint=(0.5, 0.3))

        def confirmer(_):
            success, msg = delete_conversation_file(filename)
            if success:
                popup.dismiss()
                if self._current_selected and self._current_selected.filename == filename:
                    self._current_selected = None
                self.build_list()
            else:
                popup.title = f"Erreur : {msg}"

        btn_yes.bind(on_release=confirmer)
        btn_no.bind(on_release=lambda _: popup.dismiss())
        popup.open()
