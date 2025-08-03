import os
import sys

# Supprimer tous les logs Kivy dans la console et dans un fichier
os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"

# Rediriger les print() vers un fichier log
sys.stdout = open("debug.log", "w", encoding="utf-8")

from kivy.config import Config
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_LEFT, WINDOW_TOP

# Définir la taille et la position de la fenêtre
Config.set('graphics', 'width', str(WINDOW_WIDTH))
Config.set('graphics', 'height', str(WINDOW_HEIGHT))
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', str(WINDOW_LEFT))
Config.set('graphics', 'top', str(WINDOW_TOP))

from kivy.app import App
from interface import ChatInterface

class OllamaKivyApp(App):
    def build(self):
        return ChatInterface()

if __name__ == '__main__':
    print("Lancement de l'application", flush=True)
    OllamaKivyApp().run()
