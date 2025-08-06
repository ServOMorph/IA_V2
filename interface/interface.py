from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock

from config import (
    BACKGROUND_COLOR, TEXTINPUT_BACKGROUND_COLOR, TEXT_COLOR, HINT_TEXT_COLOR,
    BUTTON_SEND_COLOR, FONT_SIZE, BORDER_RADIUS, SCROLLVIEW_SIZE_HINT_Y,
    INPUT_SIZE_HINT_Y, BUTTONS_SIZE_HINT_Y, DEV_MODE, DEV_SHORTCUTS
)

from .widgets import HoverButton, ImageHoverButton, Bubble
from .events import EventManager

Window.clearcolor = BACKGROUND_COLOR

from ollama_api import query_ollama_stream
from historique import enregistrer_echange

class ChatInterface(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        background = Image(
            source="Assets/Logo_SerenIATech.png",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(background)

        main_layout = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=0, spacing=0)

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

        self.send_container = BoxLayout(orientation='horizontal', spacing=5, size_hint=(None, None), size=(60, 40))

        self.send_button = ImageHoverButton(
            source="Assets/Ico_Envoyer.png",
            size_hint=(None, None),
            size=(40, 40)
        )
        self.send_button.bind(on_press=self.send_message)
        self.send_container.add_widget(self.send_button)

        input_layout.add_widget(self.input)
        input_layout.add_widget(self.send_container)

        self.thinking_label = Label(
            text='',
            size_hint_y=None,
            height=20,
            font_size=14,
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            valign='middle'
        )
        self.thinking_label.bind(size=self.thinking_label.setter('text_size'))

        quit_layout = BoxLayout(size_hint_y=BUTTONS_SIZE_HINT_Y, padding=10)

        if DEV_MODE:
            shortcut_text = "   |   ".join(
                f"{key.upper()} : {label}" for key, (label, _) in DEV_SHORTCUTS.items()
            )
            shortcut_label = Label(
                text=shortcut_text,
                font_size=14,
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

        main_layout.add_widget(self.scroll)
        main_layout.add_widget(self.thinking_label)
        main_layout.add_widget(input_layout)
        main_layout.add_widget(quit_layout)

        self.add_widget(main_layout)

        self.fleche_bas = ImageHoverButton(
            source="Assets/fleche_bas.png",
            size_hint=(None, None),
            size=(30, 30),
            pos_hint={"right": 0.975, "y": 0.21},
            opacity=0
        )
        self.fleche_bas.bind(on_press=self.scroll_to_bottom)
        self.add_widget(self.fleche_bas)

        self.chat_layout.bind(height=self.mettre_a_jour_fleche)

        self.last_prompt = ""
        self.event_manager = EventManager(self)
        self.stop_stream = False
        self.stop_button = None

        if DEV_MODE:
            Window.bind(on_key_down=self.handle_dev_shortcuts)

    def handle_dev_shortcuts(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            self.quit_app(None)
            return True

        for shortcut_key, (label, message) in DEV_SHORTCUTS.items():
            if f"f{key - 281}" == shortcut_key.lower():
                self.input.text = message
                Clock.schedule_once(lambda dt: self.lancer_generation(message))
                return True
        return False

    def show_stop_button(self):
        if self.stop_button is not None:
            return

        self.stop_button = ImageHoverButton(
            source="Assets/stop.png",
            size_hint=(None, None),
            size=(30, 30),
            pos_hint={"right": 0.915, "y": 0.21}
        )
        self.stop_button.bind(on_press=self.stop_action)
        self.add_widget(self.stop_button)

    def hide_stop_button(self):
        if self.stop_button and self.stop_button in self.children:
            self.remove_widget(self.stop_button)
        self.stop_button = None

    def mettre_a_jour_fleche(self, *args):
        def verifier_scroll(dt):
            if self.chat_layout.height > self.scroll.height:
                self.fleche_bas.opacity = 1
            else:
                self.fleche_bas.opacity = 0
        Clock.schedule_once(verifier_scroll, 0.05)

    def scroll_to_bottom(self, instance):
        Clock.schedule_once(lambda dt: self.scroll.scroll_to(self.chat_layout))

    def send_message(self, instance):
        user_input = self.input.text.strip()
        if user_input:
            self.input.text = ""
            Clock.schedule_once(lambda dt: self.lancer_generation(user_input))

    def lancer_generation(self, prompt):
        self.display_message(prompt, is_user=True)
        self.last_prompt = prompt
        self.thinking_label.text = "Je réfléchis..."
        self.send_button.disabled = True
        self.send_button.source = "Assets/Ico_Envoyer_Verouiller.png"
        self.confirmer_envoi()
        self.stop_stream = False
        Clock.schedule_once(lambda dt: self.show_stop_button())

        import threading
        threading.Thread(target=self.start_streaming_response, args=(prompt,), daemon=True).start()

    def confirmer_envoi(self):
        coche = Image(source="Assets/coche.png", size_hint=(None, None), size=(20, 20))
        self.send_container.add_widget(coche)
        Clock.schedule_once(lambda dt: self.send_container.remove_widget(coche), 1.5)

    def copier_texte(self, texte, container):
        Clipboard.copy(texte)
        coche = Image(source="Assets/coche.png", size_hint=(None, None), size=(20, 20))
        container.add_widget(coche)
        Clock.schedule_once(lambda dt: container.remove_widget(coche), 1.5)

    def display_message(self, text, is_user):
        bubble = Bubble(text=text, is_user=is_user)
        message_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        message_layout.bind(minimum_height=message_layout.setter('height'))
        message_layout.padding = (10, 0, 10, 0)

        bubble_container = BoxLayout(size_hint_y=None, spacing=5)
        bubble_container.bind(minimum_height=bubble_container.setter('height'))

        if is_user:
            bubble_container.add_widget(bubble)
            bubble_container.add_widget(Widget())
        else:
            logo = Image(source="Assets/Logo_IA.png", size_hint=(None, None), size=(40, 40), allow_stretch=True)
            icon_container = BoxLayout(orientation='horizontal', spacing=5, size_hint=(None, None), size=(60, 25))
            self.copy_button = ImageHoverButton(
                source="Assets/Ico_Copiercoller.png",
                size_hint=(None, None),
                size=(25, 25)
            )
            self.copy_button.bind(on_press=lambda instance: self.copier_texte(bubble.text, icon_container))
            icon_container.add_widget(self.copy_button)

            message_row = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=5)
            message_row.bind(minimum_height=message_row.setter('height'))
            message_row.add_widget(logo)
            message_row.add_widget(bubble)
            message_row.add_widget(icon_container)
            bubble_container.add_widget(message_row)

        message_layout.add_widget(bubble_container)
        self.chat_layout.add_widget(message_layout)
        Clock.schedule_once(lambda dt: self.scroll.scroll_to(message_layout))
        self.mettre_a_jour_fleche()
        return bubble

    def start_streaming_response(self, prompt):
        self.partial_response = ""

        def on_token(token):
            if self.stop_stream:
                return
            self.partial_response += token
            Clock.schedule_once(lambda dt: self.update_bubble_text(self.partial_response))

        Clock.schedule_once(lambda dt: self.prepare_stream_bubble())
        query_ollama_stream(prompt, on_token)
        enregistrer_echange(prompt, self.partial_response)
        Clock.schedule_once(lambda dt: self.on_stream_end())

    def prepare_stream_bubble(self):
        self.current_bubble = self.display_message("", is_user=False)

    def update_bubble_text(self, text):
        if hasattr(self, "current_bubble"):
            self.current_bubble.text = text

    def on_stream_end(self):
        self.thinking_label.text = ""
        self.send_button.disabled = False
        self.send_button.source = "Assets/Ico_Envoyer.png"
        self.hide_stop_button()

    def stop_action(self, instance):
        self.stop_stream = True
        self.on_stream_end()

    def quit_app(self, instance):
        from kivy.app import App
        App.get_running_app().stop()
