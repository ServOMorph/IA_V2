#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console interactive pour discuter avec Ollama en conservant le contexte.
Utilise query_ollama et query_ollama_stream définis dans ollama_api.py.

Mises à jour :
- Lecture de la consigne système depuis un fichier system_prompt.txt.
- La consigne est toujours envoyée en rôle 'system' en début de conversation.
- Réinitialisation qui conserve cette consigne.
- Conformité §9 et §12 du Document d'apprentissage.
"""

import os
import sys
import datetime as dt

# Ajoute la racine IA_V2 au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ollama_api import query_ollama_stream

# --- Chemins ---
BASE_DIR = os.path.dirname(__file__)
SAVE_DIR = os.path.join(BASE_DIR, "conversations_console")
PROMPT_FILE = os.path.join(BASE_DIR, "system_prompt.txt")

os.makedirs(SAVE_DIR, exist_ok=True)

# --- Lecture du message système ---
if not os.path.exists(PROMPT_FILE):
    print(f"[ERREUR] Fichier manquant : {PROMPT_FILE}", file=sys.stderr)
    sys.exit(1)

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    system_message = f.read().strip()

# --- Mémoire locale de la conversation ---
conversation = [("system", system_message)]


def now_ts():
    """Horodatage simple pour nom de fichier."""
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_conversation():
    """Sauvegarde la conversation actuelle dans un fichier texte."""
    filename = f"conversation_{now_ts()}.txt"
    path = os.path.join(SAVE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        for role, content in conversation:
            f.write(f"{role.upper()} : {content}\n\n")
    print(f"[Conversation sauvegardée : {path}]")


def print_help():
    """Affiche les commandes disponibles."""
    print("""
Commandes :
  :help       → Afficher cette aide
  :reset      → Réinitialiser la conversation (garde la consigne système)
  :save       → Sauvegarder la conversation dans un fichier
  :exit       → Quitter le programme
""")


def main():
    print("=" * 70)
    print(" Mode console interactif — Test mémoire Ollama ")
    print("=" * 70)
    print(f"[Consigne système chargée depuis {PROMPT_FILE}]")
    print("Tapez :help pour les commandes.")
    print("")

    while True:
        try:
            user_input = input("Vous > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[Fin de session]")
            break

        if not user_input:
            continue

        # Commandes spéciales
        if user_input.startswith(":"):
            cmd = user_input.lower()
            if cmd == ":help":
                print_help()
            elif cmd == ":reset":
                conversation.clear()
                conversation.append(("system", system_message))
                print("[Conversation réinitialisée]")
            elif cmd == ":save":
                save_conversation()
            elif cmd == ":exit":
                print("[Quitter]")
                break
            else:
                print("[Commande inconnue — tapez :help]")
            continue

        # Ajout du message utilisateur
        conversation.append(("user", user_input))

        # Construction du prompt complet
        prompt_context = ""
        for role, content in conversation:
            prompt_context += f"{role.upper()} : {content}\n"

        print("IA   > ", end="", flush=True)

        # Capture et affichage token-par-token
        response_chunks = []

        def capture_and_print(token):
            response_chunks.append(token)
            sys.stdout.write(token)
            sys.stdout.flush()

        try:
            query_ollama_stream(prompt_context, capture_and_print)
            full_response = "".join(response_chunks).strip()
        except Exception as e:
            print(f"[Erreur API : {e}]", file=sys.stderr)
            full_response = "[Erreur de connexion à Ollama]"

        # Ajout de la réponse au contexte
        conversation.append(("assistant", full_response))
        print("")


if __name__ == "__main__":
    main()
