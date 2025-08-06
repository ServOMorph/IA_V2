from kivy.clock import Clock
from kivy.uix.image import Image
from interface.custom_widgets import ImageHoverButton
from ollama_api import query_ollama_stream
from historique import enregistrer_echange
import threading

# ✅ Ajout pour sauvegarde des conversations
from conversations.conversation_manager import append_message

class ChatStreamMixin:
    def lancer_generation(self, prompt):
        try:
            self.display_message(prompt, is_user=True)
            self.last_prompt = prompt
            self.thinking_label.text = "Je réfléchis..."
            self.send_button.disabled = True
            self.send_button.source = "Assets/Ico_Envoyer_Verouiller.png"
            self.confirmer_envoi()
            self.stop_stream = False
            Clock.schedule_once(lambda dt: self.show_stop_button())

            threading.Thread(
                target=self.start_streaming_response, 
                args=(prompt,), 
                daemon=True
            ).start()
        except Exception as e:
            print(f"[ERREUR lancer_generation] {e}", flush=True)

    def start_streaming_response(self, prompt):
        self.partial_response = ""

        def on_token(token):
            if self.stop_stream:
                return
            self.partial_response += token
            Clock.schedule_once(lambda dt: self.update_bubble_text(self.partial_response))

        Clock.schedule_once(lambda dt: self.prepare_stream_bubble())
        query_ollama_stream(prompt, on_token)

        # ✅ À la fin du stream, on sauvegarde dans historique global (facultatif)
        enregistrer_echange(prompt, self.partial_response)

        # ✅ Et on enregistre dans le fichier de conversation actif (si actif)
        if self.conversation_filepath:
            append_message(self.conversation_filepath, "assistant", self.partial_response)

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
