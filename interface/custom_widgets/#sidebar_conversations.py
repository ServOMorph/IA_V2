from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior

from config import FONT_SIZE
from conversations.conversation_manager import list_conversations, read_conversation
from .hover_sidebar_button import HoverSidebarButton

from .sidebar import IconButton
from .sidebar.conversation_row import HoverRow







class SidebarConversations(BoxLayout):
    def __init__(self, on_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (0.25, 1)
        self.padding = 8
        self.spacing = 6
        self.on_select_callback = on_select_callback

        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # fond sombre (modifiable)
            self.bg_rect = RoundedRectangle(radius=[0], pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        title = Label(
            text="[b]Conversations[/b]",
            markup=True,
            font_size=14,
            size_hint=(1, None),
            height=30,
            halign="left",
            valign="middle"
        )
        title.bind(size=title.setter("text_size"))
        self.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        layout = GridLayout(cols=1, spacing=4, size_hint_y=None, padding=(0, 5))
        layout.bind(minimum_height=layout.setter('height'))

        for filename in list_conversations():
            label = self.extract_preview(filename)
            label = f"{label} …"  # on garde l’ellipse demandée

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
            # IMPORTANT : capturer filename via défaut d’argument
            btn.bind(on_press=lambda instance, name=filename: self.select_conversation(name))

            # Ligne avec icône + menu déroulant
            row = HoverRow(
                filename=filename,
                btn=btn,
                icon_source="Assets/ico_modifier.png",
                size_hint=(1, None),
                height=32
            )

            layout.add_widget(row)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def extract_preview(self, filename):
        try:
            contenu = read_conversation(f"conversations/{filename}")
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

    def select_conversation(self, filename):
        if self.on_select_callback:
            self.on_select_callback(filename)
