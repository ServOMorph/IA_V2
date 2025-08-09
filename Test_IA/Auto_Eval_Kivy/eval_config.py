# -*- coding: utf-8 -*-
"""
Configuration centralisée pour l'évaluation automatisée via Kivy (driver externe).

Conforme au "Document d'apprentissage" :
- Centralisation des constantes (Section 12).
- Journalisation et garde-fous (Section 2).
- Respect du thread UI pour toute interaction Kivy (Section 14).
"""

from pathlib import Path

# --- Points d’ancrage de l’application Kivy à piloter ---
APP_IMPORT_PATH = "main"                 # module qui expose la classe App
APP_CLASS_NAME = "ServOMorph_IAApp"      # classe Kivy App

# Essais d’import pour la classe d’interface (pour monkey-patch ciblé)
CHATINTERFACE_IMPORT_TRY = [
    "interface",                         # si interface/__init__.py exporte ChatInterface
    "interface.chat.chat_interface",     # chemin direct vers la classe
]

CHATINTERFACE_CLASS_NAME = "ChatInterface"

# --- Dossiers / sorties ---
BASE_DIR = Path(__file__).resolve().parents[2]  # .../IA_V2
OUTPUT_BASE_DIR = BASE_DIR / "Test_IA" / "Auto_Eval_Kivy" / "outputs"
OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

# --- Fichiers de logs / transcripts (créés dynamiquement dans un sous-dossier horodaté) ---
TRANSCRIPT_TXT_NAME = "transcript.txt"
TRANSCRIPT_JSONL_NAME = "transcript.jsonl"
SESSION_LOG_NAME = "session.log"

# --- Scénario par défaut ---
DEFAULT_SCENARIO_PATH = BASE_DIR / "Test_IA" / "Auto_Eval_Kivy" / "scenario_example.json"

# --- Options timing ---
SEND_DELAY_MS = 50            # délai min après setting du TextInput avant l’envoi
STEP_SPACING_MS = 300         # espacement par défaut entre étapes
APP_QUIT_AFTER_SCENARIO_MS = 1200  # délai avant App.stop() une fois le scenario terminé

# --- Sécurité / robustesse ---
MAX_MESSAGE_LEN_LOG = 8000    # on tronque dans les logs si dépassé (prévention taille)
LOG_DATETIME_FMT = "%Y-%m-%d %H:%M:%S.%f"

# --- Détection de chemins sensibles de l’app (non bloquant si absent) ---
# NB: chat_stream.py exige Test_IA/Console_Interactif/system_prompt.txt ; s’il n’existe pas,
# l’import dans l’app peut lever FileNotFoundError. Nous ne modifions pas l’app ici.
EXPECTED_SYSTEM_PROMPT = BASE_DIR / "Test_IA" / "Console_Interactif" / "system_prompt.txt"

# --- Hooks à installer (noms de méthodes) ---
HOOKS = {
    "send_message": "send_message",
    "display_message": "display_message",
    "lancer_generation": "lancer_generation",
    "prepare_stream_bubble": "prepare_stream_bubble",
    "update_bubble_text": "update_bubble_text",
    "on_stream_end_final": "on_stream_end_final",
}

# --- Expressions et comportements d’attente pour le scénario ---
DEFAULT_EXPECT_TIMEOUT_MS = 15000  # timeout max pour "expect_reply" (ms)
