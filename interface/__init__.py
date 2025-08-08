# interface/__init__.py
# Point d'entrée unique pour l'interface : réexporte les classes utiles.

# Chat (classe principale + mixins)
from .chat import (
    ChatInterface,
    ChatEventsMixin,
    ChatStreamMixin,
    ChatUtilsMixin,
)

# Widgets réutilisables
from .custom_widgets import (
    Bubble,
    HoverButton,
    ImageHoverButton,
    HoverSidebarButton,
    SidebarConversations,
)

__all__ = [
    # Chat
    "ChatInterface",
    "ChatEventsMixin",
    "ChatStreamMixin",
    "ChatUtilsMixin",
    # Widgets
    "Bubble",
    "HoverButton",
    "ImageHoverButton",
    "HoverSidebarButton",
    "SidebarConversations",
]
