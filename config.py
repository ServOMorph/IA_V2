# Configuration API Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "mistral"

# Configuration fenêtre
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 1000
WINDOW_LEFT = 0
WINDOW_TOP = 30

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
BUBBLE_WIDTH_RATIO = 0.7                        # Largeur max des bulles (70% de la fenêtre)

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

# =========================
# 🎛️ Sidebar / Conversations
# (Doc §12 : centraliser les constantes modifiables)
# =========================
SIDEBAR_ROW_HEIGHT = 42           # hauteur d'une ligne (px)
SIDEBAR_ICON_SIZE = (20, 20)      # taille icône menu "..."
SIDEBAR_ICON_PADDING = (6, 6)     # padding autour de l'icône
SIDEBAR_PREVIEW_MAXLEN = 80       # longueur max du preview (avec ellipsis)

# libellés menu contextuel
MENU_ACTIONS = ("Renommer", "Supprimer")

# chemins d'icônes (ajuste selon ton arborescence)
ICON_MORE_PATH = "assets/icons/more_vert.png"
ICON_EDIT_PATH = "assets/icons/edit.png"
ICON_DELETE_PATH = "assets/icons/delete.png"
ICON_CHAT_PATH = "assets/icons/chat.png"
