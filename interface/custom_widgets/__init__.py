# interface/custom_widgets/__init__.py
"""
Exports publics des widgets réutilisables de l'interface.
Permet:
    from interface.custom_widgets import Bubble, HoverButton, ImageHoverButton, HoverSidebarButton, SidebarConversations
et, grâce au réexport dans interface/__init__.py:
    from interface import Bubble, HoverButton, ...
"""

from .bubble import Bubble
from .hover_button import HoverButton
from .image_hover_button import ImageHoverButton
from .hover_sidebar_button import HoverSidebarButton
from .sidebar_conversations import SidebarConversations

__all__ = [
    "Bubble",
    "HoverButton",
    "ImageHoverButton",
    "HoverSidebarButton",
    "SidebarConversations",
]
