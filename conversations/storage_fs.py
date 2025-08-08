# -*- coding: utf-8 -*-
"""
storage_fs.py
Couche de stockage des conversations sur disque :
- Fichiers .txt (contenu)
- Fichiers .json (métadonnées)
- index.json (liste + méta synthétiques)
- Écritures atomiques, verrous intra-process

Conformité "Document d'apprentissage pour chartgpt.txt":
- §1 Gouvernance du Refactor (séparation claire des responsabilités)
- §2 Journalisation & Stabilité (try/except aux points critiques, atomique)
- §8 Tests & Validation (fonctions pures, faciles à tester)
- §12 Constantes & Config (lecture config.py si présent)
- §14 Threading & Opérations Bloquantes (verrous par conversation + index)
"""

from __future__ import annotations

import os
import io
import json
import tempfile
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

# =============================================================================
# Configuration (override via config.py si dispo)
# =============================================================================
# 1) On essaie de lire depuis config.py (centralisation §12)
try:
    from config import (
        CONVERSATIONS_DIR as _CONF_DIR,
        CONVERSATIONS_INDEX_FILENAME as _CONF_INDEX_NAME,
        CONVERSATION_FILE_PREFIX as _CONF_FILE_PREFIX,
        CONVERSATION_FILE_EXT as _CONF_FILE_EXT,
        METADATA_FILE_EXT as _CONF_META_EXT,
        DEBUG as _CONF_DEBUG,
    )
except Exception:
    # 2) Fallback : on FORCE par défaut le chemin demandé par l'utilisateur
    #    (peut toujours être surchargé via config.py)
    _CONF_DIR = r"C:\Users\raph6\Documents\ServOMorph\IA_V2\conversations\sav_conversations"
    _CONF_INDEX_NAME = "index.json"
    _CONF_FILE_PREFIX = "conversation"
    _CONF_FILE_EXT = ".txt"
    _CONF_META_EXT = ".json"
    _CONF_DEBUG = True

# Normalisation du chemin (utile même sous Windows)
CONVERSATION_DIR = os.path.normpath(_CONF_DIR)
INDEX_PATH = os.path.join(CONVERSATION_DIR, _CONF_INDEX_NAME)
CONV_PREFIX = _CONF_FILE_PREFIX
CONV_EXT = _CONF_FILE_EXT
META_EXT = _CONF_META_EXT
DEBUG = bool(_CONF_DEBUG)

# =============================================================================
# Verrous
# =============================================================================
_index_lock = threading.Lock()
_conv_locks: Dict[str, threading.Lock] = {}
_conv_locks_guard = threading.Lock()


def _get_conv_lock(conv_id: str) -> threading.Lock:
    with _conv_locks_guard:
        if conv_id not in _conv_locks:
            _conv_locks[conv_id] = threading.Lock()
        return _conv_locks[conv_id]


# =============================================================================
# Utilitaires
# =============================================================================
def _log(msg: str) -> None:
    if DEBUG:
        print(f"[storage_fs] {msg}")


def ensure_dir() -> None:
    os.makedirs(CONVERSATION_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ts_for_id() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def atomic_write_text(path: str, content: str, encoding: str = "utf-8") -> None:
    """Écriture atomique : tmp + replace (limite les corruptions) — §2."""
    ensure_dir()
    # Les fichiers temporaires sont créés DANS le dossier cible pour fiabilité des replace
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=CONVERSATION_DIR)
    try:
        with io.open(fd, "w", encoding=encoding, newline="\n") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def read_text(path: str, encoding: str = "utf-8") -> str:
    with io.open(path, "r", encoding=encoding) as f:
        return f.read()


def conv_id_from_filename(filename: str) -> Optional[str]:
    base = os.path.basename(filename)
    if base.startswith(f"{CONV_PREFIX}_") and base.endswith(CONV_EXT):
        return base[len(CONV_PREFIX) + 1 : -len(CONV_EXT)]
    return None


def file_path(conv_id: str) -> str:
    return os.path.join(CONVERSATION_DIR, f"{CONV_PREFIX}_{conv_id}{CONV_EXT}")


def meta_path(conv_id: str) -> str:
    return os.path.join(CONVERSATION_DIR, f"{CONV_PREFIX}_{conv_id}{META_EXT}")


# =============================================================================
# Index (index.json)
# =============================================================================
INDEX_VERSION = 1


def load_index() -> Dict[str, Any]:
    ensure_dir()
    if not os.path.exists(INDEX_PATH):
        idx = {"version": INDEX_VERSION, "updated_at": now_iso(), "items": []}
        atomic_write_text(INDEX_PATH, json.dumps(idx, ensure_ascii=False, indent=2))
        return idx
    try:
        data = json.loads(read_text(INDEX_PATH))
        if "version" not in data:
            data["version"] = INDEX_VERSION
        if "items" not in data:
            data["items"] = []
        return data
    except Exception as e:
        _log(f"index.json illisible → recréé (err: {e})")
        idx = {"version": INDEX_VERSION, "updated_at": now_iso(), "items": []}
        atomic_write_text(INDEX_PATH, json.dumps(idx, ensure_ascii=False, indent=2))
        return idx


