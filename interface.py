from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from kivy.clock import Clock
import threading
from ollama_api import query_ollama
from historique import enregistrer_echange

class ChatInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatInterface, self).__init__(orientation='vertical', **kwargs)

        self.output = TextInput(size_hint_y=0.8, readonly=True)
        self.input = TextInput(hint_text='Votre message...', size_hint_y=0.1, multiline=True)
        button_layout = BoxLayout(size_hint_y=0.1)

        send_button = Button(text="Envoyer")
        send_button.bind(on_press=self.send_message)

        quit_button = Button(text="Quitter")
        quit_button.bind(on_press=self.quit_app)

        button_layout.add_widget(send_button)
        button_layout.add_widget(quit_button)

        self.add_widget(self.output)
        self.add_widget(self.input)
        self.add_widget(button_layout)

        self.last_prompt = ""  # Initialisation pour éviter les erreurs

    def send_message(self, instance):
        user_input = self.input.text.strip()
        if user_input:
            print(f"[Utilisateur] {user_input}")
            self.output.text += f"> {user_input}\n"
            self.input.text = ""
            self.last_prompt = user_input
            threading.Thread(target=self._query_and_display, args=(user_input,), daemon=True).start()

    def _query_and_display(self, prompt):
        try:
            reply = query_ollama(prompt)
            Clock.schedule_once(lambda dt: self.append_response(reply))
        except Exception as e:
            print(f"[Erreur Thread] {e}")

    def append_response(self, reply):
        self.output.text += f"{reply}\n\n"
        enregistrer_echange(self.last_prompt, reply)

    def quit_app(self, instance):
        App.get_running_app().stop()
