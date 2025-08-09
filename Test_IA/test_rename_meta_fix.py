import os
import json
import time

from IA_V2.conversations.conversation_manager import (
    create_conversation, rename_conversation_file, file_path
)
from IA_V2.conversations import storage_fs as store


def print_state(conv_id):
    """Affiche l’état complet et vérifie la cohérence."""
    txt_path = store.file_path(conv_id)
    meta_path = store.meta_path(conv_id)
    meta = store.read_meta(conv_id)
    idx = store.load_index()

    print(f"\n=== ETAT CONVERSATION {conv_id} ===")
    print(f"[CHECK] file_path() -> {txt_path} | Exists: {os.path.exists(txt_path)}")
    print(f"[CHECK] META path -> {meta_path} | Exists: {os.path.exists(meta_path)}")
    print(f"Meta title: {meta.get('title')}")
    meta_file = meta.get("file", "NON DEFINI")
    print(f"Meta file: {meta_file} | Exists: {os.path.exists(os.path.join(store.CONVERSATION_DIR, meta_file))}")
    item = next((it for it in idx['items'] if it['id'] == conv_id), None)
    if item:
        idx_file = item.get("file", "NON DEFINI")
        print(f"Index file: {idx_file} | Exists: {os.path.exists(os.path.join(store.CONVERSATION_DIR, idx_file))}")
    else:
        print("Index entry: ABSENT")
    print("==============================")


def test_historical_rename_only():
    print("\n--- TEST RENOMMAGE API HISTORIQUE (VALIDATION META) ---")
    conv = create_conversation("Titre initial histo")
    conv_id = conv["id"]
    old_name = os.path.basename(file_path(conv_id))
    new_name = old_name.replace(".txt", "_renamed.txt")

    print("\n[AVANT]")
    print_state(conv_id)

    ok, msg = rename_conversation_file(old_name, new_name)
    print(f"\nRésultat renommage: ok={ok}, msg='{msg}'")

    print("\n[APRES]")
    print_state(conv_id)


if __name__ == "__main__":
    test_historical_rename_only()
    print("\n--- INDEX FINAL ---")
    print(json.dumps(store.load_index(), indent=2, ensure_ascii=False))