def save_index(index: Dict[str, Any]) -> None:
    index["version"] = INDEX_VERSION
    index["updated_at"] = now_iso()
    atomic_write_text(INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2))


def find_in_index(index: Dict[str, Any], conv_id: str) -> Optional[Dict[str, Any]]:
    for it in index.get("items", []):
        if it.get("id") == conv_id:
            return it
    return None


# =============================================================================
# Métadonnées
# =============================================================================
def write_meta(conv_id: str, meta: Dict[str, Any]) -> None:
    atomic_write_text(meta_path(conv_id), json.dumps(meta, ensure_ascii=False, indent=2))


def read_meta(conv_id: str) -> Dict[str, Any]:
    p = meta_path(conv_id)
    if not os.path.exists(p):
        return {}
    try:
        return json.loads(read_text(p))
    except Exception as e:
        _log(f"meta illisible pour {conv_id}: {e}")
        return {}


# =============================================================================
# Opérations haut-niveau (utilisées par la façade)
# =============================================================================
def list_index_items_sorted() -> List[Dict[str, Any]]:
    idx = load_index()
    items = idx.get("items", [])
    try:
        items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    except Exception:
        pass
    return items


def create_conv(title: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    conv_id = ts_for_id()
    file_name = f"{CONV_PREFIX}_{conv_id}{CONV_EXT}"
    meta_name = f"{CONV_PREFIX}_{conv_id}{META_EXT}"
    ts = now_iso()

    item = {
        "id": conv_id,
        "title": (title or conv_id).strip(),
        "file": file_name,
        "meta": meta_name,
        "created_at": ts,
        "updated_at": ts,
        "message_count": 0,
        "tags": list(tags or []),
    }

    atomic_write_text(file_path(conv_id), "")
    write_meta(conv_id, {**item})

    with _index_lock:
        idx = load_index()
        idx["items"].append(item)
        save_index(idx)

    _log(f"Conversation créée: {conv_id} '{item['title']}'")
    return item


def append_message(conv_id: str, role: str, message: str) -> None:
    role_norm = (role or "").strip().lower()
    if role_norm not in ("user", "assistant", "ai"):
        role_norm = "user"

    lock = _get_conv_lock(conv_id)
    with lock:
        p = file_path(conv_id)
        if not os.path.exists(p):
            raise FileNotFoundError(f"Conversation introuvable: {conv_id}")

        ts = now_iso()
        existing = read_text(p) if os.path.getsize(p) > 0 else ""
        block = f"\n[{ts}] {role_norm.upper()}: {message}\n"
        atomic_write_text(p, existing + block)

        meta = read_meta(conv_id)
        meta["updated_at"] = ts
        meta["message_count"] = int(meta.get("message_count", 0)) + 1
        write_meta(conv_id, meta)

        with _index_lock:
            idx = load_index()
            it = find_in_index(idx, conv_id)
            if it:
                it["updated_at"] = ts
                it["message_count"] = int(it.get("message_count", 0)) + 1
                save_index(idx)

    _log(f"Append [{role_norm}] {conv_id} ({len(message)} chars)")


def read_conv_text(conv_id: str) -> str:
    p = file_path(conv_id)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Conversation introuvable: {conv_id}")
    return read_text(p)


def rename_title(conv_id: str, new_title: str) -> Dict[str, Any]:
    new_title = (new_title or "").strip()
    if not new_title:
        raise ValueError("Le nouveau titre est vide.")

    lock = _get_conv_lock(conv_id)
    with lock:
        ts = now_iso()
        meta = read_meta(conv_id)
        if not meta:
            raise FileNotFoundError("Métadonnées introuvables.")

        meta["title"] = new_title
        meta["updated_at"] = ts
        write_meta(conv_id, meta)

        with _index_lock:
            idx = load_index()
            it = find_in_index(idx, conv_id)
            if not it:
                raise FileNotFoundError("Conversation absente de l'index.")
            it["title"] = new_title
            it["updated_at"] = ts
            save_index(idx)

    _log(f"Titre changé → {conv_id} -> '{new_title}'")
    return meta


def delete_conv(conv_id: str) -> None:
    lock = _get_conv_lock(conv_id)
    with lock:
        txt = file_path(conv_id)
        meta = meta_path(conv_id)
        for p in (txt, meta):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception as e:
                _log(f"Erreur suppression '{p}': {e}")
                raise

        with _index_lock:
            idx = load_index()
            idx["items"] = [it for it in idx.get("items", []) if it.get("id") != conv_id]
            save_index(idx)

    _log(f"Conversation supprimée: {conv_id}")


def retitle_from_first_user_line(conv_id: str) -> Optional[str]:
    raw = read_conv_text(conv_id)
    take_next_non_empty = False
    first: Optional[str] = None
    for line in raw.splitlines():
        s = line.strip()
        if s.upper().startswith("USER:") or (s.startswith("[") and "USER:" in s.upper()):
            take_next_non_empty = True
            continue
        if take_next_non_empty and s:
            first = s
            break
    title = first or conv_id
    rename_title(conv_id, title)
    return title
