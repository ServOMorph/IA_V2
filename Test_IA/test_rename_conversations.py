import os
import json
import time

from IA_V2.conversations.conversation_manager import (
    create_conversation, rename_conversation,
    rename_conversation_file, file_path
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


def test_modern_rename():
    print("\n--- TEST RENOMMAGE API MODERNE ---")
    conv = create_conversation("Titre initial")
    conv_id = conv["id"]

    print_state(conv_id)
    rename_conversation(conv_id, "Nouveau titre moderne")
    print_state(conv_id)


def test_historical_rename():
    print("\n--- TEST RENOMMAGE API HISTORIQUE ---")
    conv = create_conversation("Titre initial histo")
    conv_id = conv["id"]
    old_name = os.path.basename(file_path(conv_id))
    new_name = old_name.replace(".txt", "_renamed.txt")

    print_state(conv_id)
    ok, msg = rename_conversation_file(old_name, new_name)
    print(f"Résultat: ok={ok}, msg='{msg}'")
    print_state(conv_id)


def test_errors():
    print("\n--- TEST CAS D'ERREURS ---")
    ok, msg = rename_conversation_file("inexistant.txt", "test.txt")
    print(f"Renommage inexistant: ok={ok}, msg='{msg}'")

    time.sleep(1)
    conv1 = create_conversation("Conv1")
    time.sleep(1)
    conv2 = create_conversation("Conv2")
    old_name = os.path.basename(file_path(conv1["id"]))
    existing_name = os.path.basename(file_path(conv2["id"]))
    ok, msg = rename_conversation_file(old_name, existing_name)
    print(f"Renommage vers existant: ok={ok}, msg='{msg}'")


if __name__ == "__main__":
    test_modern_rename()
    time.sleep(1)
    test_historical_rename()
    time.sleep(1)
    test_errors()
    print("\n--- INDEX FINAL ---")
    print(json.dumps(store.load_index(), indent=2, ensure_ascii=False))
