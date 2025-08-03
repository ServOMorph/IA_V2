import requests
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
        print(f"[API Ollama] Réponse : {content}")
        return content
    except Exception as e:
        print(f"[Erreur API Ollama] {str(e)}")
        return "[Erreur de connexion à Ollama]"
