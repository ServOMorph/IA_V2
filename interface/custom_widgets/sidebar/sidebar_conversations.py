from typing import Optional, Iterable
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp

from .data_provider import ConversationsProvider, FileSystemConversationsProvider, Conversation
from .conversation_row import ConversationRow


class SidebarConversations(BoxLayout):
    """
    Assembleur : ScrollView + GridLayout de ConversationRow.
    - Ne fait AUCUNE lecture disque : tout passe par provider (Doc §4).
    - Rafraîchit la liste à la demande.
    - Propage les callbacks on_select / on_rename / on_delete.
    """

    def __init__(
        self,
        provider: Optional[ConversationsProvider] = None,
        on_select_callback=None,
        on_rename=None,
        on_delete=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.provider = provider or FileSystemConversationsProvider()
        self.on_select_callback = on_select_callback
        self.on_rename = on_rename
        self.on_delete = on_delete

        # Scroll + Grid
        self._grid = GridLayout(cols=1, size_hint_y=None, padding=(dp(4), dp(4)), spacing=dp(4))
        self._grid.bind(minimum_height=self._grid.setter("height"))

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        scroll.add_widget(self._grid)
        self.add_widget(scroll)

        self.reload()

    # ------- API publique -------
    def reload(self):
        """Reconstruit la liste depuis provider (Doc §1 : parité fonctionnelle)."""
        self._grid.clear_widgets()
        try:
            conversations: Iterable[Conversation] = self.provider.list_conversations()
            for conv in conversations:
                row = ConversationRow(
                    title=conv.title,
                    preview=conv.preview,
                    filename=conv.filename,
                    on_select=self._on_select,
                    on_rename=self._on_rename,
                    on_delete=self._on_delete,
                    size_hint_y=None,
                )
                self._grid.add_widget(row)
        except Exception as e:
            print(f"[SidebarConversations] Erreur reload: {e}")

    # ------- Callbacks internes -------
    def _on_select(self, filename: str):
        if callable(self.on_select_callback):
            self.on_select_callback(filename)

    def _on_rename(self, filename: str):
        if callable(self.on_rename):
            self.on_rename(filename)
        else:
            # Fallback provider puis reload
            try:
                new_title = self._prompt_new_title(filename)  # placeholder simple
                if new_title:
                    self.provider.rename(filename, new_title)
                    self.reload()
            except Exception as e:
                print(f"[SidebarConversations] rename error: {e}")

    def _on_delete(self, filename: str):
        if callable(self.on_delete):
            self.on_delete(filename)
        else:
            try:
                self.provider.delete(filename)
                self.reload()
            except Exception as e:
                print(f"[SidebarConversations] delete error: {e}")

    # ------- Utilitaire minimal -------
    def _prompt_new_title(self, filename: str) -> str:
        """
        Placeholder console pour rester non-intrusif :
        dans ton app, remplace par un popup Kivy et passe on_rename.
        """
        try:
            base = filename.rsplit(".", 1)[0]
            print(f"Entrer le nouveau titre pour '{base}' puis Entrée (laisser vide pour annuler) : ", end="", flush=True)
            # NOTE : dans un vrai contexte Kivy, on ne bloquerait pas le thread. Ici c’est un fallback.
            import sys
            return sys.stdin.readline().strip()
        except Exception:
            return ""
