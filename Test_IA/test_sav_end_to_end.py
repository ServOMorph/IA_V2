import os
import json
import time
from IA_V2.conversations import storage_fs as store
from IA_V2.conversations import conversation_manager as cm


def check_coherence(label=""):
    """
    Vérifie que tous les éléments dans l'index ont leurs fichiers et métadonnées cohérents.
    """
    print(f"\n[CHECK COHERENCE] {label}")
    idx = store.load_index()
    ok = True
    for item in idx.get("items", []):
        cid = item["id"]
        txt_path = store.file_path(cid)
        meta_path = store.meta_path(cid)
        meta = store.read_meta(cid)

        if not os.path.exists(txt_path):
            print(f"[ERROR] {cid} : Fichier TXT manquant -> {txt_path}")
            ok = False
        if not os.path.exists(meta_path):
            print(f"[ERROR] {cid} : Fichier META manquant -> {meta_path}")
            ok = False

        if meta.get("file") != os.path.basename(txt_path):
            print(f"[ERROR] {cid} : meta['file'] incohérent ({meta.get('file')} != {os.path.basename(txt_path)})")
            ok = False
        if meta.get("meta") != os.path.basename(meta_path):
            print(f"[ERROR] {cid} : meta['meta'] incohérent ({meta.get('meta')} != {os.path.basename(meta_path)})")
            ok = False

        if item.get("file") != os.path.basename(txt_path):
            print(f"[ERROR] {cid} : index['file'] incohérent ({item.get('file')} != {os.path.basename(txt_path)})")
            ok = False
        if item.get("meta") != os.path.basename(meta_path):
            print(f"[ERROR] {cid} : index['meta'] incohérent ({item.get('meta')} != {os.path.basename(meta_path)})")
            ok = False

    if ok:
        print("[OK] Cohérence totale.")
    return ok


def run_tests():
    print("=== TEST END-TO-END SAV ===")

    # 0. Nettoyage initial
    cm.delete_all_conversations()

    # 1. Création
    print("\n[TEST] Création de conversation")
    conv = cm.create_conversation("Titre initial")
    cid = conv["id"]
    check_coherence("Après création")

    # 2. Lecture / Append
    print("\n[TEST] Ajout et lecture de message")
    cm.append_message_by_id(cid, "user", "Bonjour !")
    txt = cm.read_conversation_text_by_id(cid)
    assert "Bonjour !" in txt, "[FAIL] Append ou lecture échoué"
    print("[OK] Append et lecture fonctionnels.")

    # 3. Renommage moderne
    print("\n[TEST] Renommage moderne (titre uniquement)")
    cm.rename_conversation(cid, "Nouveau titre moderne")
    check_coherence("Après renommage moderne")

    # 4. Renommage historique
    print("\n[TEST] Renommage historique (fichiers + meta + index)")
    old_name = os.path.basename(store.file_path(cid))
    new_name = old_name.replace(".txt", "_renamed.txt")
    ok, msg = cm.rename_conversation_file(old_name, new_name)
    assert ok, f"[FAIL] Renommage historique échoué: {msg}"
    check_coherence("Après renommage historique")

    # 5. Suppression
    print("\n[TEST] Suppression conversation")
    cm.delete_conversation(cid)
    assert not os.path.exists(store.file_path(cid)), "[FAIL] Fichier TXT toujours présent après suppression"
    assert not os.path.exists(store.meta_path(cid)), "[FAIL] Fichier META toujours présent après suppression"
    print("[OK] Suppression individuelle fonctionnelle.")
    check_coherence("Après suppression")

    # 6. Test nettoyage automatique
    print("\n[TEST] Réparation automatique")
    conv2 = cm.create_conversation("Test nettoyage")
    cid2 = conv2["id"]
    os.remove(store.file_path(cid2))  # Simule fichier manquant
    cm.repair_conversations()  # Appel manuel
    idx = store.load_index()
    assert not any(it["id"] == cid2 for it in idx["items"]), "[FAIL] Entrée fantôme non supprimée"
    print("[OK] Réparation automatique supprime bien les fantômes.")

    print("\n=== FIN TESTS ===")
    check_coherence("Final")


if __name__ == "__main__":
    run_tests()
