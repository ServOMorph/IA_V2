import os
from datetime import datetime

# 📁 Dossier où les conversations seront enregistrées
CONVERSATION_DIR = os.path.dirname(__file__)

def _ensure_conversation_dir():
    """S'assure que le dossier existe."""
    if not os.path.exists(CONVERSATION_DIR):
        os.makedirs(CONVERSATION_DIR)

def create_new_conversation():
    """Crée un nouveau fichier de conversation horodaté et retourne son chemin complet."""
    _ensure_conversation_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"conversation_{timestamp}.txt"
    filepath = os.path.join(CONVERSATION_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Nouvelle conversation – {timestamp}\n")
    return filepath

def append_message(filepath, role, message):
    """Ajoute un message horodaté dans la conversation."""
    if role not in ("user", "assistant"):
        raise ValueError("Le rôle doit être 'user' ou 'assistant'")
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] {role.upper()}: {message}\n")

def read_conversation(filepath):
    """Retourne le contenu brut du fichier conversation."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def list_conversations():
    """Liste tous les fichiers de conversations disponibles dans le dossier."""
    _ensure_conversation_dir()
    return sorted(f for f in os.listdir(CONVERSATION_DIR) if f.endswith(".txt"))

def rename_conversation_file(old_name, new_name):
    """Renomme physiquement un fichier de conversation."""
    _ensure_conversation_dir()
    old_path = os.path.join(CONVERSATION_DIR, old_name)
    new_path = os.path.join(CONVERSATION_DIR, new_name)
    if not os.path.exists(old_path):
        return False, f"Le fichier '{old_name}' n'existe pas."
    if os.path.exists(new_path):
        return False, f"Un fichier nommé '{new_name}' existe déjà."
    try:
        os.rename(old_path, new_path)
        return True, ""
    except Exception as e:
        return False, f"Erreur lors du renommage : {e}"

def delete_conversation_file(filename):
    """Supprime physiquement un fichier de conversation."""
    _ensure_conversation_dir()
    path = os.path.join(CONVERSATION_DIR, filename)
    if not os.path.exists(path):
        return False, f"Le fichier '{filename}' n'existe pas."
    try:
        os.remove(path)
        return True, ""
    except Exception as e:
        return False, f"Erreur lors de la suppression : {e}"
