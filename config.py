# Configuration API Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "mistral"

# Configuration fenêtre
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
WINDOW_LEFT = 100
WINDOW_TOP = 200

# Couleurs de l'interface inspirées de Mistral AI Chat (ajustées)
BACKGROUND_COLOR = (0.09, 0.09, 0.11, 1)
TEXTINPUT_BACKGROUND_COLOR = (0.16, 0.16, 0.19, 1)
TEXT_COLOR = (0.95, 0.95, 0.95, 1)
HINT_TEXT_COLOR = (0.55, 0.55, 0.58, 1)
BUTTON_SEND_COLOR = (0.91, 0.27, 0.13, 1)
BUTTON_QUIT_COLOR = (0.4, 0.2, 0.2, 1)

# 🎨 Bulles de discussion personnalisées
BUBBLE_USER_COLOR = (0.16, 0.16, 0.19, 1)       # #292930 : utilisateur
BUBBLE_IA_COLOR = (0.12, 0.20, 0.33, 1)         # #1f3454 : IA

# Apparence
FONT_SIZE = 16
BORDER_RADIUS = [12]
BUBBLE_PADDING = (12, 8)

# Layout
SCROLLVIEW_SIZE_HINT_Y = 0.8
INPUT_SIZE_HINT_Y = 0.1
BUTTONS_SIZE_HINT_Y = 0.1

# Mode développeur
DEV_MODE = True

DEV_SHORTCUTS = {
    "f2": ("Msg court", "Quelle est la capitale de l'Espagne"),
    "f3": ("Msg moyen", "Quel est le plus grand océan du monde ?"),
    "f4": ("Msg long", "Explique-moi le fonctionnement d’un moteur à combustion interne.")
}

