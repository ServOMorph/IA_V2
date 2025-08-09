# -*- coding: utf-8 -*-
"""
conversations_manager.py
Façade fine au-dessus de storage_fs :
- API moderne par conv_id pour l’UI (recommandée)
- API historique par filepath (compat), pour ne rien casser

Conformité "Document d'apprentissage pour chartgpt.txt":
- §1 Séparation des responsabilités (façade vs stockage)
- §12 Centralisation config (réutilise storage_fs/config si dispo)
- §8 Testabilité (façade ultra-mince)
"""

from __future__ import annotations

import os
import json
from typing import Dict, List, Optional, Any, Tuple

from . import storage_fs as store

# ============================================================================
# Centralisation / Config : on tente d'importer depuis config.py
# ============================================================================
_ATTACHED_DOCS_REGISTRY_DEFAULT = os.path.join(
    "conversations", "sav_conversations", "attached_docs.json"
)

try:
    # Optionnel : si présent dans config.py, on l'utilise (Doc §12)
    from config import ATTACHED_DOCS_REGISTRY as _ATTACHED_DOCS_REGISTRY  # type: ignore
except Exception:
    _ATTACHED_DOCS_REGISTRY = _ATTACHED_DOCS_REGISTRY_DEFAULT


# =============================================================================
# OUTILS REGISTRE DOCS (persistance légère et atomique)
# Clé = conv_id ; valeur = {"reference_docs": [<abs paths>]}
# =============================================================================
def _ensure_registry_dir() -> None:
    base = os.path.dirname(_ATTACHED_DOCS_REGISTRY)
    os.makedirs(base, exist_ok=True)

def _load_registry() -> Dict[str, Any]:
    _ensure_registry_dir()
    if not os.path.exists(_ATTACHED_DOCS_REGISTRY):
        return {}
    try:
        with open(_ATTACHED_DOCS_REGISTRY, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_registry(reg: Dict[str, Any]) -> None:
    _ensure_registry_dir()
    tmp = _ATTACHED_DOCS_REGISTRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _ATTACHED_DOCS_REGISTRY)

def _registry_add_conv(conv_id: str) -> None:
    reg = _load_registry()
    if conv_id not in reg:
        reg[conv_id] = {"reference_docs": []}
        _save_registry(reg)

def _conv_id_from_filepath(filepath: str) -> Optional[str]:
    filename = os.path.basename(filepath)
    return store.conv_id_from_filename(filename)


# =============================================================================
# API RECOMMANDÉE (par conv_id) — pour la sidebar & le core
# =============================================================================
def list_conversations_index() -> List[Dict[str, Any]]:
    """Liste triée (desc) des conversations depuis l'index.json (lazy-load UI)."""
    return store.list_index_items_sorted()

def create_conversation(title: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Crée une conversation vide + meta + index, retourne l'item d'index."""
    item = store.create_conv(title=title, tags=tags)
    # prépare le registre des docs pour ce conv_id
    _registry_add_conv(item["id"])
    return item

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
    """Supprime .txt, .json et l'entrée d'index + purge registre docs."""
    # supprime côté storage
    store.delete_conv(conv_id)
    # nettoie le registre des docs
    reg = _load_registry()
    if conv_id in reg:
        del reg[conv_id]
        _save_registry(reg)

def retitle_from_first_user_line(conv_id: str) -> Optional[str]:
    """Utilitaire: titre = première ligne après un bloc USER, si trouvée."""
    return store.retitle_from_first_user_line(conv_id)


# -----------------------------------------------------------------------------
# Docs de référence par conversation (API moderne conv_id)
# -----------------------------------------------------------------------------
def add_reference_doc_by_id(conv_id: str, doc_path: str) -> None:
    """
    Lie un document texte à la conversation (par conv_id).
    On stocke le chemin ABSOLU ; pas de copie physique.
    Idempotent (pas de doublon).
    """
    if not conv_id:
        raise ValueError("conv_id manquant")

    reg = _load_registry()
    if conv_id not in reg:
        reg[conv_id] = {"reference_docs": []}

    docs = reg[conv_id].get("reference_docs", [])
    doc_abs = os.path.abspath(doc_path)
    if doc_abs not in docs:
        docs.append(doc_abs)
    reg[conv_id]["reference_docs"] = docs
    _save_registry(reg)

def get_reference_docs_by_id(conv_id: str) -> List[str]:
    """
    Retourne la liste des chemins ABSOLUS des documents liés à conv_id.
    """
    if not conv_id:
        return []
    reg = _load_registry()
    entry = reg.get(conv_id, {})
    return list(entry.get("reference_docs", []))


# =============================================================================
# API HISTORIQUE (compat) — par filepath
# =============================================================================
def create_new_conversation() -> str:
    """
    Crée un nouveau fichier .txt (signature historique) mais passe par l'API moderne.
    """
    # Titre par défaut horodaté via utilitaire de storage
    item = create_conversation(title=f"Nouvelle conversation – {store.ts_for_id()}")
    # retourne le chemin historique (.txt) pour compat
    return store.file_path(item["id"])

def append_message(filepath: str, role: str, message: str) -> None:
    conv_id = _conv_id_from_filepath(filepath)
    if not conv_id:
        raise ValueError("Nom de fichier inattendu, impossible d'extraire conv_id.")
    return append_message_by_id(conv_id, role, message)

def read_conversation(filepath: str) -> str:
    conv_id = _conv_id_from_filepath(filepath)
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


# -----------------------------------------------------------------------------
# Compatibilité : mapping filepath -> conv_id pour les docs liés
# -----------------------------------------------------------------------------
def add_reference_doc(conversation_filepath: str, doc_path: str) -> None:
    """
    Compat historique : ajoute un doc lié en partant d'un filepath (.txt).
    """
    conv_id = _conv_id_from_filepath(conversation_filepath)
    if not conv_id:
        raise ValueError("Nom de fichier inattendu, impossible d'extraire conv_id.")
    return add_reference_doc_by_id(conv_id, doc_path)

def get_reference_docs(conversation_filepath: str) -> List[str]:
    """
    Compat historique : liste les docs liés en partant d'un filepath (.txt).
    """
    conv_id = _conv_id_from_filepath(conversation_filepath)
    if not conv_id:
        return []
    return get_reference_docs_by_id(conv_id)


# -----------------------------------------------------------------------------
# Ré-export utilitaires utiles côté UI (pour éviter d'importer storage_fs partout)
# -----------------------------------------------------------------------------
def conv_id_from_filename(filename: str) -> Optional[str]:
    """Ré-export de l’utilitaire storage_fs."""
    return store.conv_id_from_filename(filename)

def file_path(conv_id: str) -> str:
    """Ré-export : chemin .txt de la conversation."""
    return store.file_path(conv_id)

def ts_for_id() -> str:
    """Ré-export : timestamp formaté utilisé pour les IDs."""
    return store.ts_for_id()
