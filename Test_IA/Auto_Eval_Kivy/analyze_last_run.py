# -*- coding: utf-8 -*-
"""
Analyse du dernier run Auto_Eval_Kivy.
Lit transcript.jsonl et affiche la discussion + statistiques.
"""

import json
from pathlib import Path
from datetime import datetime

# 📂 Chemin vers outputs/
OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"

def get_last_run_dir():
    """Retourne le dossier le plus récent dans outputs/."""
    dirs = [d for d in OUTPUTS_DIR.iterdir() if d.is_dir()]
    if not dirs:
        raise FileNotFoundError(f"Aucun dossier trouvé dans {OUTPUTS_DIR}")
    return max(dirs, key=lambda d: d.stat().st_mtime)

def load_jsonl(path):
    """Charge un fichier JSONL en liste de dict."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def format_conversation(logs):
    """Retourne une chaîne lisible de la conversation."""
    lines = []
    for entry in logs:
        role = entry["role"]
        ts = entry["ts"]
        txt = entry["text"].strip()
        if role in ("user", "user_displayed", "user_enriched"):
            lines.append(f"[{ts}] 🧑 USER : {txt}")
        elif role in ("assistant_token",):
            # Les tokens intermédiaires sont facultatifs dans l'affichage final
            continue
        elif role in ("assistant_complete", "assistant_displayed"):
            lines.append(f"[{ts}] 🤖 IA : {txt}")
    return "\n".join(lines)

def compute_stats(logs):
    """Calcule quelques statistiques simples."""
    user_msgs = [l for l in logs if l["role"].startswith("user")]
    ai_msgs = [l for l in logs if l["role"] == "assistant_complete"]

    stats = {
        "messages_user": len(user_msgs),
        "messages_ai": len(ai_msgs),
        "total_chars_ai": sum(len(m["text"]) for m in ai_msgs),
    }

    # Temps de réponse IA (du dernier user au assistant_complete)
    if user_msgs and ai_msgs:
        try:
            fmt = "%Y-%m-%d %H:%M:%S.%f"
            t_user = datetime.strptime(user_msgs[-1]["ts"], fmt)
            t_ai = datetime.strptime(ai_msgs[-1]["ts"], fmt)
            stats["derniere_reponse_ms"] = int((t_ai - t_user).total_seconds() * 1000)
        except Exception:
            stats["derniere_reponse_ms"] = None

    return stats

def main():
    last_dir = get_last_run_dir()
    transcript_file = last_dir / "transcript.jsonl"
    print(f"📂 Analyse du run : {last_dir.name}")

    logs = load_jsonl(transcript_file)

    print("\n=== 💬 Conversation ===")
    print(format_conversation(logs))

    print("\n=== 📊 Statistiques ===")
    stats = compute_stats(logs)
    for k, v in stats.items():
        print(f"{k} : {v}")

if __name__ == "__main__":
    main()
