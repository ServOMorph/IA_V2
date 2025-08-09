# -*- coding: utf-8 -*-
"""
docs_registry.py
-----------------
Gestion des documents de référence liés aux conversations.
Stockage dans un fichier JSON défini par ATTACHED_DOCS_REGISTRY.
"""

import os
import json
from typing import Any, Dict, List
from config import ATTACHED_DOCS_REGISTRY


# ============================================================================
# Fonctions internes
# ============================================================================
def _ensure_registry_dir() -> None:
    base = os.path.dirname(ATTACHED_DOCS_REGISTRY)
    os.makedirs(base, exist_ok=True)


def _load_registry() -> Dict[str, Any]:
    _ensure_registry_dir()
    if not os.path.exists(ATTACHED_DOCS_REGISTRY):
        return {}
    try:
        with open(ATTACHED_DOCS_REGISTRY, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_registry(reg: Dict[str, Any]) -> None:
    _ensure_registry_dir()
    tmp = ATTACHED_DOCS_REGISTRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, ATTACHED_DOCS_REGISTRY)


def _registry_add_conv(conv_id: str) -> None:
    reg = _load_registry()
    if conv_id not in reg:
        reg[conv_id] = {"reference_docs": []}
        _save_registry(reg)


# ============================================================================
# API publique
# ============================================================================
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


def remove_conversation_docs(conv_id: str) -> None:
    reg = _load_registry()
    if conv_id in reg:
        del reg[conv_id]
        _save_registry(reg)
