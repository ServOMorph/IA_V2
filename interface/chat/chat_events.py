from kivy.core.window import Window
from kivy.clock import Clock
from kivy.app import App

from config import DEV_MODE, DEV_SHORTCUTS


class ChatEventsMixin:
    def setup_event_bindings(self):
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

    def quit_app(self, instance):
        App.get_running_app().stop()

    def stop_action(self, instance):
        self.stop_stream = True
        self.on_stream_end()
