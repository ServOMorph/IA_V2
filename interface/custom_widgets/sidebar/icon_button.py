from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

class IconButton(ButtonBehavior, Image):
    """
    Image cliquable (utilisée pour l’icône 'modifier').
    Séparée dans le sous-dossier 'sidebar' pour :
      - respecter la modularité (doc §4)
      - faciliter la réutilisation dans d'autres composants
      - éviter les imports circulaires
    """
    pass
