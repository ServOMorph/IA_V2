# -*- coding: utf-8 -*-
"""
conversation_repair.py — version sécurisée
"""

import os
import re
import shutil
import json
from typing import Any, Dict
from . import storage_fs as store
from config import (
    ATTACHED_DOCS_REGISTRY,
    CONVERSATION_FILE_PREFIX as CONV_FILE_PREFIX,
    CONVERSATION_FILE_EXT as CONV_FILE_EXT,
    METADATA_FILE_EXT as CONV_META_EXT,
    CONV_FILENAME_PATTERN
)

# Nom de l'index déterminé depuis storage_fs
CONV_INDEX_FILE = os.path.basename(store.INDEX_PATH)

def _rebuild_index_from_meta():
    """Reconstruit l'index à partir des fichiers .json de conversation."""
    from datetime import datetime
    items = []
    for fname in os.listdir(store.CONVERSATION_DIR):
        if (
            fname.endswith(CONV_META_EXT)
            and fname.lower() != CONV_INDEX_FILE.lower()
            and fname.lower() != os.path.basename(ATTACHED_DOCS_REGISTRY).lower()
        ):
            meta_path = os.path.join(store.CONVERSATION_DIR, fname)
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if meta.get("id") and meta.get("file") and meta.get("meta"):
                    items.append(meta)
            except Exception as e:
                print(f"[Repair] Erreur lecture {fname} : {e}")

    items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    idx_data = {
        "version": store.INDEX_VERSION,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": items
    }
    store.save_index(idx_data)
    print(f"[Repair] Index reconstruit automatiquement avec {len(items)} conversations.")
    return idx_data


def repair_all(safe_mode: bool = False) -> None:
    """Répare les fichiers de conversations et l'index."""
    store.ensure_dir()
    idx = store.load_index()

    # Reconstruction auto si vide ou absent
    index_path = os.path.join(store.CONVERSATION_DIR, CONV_INDEX_FILE)
    if (not idx.get("items") or not os.path.exists(index_path)) and any(
        f.endswith(CONV_META_EXT)
        and f.lower() != CONV_INDEX_FILE.lower()
        and f.lower() != os.path.basename(ATTACHED_DOCS_REGISTRY).lower()
        for f in os.listdir(store.CONVERSATION_DIR)
    ):
        print("[Repair] Index vide ou absent mais conversations détectées → reconstruction…")
        idx = _rebuild_index_from_meta()

    items = idx.get("items", [])
    new_items = []
    removed_count = 0
    fixed_meta_count = 0
    renamed_count = 0
    pattern = re.compile(CONV_FILENAME_PATTERN)

    for item in items:
        conv_file = item.get("file")
        conv_id = item.get("id")
        if not conv_id or not conv_file:
            removed_count += 1
            continue

        txt_path = os.path.join(store.CONVERSATION_DIR, conv_file)
        if not os.path.exists(txt_path):
            print(f"[Repair] Suppression entrée index : fichier {conv_file} manquant")
            removed_count += 1
            continue

        expected_name = f"{CONV_FILE_PREFIX}_{conv_id}{CONV_FILE_EXT}"
        if not pattern.match(conv_file):
            if safe_mode:
                print(f"[Repair] Nom non conforme {conv_file} → devrait être {expected_name}")
            else:
                new_path = os.path.join(store.CONVERSATION_DIR, expected_name)
                shutil.move(txt_path, new_path)
                print(f"[Repair] Renommé {conv_file} → {expected_name}")
                conv_file = expected_name
                item["file"] = expected_name
                renamed_count += 1

        # Correction métadonnées
        meta_path = store.meta_path(conv_id)
        if os.path.exists(meta_path):
            meta_data = store.read_meta(conv_id)
            meta_changed = False
            if meta_data.get("file") != conv_file:
                meta_data["file"] = conv_file
                meta_changed = True
            expected_meta_name = f"{CONV_FILE_PREFIX}_{conv_id}{CONV_META_EXT}"
            if meta_data.get("meta") != expected_meta_name:
                meta_data["meta"] = expected_meta_name
                meta_changed = True
            if meta_changed:
                store.write_meta(conv_id, meta_data)
                fixed_meta_count += 1

        new_items.append(item)

    # Sauvegarde nouvel index
    idx["items"] = new_items
    store.save_index(idx)

    # Suppression fichiers orphelins (exclut index.json et attached_docs.json)
    all_files = set(os.listdir(store.CONVERSATION_DIR))
    used_files = {it["file"] for it in new_items if "file" in it} | {it["meta"] for it in new_items if "meta" in it}
    exclude_files = {
        os.path.basename(ATTACHED_DOCS_REGISTRY).lower(),
        CONV_INDEX_FILE.lower()
    }
    orphan_files = {f for f in all_files if f.lower() not in {uf.lower() for uf in used_files} and f.lower() not in exclude_files}

    for orphan in orphan_files:
        path = os.path.join(store.CONVERSATION_DIR, orphan)
        try:
            if not safe_mode:
                os.remove(path)
            print(f"[Repair] Fichier orphelin supprimé : {orphan}")
        except Exception as e:
            print(f"[Repair] Erreur suppression orphelin {orphan} : {e}")

    print(f"[Repair] {removed_count} entrées supprimées, {fixed_meta_count} métadonnées corrigées, "
          f"{renamed_count} fichiers renommés, {len(orphan_files)} fichiers orphelins supprimés.")
