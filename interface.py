from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
import threading
import sys

from config import (
    BACKGROUND_COLOR, TEXTINPUT_BACKGROUND_COLOR, TEXT_COLOR, HINT_TEXT_COLOR,
    BUTTON_SEND_COLOR, BUTTON_QUIT_COLOR, BUBBLE_USER_COLOR, BUBBLE_IA_COLOR,
    FONT_SIZE, BORDER_RADIUS, BUBBLE_PADDING,
    SCROLLVIEW_SIZE_HINT_Y, INPUT_SIZE_HINT_Y, BUTTONS_SIZE_HINT_Y,
    DEV_MODE, DEV_SHORTCUTS
)
from ollama_api import query_ollama
from historique import enregistrer_echange

Window.clearcolor = BACKGROUND_COLOR

def lighten_color(color, factor=0.15):
    return tuple(min(1.0, c + factor) for c in color[:3]) + (color[3],)

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

class Bubble(Label):
    def __init__(self, text, is_user, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = FONT_SIZE
        self.color = TEXT_COLOR
        self.markup = True
        self.size_hint_x = None
        self.size_hint_y = None
        self.halign = 'left'
        self.valign = 'top'
        self.padding = BUBBLE_PADDING
        self.text_size = (Window.width * 0.7, None)
        self.shorten = False
        self.is_user = is_user

        self.bind(texture_size=self.update_size)
        Clock.schedule_once(self.init_background)

    def update_size(self, instance, value):
        self.size = (value[0] + self.padding[0] * 2, value[1] + self.padding[1] * 2)

    def init_background(self, *args):
        from config import BUBBLE_USER_COLOR, BUBBLE_IA_COLOR
        color = BUBBLE_USER_COLOR if self.is_user else BUBBLE_IA_COLOR

        with self.canvas.before:
            Color(*color)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=BORDER_RADIUS)

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class ChatInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatInterface, self).__init__(orientation='vertical', **kwargs)

        self.scroll = ScrollView(size_hint=(1, SCROLLVIEW_SIZE_HINT_Y))
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=10)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll.add_widget(self.chat_layout)

        input_layout = BoxLayout(size_hint_y=INPUT_SIZE_HINT_Y, padding=10, spacing=10)

        self.input = TextInput(
            hint_text='Votre message...', multiline=True,
            background_color=TEXTINPUT_BACKGROUND_COLOR,
            foreground_color=TEXT_COLOR,
            cursor_color=TEXT_COLOR,
            hint_text_color=HINT_TEXT_COLOR,
            size_hint_x=0.85
        )

        send_button = HoverButton(text="Envoyer", size_hint_x=0.15, base_color=BUTTON_SEND_COLOR)
        send_button.bind(on_press=self.send_message)

        input_layout.add_widget(self.input)
        input_layout.add_widget(send_button)

        from kivy.core.text import Label as CoreLabel
        label = CoreLabel(text="Quitter", font_size=FONT_SIZE)
        label.refresh()
        text_width = label.texture.size[0]

        quit_layout = BoxLayout(size_hint_y=BUTTONS_SIZE_HINT_Y, padding=10)

        if DEV_MODE:
            shortcut_text = "   |   ".join(
                f"{key.upper()} : {label}" for key, (label, _) in DEV_SHORTCUTS.items()
            )
            shortcut_label = Label(
                text=shortcut_text,
                font_size=10,
                color=(0.6, 0.6, 0.6, 1),
                size_hint=(None, 1),
                halign='left',
                valign='middle'
            )
            shortcut_label.bind(texture_size=shortcut_label.setter('size'))
            quit_layout.add_widget(shortcut_label)
        else:
            quit_layout.add_widget(Widget())

        quit_button = HoverButton(
            text="Quitter",
            size_hint=(None, None),
            size=(text_width + 30, 40),
            base_color=TEXTINPUT_BACKGROUND_COLOR
        )
        quit_button.bind(on_press=self.quit_app)

        quit_layout.add_widget(Widget())
        quit_layout.add_widget(quit_button)
        quit_layout.add_widget(Widget())

        self.add_widget(self.scroll)
        self.add_widget(input_layout)
        self.add_widget(quit_layout)

        self.last_prompt = ""

        if DEV_MODE:
            Window.bind(on_key_down=self._handle_dev_shortcuts)

    def _handle_dev_shortcuts(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # ESC
            self.quit_app(None)
            return

        keymap = {
            283: "f2",
            284: "f3",
            285: "f4"
        }
        key_name = keymap.get(key)
        if key_name and key_name in DEV_SHORTCUTS:
            _, message = DEV_SHORTCUTS[key_name]
            self._send_dev_message(message)

    def _send_dev_message(self, message):
        self.display_message(message, is_user=True)
        self.last_prompt = message
        threading.Thread(target=self._query_and_display, args=(message,), daemon=True).start()

    def send_message(self, instance):
        user_input = self.input.text.strip()
        if user_input:
            self.display_message(user_input, is_user=True)
            self.input.text = ""
            self.last_prompt = user_input
            threading.Thread(target=self._query_and_display, args=(user_input,), daemon=True).start()

    def _query_and_display(self, prompt):
        try:
            reply = query_ollama(prompt)
            Clock.schedule_once(lambda dt: self.display_message(reply, is_user=False))
        except Exception as e:
            print(f"[Erreur Thread] {e}", file=sys.stderr, flush=True)

    def copier_texte(self, texte):
        Clipboard.copy(texte)

    def display_message(self, text, is_user):
        bubble = Bubble(text=text, is_user=is_user)

        message_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        message_layout.padding = (10, 0, 10, 0)

        bubble_container = BoxLayout(size_hint_y=None)
        bubble_container.bind(minimum_height=bubble_container.setter('height'))

        if is_user:
            bubble_container.add_widget(bubble)
            bubble_container.add_widget(Widget())
            message_layout.add_widget(bubble_container)
        else:
            bubble_container.add_widget(Widget())
            bubble_container.add_widget(bubble)
            message_layout.add_widget(bubble_container)

            spacer = Widget(size_hint_y=None, height=2)
            message_layout.add_widget(spacer)

            copy_button_height = 25
            copy_button = HoverButton(
                text="Copier", font_size=12, size_hint=(None, None), size=(80, copy_button_height),
                base_color=(0.4, 0.4, 0.4, 1)
            )
            copy_button.bind(on_press=lambda instance: self.copier_texte(text))

            copy_container = BoxLayout(size_hint_y=None, height=copy_button_height)
            copy_container.add_widget(Widget())
            copy_container.add_widget(copy_button)

            message_layout.add_widget(copy_container)

        message_layout.height = bubble.height + 35
        self.chat_layout.add_widget(message_layout)
        Clock.schedule_once(lambda dt: self.scroll.scroll_to(message_layout))

        if not is_user:
            enregistrer_echange(self.last_prompt, text)

    def quit_app(self, instance):
        App.get_running_app().stop()
