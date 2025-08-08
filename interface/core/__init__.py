# interface/core/__init__.py
"""
Sous-package 'core' : point d'accès logique pour la logique non-visuelle (events, utils).
Cette version utilise des imports de transition pour ne rien casser.
"""

# Réexport explicite depuis les modules de transition
from .events import *  # noqa: F401,F403
from .utils import *   # noqa: F401,F403
