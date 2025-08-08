from __future__ import annotations
from typing import Protocol, Iterable, NamedTuple, List, Optional
from dataclasses import dataclass
from pathlib import Path

from config import SIDEBAR_PREVIEW_MAXLEN

# Facultatif : si le projet expose déjà un manager, on le réutilise (parité fonctionnelle, Doc §1)
try:
    from conversations.conversation_manager import list_conversations as cm_list
    from conversations.conversation_manager import read_conversation as cm_read
except Exception:
    cm_list = None
    cm_read = None


class Conversation(NamedTuple):
    filename: str
    title: str
    preview: str


class ConversationsProvider(Protocol):
    def list_conversations(self) -> Iterable[Conversation]:
        ...

    def rename(self, filename: str, new_title: str) -> None:
        ...

    def delete(self, filename: str) -> None:
        ...


class FileSystemConversationsProvider:
    """
    Provider par défaut (fichiers).
    - S'il existe conversations.conversation_manager, on l'utilise.
    - Sinon, on liste un dossier `conversations_dir` (par défaut ./conversations).
    Doc §4 (séparation), §8 (tests), §12 (constantes).
    """

    def __init__(self, conversations_dir: Optional[Path] = None):
        self.conversations_dir = Path(conversations_dir or Path("./conversations")).resolve()

    # ---------- API ----------
    def list_conversations(self) -> Iterable[Conversation]:
        if cm_list and cm_read:
            # On s'appuie sur l’existant si disponible (parité fonctionnelle)
            files = cm_list()
            for filename in files:
                title = self._filename_to_title(filename)
                preview = self._extract_preview_cm(filename)
                yield Conversation(filename=filename, title=title, preview=preview)
            return

        # Fallback : scan du dossier
        if not self.conversations_dir.exists():
            return []

        for path in sorted(self.conversations_dir.glob("*.txt")):
            filename = path.name
            title = self._filename_to_title(filename)
            preview = self._extract_preview_file(path)
            yield Conversation(filename=filename, title=title, preview=preview)

    def rename(self, filename: str, new_title: str) -> None:
        # Si un manager existe, on lui délègue
        if cm_list and cm_read:
            # À implémenter selon API de ton manager s'il expose une fonction rename
            print(f"[RENOMMER/provider] {filename} -> {new_title} (manager non implémenté)")
            return

        src = self.conversations_dir / filename
        if not src.exists():
            print(f"[RENOMMER/provider] Introuvable: {filename}")
            return
        dst = src.with_name(f"{new_title}.txt")
        src.rename(dst)

    def delete(self, filename: str) -> None:
        if cm_list and cm_read:
            # À implémenter selon API du manager s'il expose delete
            print(f"[SUPPRIMER/provider] {filename} (manager non implémenté)")
            return

        path = self.conversations_dir / filename
        if path.exists():
            path.unlink()

    # ---------- Helpers ----------
    def _filename_to_title(self, filename: str) -> str:
        return filename.rsplit(".", 1)[0]

    def _extract_preview_cm(self, filename: str) -> str:
        try:
            content = cm_read(filename)
            return self._extract_first_user_line(content) or self._filename_to_title(filename)
        except Exception:
            return self._filename_to_title(filename)

    def _extract_preview_file(self, path: Path) -> str:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for raw in f:
                    line = raw.strip()
                    # Format attendu: "[2024-..] USER: message"
                    if "]" in line and ":" in line:
                        try:
                            _, rest = line.split("]", 1)
                            role, message = rest.strip().split(":", 1)
                            if role.strip().upper() == "USER":
                                return self._shorten(message.strip().capitalize())
                        except Exception:
                            continue
        except Exception:
            pass
        return self._filename_to_title(path.name)

    def _extract_first_user_line(self, content: str) -> str:
        for raw in content.splitlines():
            line = raw.strip()
            if "]" in line and ":" in line:
                try:
                    _, rest = line.split("]", 1)
                    role, message = rest.strip().split(":", 1)
                    if role.strip().upper() == "USER":
                        return self._shorten(message.strip().capitalize())
                except Exception:
                    continue
        return ""

    def _shorten(self, txt: str) -> str:
        if len(txt) <= SIDEBAR_PREVIEW_MAXLEN:
            return txt
        return txt[: SIDEBAR_PREVIEW_MAXLEN - 1].rstrip() + "…"
