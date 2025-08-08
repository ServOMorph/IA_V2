# -*- coding: utf-8 -*-
"""
conversations_manager.py
Façade fine au-dessus de storage_fs :
- API moderne par conv_id pour l’UI (recommandée)
- API historique par filepath (compat), pour ne rien casser

Conformité "Document d'apprentissage pour chartgpt.txt":
- §1 Séparation des responsabilités (façade vs stockage)
- §12 Centralisation config (réutilise storage_fs/config)
- §8 Testabilité (façade ultra-mince)
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Any, Tuple

from . import storage_fs as store


# =============================================================================
# API RECOMMANDÉE (par conv_id) — pour la sidebar & le core
# =============================================================================
def list_conversations_index() -> List[Dict[str, Any]]:
    """Liste triée (desc) des conversations depuis l'index.json (lazy-load UI)."""
    return store.list_index_items_sorted()


def create_conversation(title: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Crée une conversation vide + meta + index, retourne l'item d'index."""
    return store.create_conv(title=title, tags=tags)


def append_message_by_id(conv_id: str, role: str, message: str) -> None:
    """Append dans le .txt + MAJ meta + index (écriture atomique)."""
    return store.append_message(conv_id, role, message)


def read_conversation_text_by_id(conv_id: str) -> str:
    """Contenu brut (.txt)."""
    return store.read_conv_text(conv_id)


def get_metadata(conv_id: str) -> Dict[str, Any]:
    """Métadonnées (.json)."""
    return store.read_meta(conv_id)


def rename_conversation(conv_id: str, new_title: str) -> Dict[str, Any]:
    """Change le TITRE (pas les fichiers)."""
    return store.rename_title(conv_id, new_title)


def delete_conversation(conv_id: str) -> None:
    """Supprime .txt, .json et l'entrée d'index."""
    return store.delete_conv(conv_id)


def retitle_from_first_user_line(conv_id: str) -> Optional[str]:
    """Utilitaire: titre = première ligne après un bloc USER, si trouvée."""
    return store.retitle_from_first_user_line(conv_id)


# =============================================================================
# API HISTORIQUE (compat) — par filepath
# =============================================================================
def create_new_conversation() -> str:
    """
    Crée un nouveau fichier .txt (signature historique) mais passe par l'API moderne.
    """
    item = create_conversation(title=f"Nouvelle conversation – {store.ts_for_id()}")
    return store.file_path(item["id"])


def append_message(filepath: str, role: str, message: str) -> None:
    conv_id = store.conv_id_from_filename(os.path.basename(filepath))
    if not conv_id:
        raise ValueError("Nom de fichier inattendu, impossible d'extraire conv_id.")
    return append_message_by_id(conv_id, role, message)


def read_conversation(filepath: str) -> str:
    conv_id = store.conv_id_from_filename(os.path.basename(filepath))
    if not conv_id:
        raise ValueError("Nom de fichier inattendu, impossible d'extraire conv_id.")
    return read_conversation_text_by_id(conv_id)


def list_conversations() -> List[str]:
    """
    Version historique : liste .txt (tri alpha croissant).
    NB: Préférer list_conversations_index() côté UI.
    """
    store.ensure_dir()
    files = [f for f in os.listdir(store.CONVERSATION_DIR) if f.endswith(store.CONV_EXT)]
    return sorted(files)


def rename_conversation_file(old_name: str, new_name: str) -> Tuple[bool, str]:
    """
    Historique : renomme physiquement un .txt (non recommandé).
    On garde la façade minimale : pour cohérence forte, préférer rename_conversation().
    """
    store.ensure_dir()
    old_path = os.path.join(store.CONVERSATION_DIR, old_name)
    new_path = os.path.join(store.CONVERSATION_DIR, new_name)

    if not os.path.exists(old_path):
        return False, f"Le fichier '{old_name}' n'existe pas."
    if os.path.exists(new_path):
        return False, f"Un fichier nommé '{new_name}' existe déjà."

    try:
        os.rename(old_path, new_path)
        # NOTE: pas de rename d'ID/métas ici pour rester une façade “historique” simple.
        # Si tu veux la synchro index/métas, passe par l’API conv_id.
        return True, ""
    except Exception as e:
        return False, f"Erreur lors du renommage : {e}"


def delete_conversation_file(filename: str) -> Tuple[bool, str]:
    """
    Historique : supprime un .txt uniquement (façade minimale).
    Préférer delete_conversation(conv_id) pour cohérence index/métas.
    """
    store.ensure_dir()
    path = os.path.join(store.CONVERSATION_DIR, filename)
    if not os.path.exists(path):
        return False, f"Le fichier '{filename}' n'existe pas."
    try:
        os.remove(path)
        return True, ""
    except Exception as e:
        return False, f"Erreur lors de la suppression : {e}"
