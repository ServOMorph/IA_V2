# -*- coding: utf-8 -*-
"""
repair_conversations_meta.py
-----------------------------
Corrige les incohérences entre les métadonnées .json et les fichiers .txt
dans le dossier sav_conversations.

- Détecte les champs "file" non conformes au format canonique "conversation_<ID>.txt"
- Renomme physiquement les fichiers .txt
- Met à jour la métadonnée correspondante
- Sauvegarde .bak avant toute modification
"""

import os
import json
import shutil
import re

# === CONFIGURATION ===
CONV_DIR = os.path.normpath(
    r"C:\Users\raph6\Documents\ServOMorph\IA_V2\conversations\sav_conversations"
)
INDEX_FILE = os.path.join(CONV_DIR, "index.json")
TXT_PATTERN = re.compile(r"^conversation_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.txt$")

def backup_file(path: str):
    """Crée une sauvegarde .bak si elle n'existe pas déjà."""
    if os.path.exists(path):
        bak_path = path + ".bak"
        if not os.path.exists(bak_path):
            shutil.copy2(path, bak_path)
            print(f"[Backup] {bak_path} créé.")

def load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data: dict):
    backup_file(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def repair():
    if not os.path.exists(CONV_DIR):
        print(f"[ERREUR] Dossier introuvable : {CONV_DIR}")
        return

    corrections = 0

    for fname in os.listdir(CONV_DIR):
        if not fname.endswith(".json") or fname == "index.json":
            continue

        meta_path = os.path.join(CONV_DIR, fname)
        meta_data = load_json(meta_path)

        conv_id = meta_data.get("id")
        txt_name = meta_data.get("file")

        if not conv_id or not txt_name:
            continue

        # Si déjà conforme, rien à faire
        if TXT_PATTERN.match(txt_name):
            continue

        new_txt_name = f"conversation_{conv_id}.txt"
        old_txt_path = os.path.join(CONV_DIR, txt_name)
        new_txt_path = os.path.join(CONV_DIR, new_txt_name)

        if os.path.exists(old_txt_path):
            backup_file(old_txt_path)
            os.rename(old_txt_path, new_txt_path)
            print(f"[OK] {txt_name} → {new_txt_name}")
        else:
            print(f"[AVERTISSEMENT] Fichier .txt introuvable : {old_txt_path}")
            continue

        # Mise à jour du champ "file"
        meta_data["file"] = new_txt_name
        save_json(meta_path, meta_data)
        print(f"[Meta] MAJ : {fname}")

        corrections += 1

    if corrections > 0:
        print(f"[Terminé] {corrections} conversation(s) corrigée(s).")
    else:
        print("[Info] Aucune métadonnée incorrecte trouvée.")

if __name__ == "__main__":
    repair()
