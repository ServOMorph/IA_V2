import requests
import sys
from config import OLLAMA_URL, OLLAMA_MODEL

def query_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        content = response.json().get("message", {}).get("content", "[Pas de réponse]")
        print(f"[API Ollama] Réponse : {content}", flush=True)
        return content
    except Exception as e:
        print(f"[Erreur API Ollama] {str(e)}", file=sys.stderr, flush=True)
        return "[Erreur de connexion à Ollama]"
