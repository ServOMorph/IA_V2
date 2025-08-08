from kivy.clock import Clock
from kivy.uix.image import Image
from ..custom_widgets import ImageHoverButton
from ollama_api import query_ollama_stream
from historique import enregistrer_echange
import threading
import os

from conversations.conversation_manager import append_message, read_conversation

# Charger le message système depuis le fichier partagé avec le mode console
PROMPT_FILE = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "Test_IA", "Console_Interactif", "system_prompt.txt"
)
PROMPT_FILE = os.path.abspath(PROMPT_FILE)

if not os.path.exists(PROMPT_FILE):
    raise FileNotFoundError(f"[ERREUR] Fichier system_prompt.txt introuvable : {PROMPT_FILE}")

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    SYSTEM_MESSAGE = f.read().strip()

class ChatStreamMixin:
    def lancer_generation(self, prompt):
        try:
            self.display_message(prompt, is_user=True)
            self.last_prompt = prompt
            self.thinking_label.text = "Je réfléchis..."

            # ✅ Masquer le bouton Envoyer
            self.send_container.opacity = 0
            self.send_button.disabled = True

            # ✅ Réinitialiser le contenu attendu
            self.response_complete = None

            self.stop_stream = False
            Clock.schedule_once(lambda dt: self.show_stop_button())

            threading.Thread(
                target=self.start_streaming_response,
                args=(prompt,),
                daemon=True
            ).start()
        except Exception as e:
            print(f"[ERREUR lancer_generation] {e}", flush=True)

    def _build_message_history(self, new_user_message):
        """
        Construit la liste 'messages' pour Ollama :
        - message system en premier
        - tout l'historique existant (user/assistant)
        - nouveau message utilisateur
        """
        messages = [{"role": "system", "content": SYSTEM_MESSAGE}]

        if self.conversation_filepath and os.path.exists(self.conversation_filepath):
            contenu = read_conversation(self.conversation_filepath)
            lignes = contenu.strip().split("\n")
            for ligne in lignes:
                if ligne.startswith("[") and "]" in ligne:
                    try:
                        _, reste = ligne.split("]", 1)
                        role, message = reste.strip().split(":", 1)
                        role = role.strip().lower()
                        message = message.strip()
                        if role in ("user", "assistant"):
                            messages.append({"role": role, "content": message})
                    except ValueError:
                        continue

        # Ajouter le nouveau message utilisateur
        messages.append({"role": "user", "content": new_user_message})

        return messages

    def start_streaming_response(self, prompt):
        self.partial_response = ""

        # Construire l'historique complet
        messages = self._build_message_history(prompt)

        def on_token(token):
            if self.stop_stream:
                return
            self.partial_response += token
            Clock.schedule_once(lambda dt: self.update_bubble_text(self.partial_response))

        Clock.schedule_once(lambda dt: self.prepare_stream_bubble())
        query_ollama_stream(messages, on_token)

        enregistrer_echange(prompt, self.partial_response)

        if self.conversation_filepath:
            append_message(self.conversation_filepath, "assistant", self.partial_response)

        Clock.schedule_once(lambda dt: self.on_stream_end_final())

    def prepare_stream_bubble(self):
        self.current_bubble = self.display_message("", is_user=False)

    def update_bubble_text(self, text):
        if hasattr(self, "current_bubble"):
            self.current_bubble.text = text

    def on_stream_end_final(self):
        self.response_complete = self.partial_response
        self.on_stream_end()

        # ✅ Réaffichage contrôlé après un léger délai
        Clock.schedule_once(lambda dt: self.reafficher_bouton_envoyer(), 0.2)

    def reafficher_bouton_envoyer(self):
        self.send_container.opacity = 1
        self.send_button.disabled = False
        self.hide_stop_button()

    def on_stream_end(self):
        self.thinking_label.text = ""
        # ✅ Réactivation différée dans reafficher_bouton_envoyer()

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
