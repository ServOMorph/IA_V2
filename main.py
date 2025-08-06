import os
import sys

os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"

sys.stdout = open("debug.log", "w", encoding="utf-8")

from kivy.config import Config
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_LEFT, WINDOW_TOP

Config.set('graphics', 'width', str(WINDOW_WIDTH))
Config.set('graphics', 'height', str(WINDOW_HEIGHT))
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', str(WINDOW_LEFT))
Config.set('graphics', 'top', str(WINDOW_TOP))

from kivy.app import App
from interface.interface import ChatInterface

class OllamaKivyApp(App):
    def build(self):
        return ChatInterface()

if __name__ == '__main__':
    print("Lancement de l'application", flush=True)
    OllamaKivyApp().run()
