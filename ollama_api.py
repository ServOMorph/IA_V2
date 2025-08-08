import requests
import sys
from config import OLLAMA_URL, OLLAMA_MODEL

def query_ollama(prompt_or_messages):
    """
    Version classique, réponse complète.
    Accepte soit un prompt simple (str), soit une liste de messages formatés.
    """
    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = prompt_or_messages

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
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

def query_ollama_stream(prompt_or_messages, on_token_callback):
    """
    Version streaming : appelle on_token_callback(token) à chaque token reçu.
    Accepte soit un prompt simple (str), soit une liste de messages formatés.
    """
    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = prompt_or_messages

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True
    }

    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        data = line.decode("utf-8").strip()
                        if data.startswith("data: "):
                            data = data[6:]
                        import json
                        parsed = json.loads(data)
                        token = parsed.get("message", {}).get("content", "")
                        if token:
                            on_token_callback(token)
                    except Exception as parse_error:
                        print(f"[Stream] Erreur de parsing : {parse_error}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[Erreur API Streaming Ollama] {str(e)}", file=sys.stderr, flush=True)
        on_token_callback("\n[Erreur de connexion à Ollama]")
