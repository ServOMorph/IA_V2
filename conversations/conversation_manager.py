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
# Réparation automatique au démarrage
# ============================================================================
def repair_conversations():
    """
    Répare l'index et les fichiers de conversation :
    - Supprime les entrées dont le fichier .txt n'existe plus
    - Corrige les champs 'file' et 'meta' dans les métadonnées
    - Supprime les fichiers orphelins
    """
    store.ensure_dir()

    idx = store.load_index()
    items = idx.get("items", [])
    new_items = []
    removed_count = 0
    fixed_meta_count = 0

    for item in items:
        conv_file = item.get("file")
        conv_id = item.get("id")
        txt_path = os.path.join(store.CONVERSATION_DIR, conv_file) if conv_file else None

        if not conv_file or not os.path.exists(txt_path):
            removed_count += 1
            continue

        meta_path = store.meta_path(conv_id)
        if os.path.exists(meta_path):
            meta_data = store.read_meta(conv_id)
            meta_changed = False

            expected_meta_file = os.path.basename(txt_path)
            expected_meta_meta = os.path.basename(meta_path)

            if meta_data.get("file") != expected_meta_file:
                meta_data["file"] = expected_meta_file
                meta_changed = True

            if meta_data.get("meta") != expected_meta_meta:
                meta_data["meta"] = expected_meta_meta
                meta_changed = True

            if meta_changed:
                store.write_meta(conv_id, meta_data)
                fixed_meta_count += 1

        new_items.append(item)

    idx["items"] = new_items
    store.save_index(idx)

    all_files = set(os.listdir(store.CONVERSATION_DIR))
    used_files = {it["file"] for it in new_items if "file" in it} | {it["meta"] for it in new_items if "meta" in it}
    orphan_files = all_files - used_files
    for orphan in orphan_files:
        try:
            os.remove(os.path.join(store.CONVERSATION_DIR, orphan))
        except Exception:
            pass

    print(f"[Repair] {removed_count} entrées supprimées, {fixed_meta_count} métadonnées corrigées, {len(orphan_files)} fichiers orphelins supprimés.")


# Appel automatique de la réparation
try:
    repair_conversations()
except Exception as e:
    print(f"[Repair] Échec de la réparation automatique : {e}")


# ============================================================================
# Centralisation / Config : on tente d'importer depuis config.py
# ============================================================================
_ATTACHED_DOCS_REGISTRY_DEFAULT = os.path.join(
    "conversations", "sav_conversations", "attached_docs.json"
)

try:
    from config import ATTACHED_DOCS_REGISTRY as _ATTACHED_DOCS_REGISTRY  # type: ignore
except Exception:
    _ATTACHED_DOCS_REGISTRY = _ATTACHED_DOCS_REGISTRY_DEFAULT


# =============================================================================
# OUTILS REGISTRE DOCS
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
# API RECOMMANDÉE
# =============================================================================
def list_conversations_index() -> List[Dict[str, Any]]:
    return store.list_index_items_sorted()

def create_conversation(title: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    item = store.create_conv(title=title, tags=tags)
    _registry_add_conv(item["id"])
    return item

def append_message_by_id(conv_id: str, role: str, message: str) -> None:
    return store.append_message(conv_id, role, message)

def read_conversation_text_by_id(conv_id: str) -> str:
    return store.read_conv_text(conv_id)

def get_metadata(conv_id: str) -> Dict[str, Any]:
    return store.read_meta(conv_id)

def rename_conversation(conv_id: str, new_title: str) -> Dict[str, Any]:
    return store.rename_title(conv_id, new_title)

def delete_conversation(conv_id: str) -> None:
    store.delete_conv(conv_id)
    reg = _load_registry()
    if conv_id in reg:
        del reg[conv_id]
        _save_registry(reg)

def delete_all_conversations() -> None:
    items = list_conversations_index()
    for item in items:
        conv_id = item.get("id")
        if conv_id:
            delete_conversation(conv_id)
    idx = {"version": store.INDEX_VERSION, "updated_at": store.now_iso(), "items": []}
    store.save_index(idx)
    _save_registry({})

def retitle_from_first_user_line(conv_id: str) -> Optional[str]:
    return store.retitle_from_first_user_line(conv_id)


# -----------------------------------------------------------------------------
# Docs de référence
# -----------------------------------------------------------------------------
def add_reference_doc_by_id(conv_id: str, doc_path: str) -> None:
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
    if not conv_id:
        return []
    reg = _load_registry()
    entry = reg.get(conv_id, {})
    return list(entry.get("reference_docs", []))


# =============================================================================
# API HISTORIQUE
# =============================================================================
def create_new_conversation() -> str:
    item = create_conversation(title=f"Nouvelle conversation – {store.ts_for_id()}")
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
    store.ensure_dir()
    files = [f for f in os.listdir(store.CONVERSATION_DIR) if f.endswith(store.CONV_EXT)]
    return sorted(files)

def rename_conversation_file(old_name: str, new_name: str) -> Tuple[bool, str]:
    """
    Historique : renomme physiquement un .txt MAIS garde le .json associé inchangé.
    Met à jour title et file dans les métadonnées et l'index.
    """
    store.ensure_dir()
    old_path = os.path.join(store.CONVERSATION_DIR, old_name)
    new_path = os.path.join(store.CONVERSATION_DIR, new_name)

    if not os.path.exists(old_path):
        return False, f"Le fichier '{old_name}' n'existe pas."
    if os.path.exists(new_path):
        return False, f"Un fichier nommé '{new_name}' existe déjà."

    conv_id = store.conv_id_from_filename(old_name)
    if not conv_id:
        return False, "Impossible de déterminer conv_id à partir du nom de fichier."

    # Lire meta avant renommage
    meta_backup = store.read_meta(conv_id)
    if not meta_backup:
        return False, "Métadonnées introuvables."

    try:
        # Renommer uniquement le .txt
        os.rename(old_path, new_path)

        # Mettre à jour le contenu des métadonnées
        title_from_name = os.path.splitext(new_name)[0]
        meta_backup["title"] = title_from_name
        meta_backup["file"] = os.path.basename(new_path)
        # ⚠️ On ne touche pas à meta_backup["meta"], il garde le .json original
        store.write_meta(conv_id, meta_backup)

        # Mettre à jour l'index
        idx = store.load_index()
        item = store.find_in_index(idx, conv_id)
        if item:
            item["title"] = title_from_name
            item["file"] = os.path.basename(new_path)
            # item["meta"] reste inchangé
            store.save_index(idx)

        return True, ""
    except Exception as e:
        return False, f"Erreur lors du renommage : {e}"

def delete_conversation_file(filename: str) -> Tuple[bool, str]:
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
# Compat docs liés
# -----------------------------------------------------------------------------
def add_reference_doc(conversation_filepath: str, doc_path: str) -> None:
    conv_id = _conv_id_from_filepath(conversation_filepath)
    if not conv_id:
        raise ValueError("Nom de fichier inattendu, impossible d'extraire conv_id.")
    return add_reference_doc_by_id(conv_id, doc_path)

def get_reference_docs(conversation_filepath: str) -> List[str]:
    conv_id = _conv_id_from_filepath(conversation_filepath)
    if not conv_id:
        return []
    return get_reference_docs_by_id(conv_id)


# -----------------------------------------------------------------------------
# Ré-export utilitaires
# -----------------------------------------------------------------------------
def conv_id_from_filename(filename: str) -> Optional[str]:
    return store.conv_id_from_filename(filename)

def file_path(conv_id: str) -> str:
    return store.file_path(conv_id)

def ts_for_id() -> str:
    return store.ts_for_id()
