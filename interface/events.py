import threading
import sys
from kivy.clock import Clock
from config import DEV_SHORTCUTS
from ollama_api import query_ollama
from historique import enregistrer_echange

class EventManager:
    def __init__(self, chat_interface):
        self.chat_interface = chat_interface

    def handle_dev_shortcuts(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # ESC
            self.chat_interface.quit_app(None)
            return

        keymap = {
            283: "f2",
            284: "f3",
            285: "f4"
        }
        key_name = keymap.get(key)
        if key_name and key_name in DEV_SHORTCUTS:
            _, message = DEV_SHORTCUTS[key_name]
            self.send_dev_message(message)

    def send_dev_message(self, message):
        self.chat_interface.display_message(message, is_user=True)
        self.chat_interface.last_prompt = message
        threading.Thread(target=self.query_and_display, args=(message,), daemon=True).start()

    def query_and_display(self, prompt):
        try:
            reply = query_ollama(prompt)
            Clock.schedule_once(lambda dt: self.chat_interface.display_message(reply, is_user=False))
        except Exception as e:
            print(f"[Erreur Thread] {e}", file=sys.stderr, flush=True)
