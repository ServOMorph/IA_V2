from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.uix.image import Image


class ChatUtilsMixin:
    def mettre_a_jour_fleche(self, *args):
        def verifier_scroll(dt):
            if self.chat_layout.height > self.scroll.height:
                self.fleche_bas.opacity = 1
            else:
                self.fleche_bas.opacity = 0
        Clock.schedule_once(verifier_scroll, 0.05)

    def scroll_to_bottom(self, instance):
        Clock.schedule_once(lambda dt: self.scroll.scroll_to(self.chat_layout))

    def copier_texte(self, texte, container):
        Clipboard.copy(texte)
        coche = Image(source="Assets/coche.png", size_hint=(None, None), size=(20, 20))
        container.add_widget(coche)
        Clock.schedule_once(lambda dt: container.remove_widget(coche), 1.5)
