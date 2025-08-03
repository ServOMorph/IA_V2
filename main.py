import os
from kivy.config import Config
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_LEFT, WINDOW_TOP

# Supprimer les logs de Kivy dans la console
os.environ["KIVY_NO_CONSOLELOG"] = "1"
Config.set('kivy', 'log_level', 'warning')

# Définir la taille et la position de la fenêtre à partir de config.py
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
    OllamaKivyApp().run()
