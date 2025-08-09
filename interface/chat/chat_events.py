from kivy.core.window import Window
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from config import DEV_MODE, DEV_SHORTCUTS
from conversations import conversation_manager as conv_mgr


class ChatEventsMixin:
    def setup_event_bindings(self):
        if DEV_MODE:
            Window.bind(on_key_down=self.handle_dev_shortcuts)

    def handle_dev_shortcuts(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            self.quit_app(None)
            return True

        for shortcut_key, (label, message) in DEV_SHORTCUTS.items():
            # Match des touches F2..F12
            if f"f{key - 281}" == shortcut_key.lower():
                # Cas particulier F5 : suppression globale
                if shortcut_key.lower() == "f5":
                    self._confirm_delete_all_conversations()
                    return True
                # Cas normal : injection d'un message prédéfini
                if message:
                    self.input.text = message
                    Clock.schedule_once(lambda dt: self.lancer_generation(message))
                return True
        return False

    def quit_app(self, instance):
        App.get_running_app().stop()

    def stop_action(self, instance):
        self.stop_stream = True
        self.on_stream_end()

    # ===============================
    # 🆕 Suppression globale (F5)
    # ===============================
    def _confirm_delete_all_conversations(self):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(
            text="Voulez-vous vraiment supprimer TOUTES les conversations ?",
            halign="center"
        ))

        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_yes = Button(text="Oui", background_color=(0.8, 0.2, 0.2, 1))
        btn_no = Button(text="Non")
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
        content.add_widget(btn_layout)

        popup = Popup(title="Confirmation", content=content, size_hint=(0.5, 0.3))

        def confirmer(_):
            popup.dismiss()
            conv_mgr.delete_all_conversations()
            # Si la sidebar est présente, on la rafraîchit
            if hasattr(self, "sidebar") and self.sidebar:
                self.sidebar.build_list()

        btn_yes.bind(on_release=confirmer)
        btn_no.bind(on_release=lambda _: popup.dismiss())
        popup.open()
