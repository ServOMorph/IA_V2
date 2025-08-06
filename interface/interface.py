from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard

from config import (
    BACKGROUND_COLOR, TEXTINPUT_BACKGROUND_COLOR, TEXT_COLOR, HINT_TEXT_COLOR,
    BUTTON_SEND_COLOR, FONT_SIZE, BORDER_RADIUS, SCROLLVIEW_SIZE_HINT_Y,
    INPUT_SIZE_HINT_Y, BUTTONS_SIZE_HINT_Y, DEV_MODE, DEV_SHORTCUTS
)

from .widgets import HoverButton, ImageHoverButton, Bubble
from .events import EventManager

Window.clearcolor = BACKGROUND_COLOR

class ChatInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

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

        label = CoreLabel(text="Quitter", font_size=FONT_SIZE)
        label.refresh()
        text_width = label.texture.size[0]

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
        self.event_manager = EventManager(self)

        if DEV_MODE:
            Window.bind(on_key_down=self.event_manager.handle_dev_shortcuts)

    def send_message(self, instance):
        user_input = self.input.text.strip()
        if user_input:
            self.display_message(user_input, is_user=True)
            self.input.text = ""
            self.last_prompt = user_input
            import threading
            threading.Thread(target=self.event_manager.query_and_display, args=(user_input,), daemon=True).start()

    def copier_texte(self, texte):
        Clipboard.copy(texte)

    def display_message(self, text, is_user):
        bubble = Bubble(text=text, is_user=is_user)

        message_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        message_layout.bind(minimum_height=message_layout.setter('height'))
        message_layout.padding = (10, 0, 10, 0)

        bubble_container = BoxLayout(size_hint_y=None)
        bubble_container.bind(minimum_height=bubble_container.setter('height'))

        if is_user:
            bubble_container.add_widget(bubble)
            bubble_container.add_widget(Widget())
        else:
            bubble_container.add_widget(Widget())
            bubble_container.add_widget(bubble)

            icon_button = ImageHoverButton(
                source="Assets/Ico_Copiercoller.png",
                size_hint=(None, None),
                size=(25, 25),
                pos_hint={'right': 1}
            )
            icon_button.bind(on_press=lambda instance: self.copier_texte(text))

            relative_container = RelativeLayout(size_hint_y=None, height=20)
            relative_container.add_widget(icon_button)
            icon_button.y = -5

            message_layout.add_widget(relative_container)

        message_layout.add_widget(bubble_container)
        self.chat_layout.add_widget(message_layout)

        from historique import enregistrer_echange
        if not is_user:
            enregistrer_echange(self.last_prompt, text)

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.scroll.scroll_to(message_layout))

    def quit_app(self, instance):
        from kivy.app import App
        App.get_running_app().stop()
