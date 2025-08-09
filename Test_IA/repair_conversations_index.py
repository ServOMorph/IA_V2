import os
import json
from IA_V2.conversations import storage_fs as store

def repair_index_and_files():
    print("=== Réparation de l'index et des fichiers de conversation ===")
    store.ensure_dir()

    # Charger l'index actuel
    idx = store.load_index()
    items = idx.get("items", [])
    print(f"[INFO] Index contient {len(items)} entrées avant nettoyage.")

    new_items = []
    removed_count = 0
    fixed_meta_count = 0

    # 1. Nettoyage : garder seulement les conversations dont le .txt existe
    for item in items:
        conv_file = item.get("file")
        conv_id = item.get("id")
        txt_path = os.path.join(store.CONVERSATION_DIR, conv_file) if conv_file else None

        if not conv_file or not os.path.exists(txt_path):
            print(f"[REMOVE] {conv_id} - {conv_file} (fichier introuvable)")
            removed_count += 1
            continue

        # 2. Vérification des métadonnées
        meta_path = store.meta_path(conv_id)
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)

            meta_changed = False
            expected_meta_file = os.path.basename(txt_path)
            expected_meta_meta = os.path.basename(meta_path)

            if meta_data.get("file") != expected_meta_file:
                print(f"[FIX META] {conv_id} - file: {meta_data.get('file')} -> {expected_meta_file}")
                meta_data["file"] = expected_meta_file
                meta_changed = True

            if meta_data.get("meta") != expected_meta_meta:
                print(f"[FIX META] {conv_id} - meta: {meta_data.get('meta')} -> {expected_meta_meta}")
                meta_data["meta"] = expected_meta_meta
                meta_changed = True

            if meta_changed:
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta_data, f, ensure_ascii=False, indent=2)
                fixed_meta_count += 1
        else:
            print(f"[WARN] Métadonnées manquantes pour {conv_id}")

        new_items.append(item)

    # 3. Sauvegarder l'index nettoyé
    idx["items"] = new_items
    store.save_index(idx)
    print(f"[OK] Index nettoyé. {removed_count} entrées supprimées, {fixed_meta_count} métadonnées corrigées.")

    # 4. Suppression des fichiers orphelins
    all_files = set(os.listdir(store.CONVERSATION_DIR))
    used_files = {it["file"] for it in new_items if "file" in it} | {it["meta"] for it in new_items if "meta" in it}

    orphan_files = all_files - used_files
    for orphan in orphan_files:
        orphan_path = os.path.join(store.CONVERSATION_DIR, orphan)
        try:
            os.remove(orphan_path)
            print(f"[DELETE] Fichier orphelin supprimé : {orphan}")
        except Exception as e:
            print(f"[ERROR] Impossible de supprimer {orphan} : {e}")

    print("[DONE] Réparation terminée.")

if __name__ == "__main__":
    repair_index_and_files()
