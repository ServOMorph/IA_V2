# -*- coding: utf-8 -*-
"""
Test_IA/test_sav_system.py
--------------------------
Teste :
1. Réparation automatique
2. Cycle complet de conversation (création, ajout, lecture, renommage, suppression)
3. Gestion des documents liés
"""

from conversations.conversation_repair import repair_all
from conversations import conversation_manager as cm
import tempfile
import os


def test_repair():
    print("="*50)
    print("1️⃣ TEST REPARATION")
    print("="*50)
    repair_all(safe_mode=True)   # Log uniquement
    repair_all(safe_mode=False)  # Applique les corrections
    print("\n")


def test_cycle_conversation():
    print("="*50)
    print("2️⃣ TEST CYCLE DE VIE CONVERSATION")
    print("="*50)
    conv = cm.create_conversation("Test de conversation")
    print("Créé :", conv)

    cm.append_message_by_id(conv["id"], "user", "Bonjour test")
    cm.append_message_by_id(conv["id"], "assistant", "Réponse test")

    content = cm.read_conversation_text_by_id(conv["id"])
    print("Contenu conversation :\n", content)

    cm.rename_conversation(conv["id"], "Titre modifié")
    print("Titre modifié :", cm.get_metadata(conv["id"]).get("title"))

    cm.delete_conversation(conv["id"])
    print("Suppression OK\n")


def test_docs_lies():
    print("="*50)
    print("3️⃣ TEST DOCUMENTS LIÉS")
    print("="*50)
    conv = cm.create_conversation("Conv avec doc")

    doc_path = os.path.join(tempfile.gettempdir(), "doc_test.txt")
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write("Contenu du document lié.")

    cm.add_reference_doc_by_id(conv["id"], doc_path)
    docs = cm.get_reference_docs_by_id(conv["id"])
    print("Docs liés :", docs)

    cm.delete_conversation(conv["id"])
    print("Suppression conversation et docs liés OK\n")


if __name__ == "__main__":
    test_repair()
    test_cycle_conversation()
    test_docs_lies()

    print("="*50)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("="*50)
