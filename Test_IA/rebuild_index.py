# -*- coding: utf-8 -*-
"""
Test_IA/rebuild_index.py
------------------------
Reconstruit conversations/sav_conversations/index.json à partir
des fichiers .json présents dans ce dossier.
Affiche les fichiers trouvés pour debug.
"""

import os
import json
from datetime import datetime

# 📌 Chemin du dossier de sauvegarde des conversations
CONV_DIR = os.path.join("conversations", "sav_conversations")
INDEX_FILE = os.path.join(CONV_DIR, "index.json")

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def rebuild_index():
    print(f"[INFO] Scan du dossier : {os.path.abspath(CONV_DIR)}")
    if not os.path.exists(CONV_DIR):
        print("[ERREUR] Dossier introuvable.")
        return

    items = []
    found_json_files = []

    # Lister tous les fichiers .json
    for fname in os.listdir(CONV_DIR):
        if fname.endswith(".json") and fname != "index.json":
            found_json_files.append(fname)
            meta_path = os.path.join(CONV_DIR, fname)
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                if meta.get("id") and meta.get("file") and meta.get("meta"):
                    items.append(meta)
                else:
                    print(f"[WARN] Fichier ignoré (incomplet) : {fname}")
            except Exception as e:
                print(f"[ERREUR] Lecture {fname} : {e}")

    print(f"[DEBUG] Fichiers .json trouvés : {found_json_files}")

    # Construire la structure d'index
    index_data = {
        "version": 1,
        "updated_at": now_iso(),
        "items": items
    }

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] index.json reconstruit avec {len(items)} conversations.")
    print(f"Chemin : {INDEX_FILE}")

if __name__ == "__main__":
    rebuild_index()
