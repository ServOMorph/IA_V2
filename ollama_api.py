import requests
import json
import os
from datetime import datetime
from config import OLLAMA_URL, OLLAMA_MODEL, DEBUG_API, API_TRACE_FILE

# === Vidage du fichier à chaque lancement ===
if DEBUG_API:
    try:
        with open(API_TRACE_FILE, "w", encoding="utf-8") as f:
            f.write("")  # vide le fichier
    except Exception:
        pass

def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _trace(line: str):
    if not DEBUG_API:
        return
    try:
        with open(API_TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{_ts()} {line}\n")
    except Exception:
        pass

def _trace_json(obj, prefix=""):
    if not DEBUG_API:
        return
    try:
        text = json.dumps(obj, ensure_ascii=False, indent=2)
        for l in text.splitlines():
            _trace(f"{prefix}{l}")
    except Exception as e:
        _trace(f"[TRACE_JSON_ERROR] {e}")

def query_ollama(prompt_or_messages):
    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = prompt_or_messages

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }

    _trace(f"[OUTGOING] POST {OLLAMA_URL}")
    _trace_json(payload, prefix="[PAYLOAD] ")

    try:
        resp = requests.post(OLLAMA_URL, json=payload)
        _trace(f"[HTTP] status={resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        _trace_json(data, prefix="[RAW_RESPONSE] ")

        content = data.get("message", {}).get("content", "")
        _trace(f"[ASSISTANT_COMPLETE] {content}")
        return content or "[Pas de réponse]"
    except Exception as e:
        _trace(f"[ERROR] {e}")
        return "[Erreur de connexion à Ollama]"

def query_ollama_stream(prompt_or_messages, on_token_callback):
    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = prompt_or_messages

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True
    }

    _trace(f"[OUTGOING] POST {OLLAMA_URL} (stream=True)")
    _trace_json(payload, prefix="[PAYLOAD] ")

    collected = []
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True) as resp:
            _trace(f"[HTTP] status={resp.status_code} (stream)")
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data = line.decode("utf-8").strip()
                    if data.startswith("data: "):
                        data = data[6:]
                    parsed = json.loads(data)
                except Exception as parse_err:
                    _trace(f"[STREAM_PARSE_ERROR] {parse_err} / raw={line!r}")
                    continue

                token = parsed.get("message", {}).get("content", "")
                if token:
                    collected.append(token)
                    _trace(f"[TOKEN] {token}")
                    on_token_callback(token)

        # réponse complète après le stream
        full_text = "".join(collected)
        _trace(f"[ASSISTANT_COMPLETE] {full_text}")
    except Exception as e:
        _trace(f"[ERROR] {e}")
        on_token_callback("\n[Erreur de connexion à Ollama]")
