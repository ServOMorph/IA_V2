# -*- coding: utf-8 -*-
"""
Driver externe pour lancer l'app Kivy, injecter des messages et journaliser 100% des échanges.

Version séquentielle : chaque nouvelle question est envoyée après la fin du streaming de la réponse précédente.
Ajout : log explicite des messages utilisateur ("role": "user") pour permettre le calcul des temps de réponse.
"""

import io
import json
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

from .eval_config import (
    APP_IMPORT_PATH, APP_CLASS_NAME,
    CHATINTERFACE_IMPORT_TRY, CHATINTERFACE_CLASS_NAME,
    OUTPUT_BASE_DIR, TRANSCRIPT_TXT_NAME, TRANSCRIPT_JSONL_NAME, SESSION_LOG_NAME,
    DEFAULT_SCENARIO_PATH, SEND_DELAY_MS, MAX_MESSAGE_LEN_LOG, LOG_DATETIME_FMT,
    EXPECTED_SYSTEM_PROMPT, HOOKS, DEFAULT_EXPECT_TIMEOUT_MS,
)

from kivy.clock import Clock
from kivy.app import App

# --- Helpers ---
def now_str():
    return datetime.now().strftime(LOG_DATETIME_FMT)

class EvalLogger:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.txt_path = out_dir / TRANSCRIPT_TXT_NAME
        self.jsonl_path = out_dir / TRANSCRIPT_JSONL_NAME
        self.session_log_path = out_dir / SESSION_LOG_NAME
        self._txt = io.open(self.txt_path, "w", encoding="utf-8")
        self._jsonl = io.open(self.jsonl_path, "w", encoding="utf-8")
        self._session = io.open(self.session_log_path, "w", encoding="utf-8")
        self._assistant_accumulator = ""

    def close(self):
        for f in (self._txt, self._jsonl, self._session):
            try: f.close()
            except Exception: pass

    def _truncate(self, s: str) -> str:
        if s is None:
            return ""
        if len(s) > MAX_MESSAGE_LEN_LOG:
            return s[:MAX_MESSAGE_LEN_LOG] + f"\n[... TRONQUÉ ({len(s)} chars) ...]"
        return s

    def log_event(self, role: str, text: str, meta: dict | None = None):
        t = now_str()
        safe = self._truncate(text)
        self._txt.write(f"[{t}] {role.upper()}: {safe}\n")
        self._txt.flush()
        self._jsonl.write(json.dumps({"ts": t, "role": role, "text": safe, "meta": meta or {}}, ensure_ascii=False) + "\n")
        self._jsonl.flush()

    def log_system(self, message: str, meta: dict | None = None):
        t = now_str()
        self._session.write(f"[{t}] {message} | meta={json.dumps(meta or {}, ensure_ascii=False)}\n")
        self._session.flush()

    def on_assistant_partial(self, full_text: str):
        prev = self._assistant_accumulator
        if full_text.startswith(prev):
            delta = full_text[len(prev):]
        else:
            delta = full_text
        if delta:
            self.log_event("assistant_token", delta, {"len_delta": len(delta)})
        self._assistant_accumulator = full_text

    def on_assistant_complete(self, full_text: str):
        self.log_event("assistant_complete", full_text, {"len_total": len(full_text)})

def load_scenario(path: Path) -> list[dict]:
    if not path.exists():
        return [{"action": "send_user", "text": "Test : dis 'pong' puis stop"}]
    with io.open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("scenario JSON must be a list")
        return data

def try_import_chatinterface():
    last_exc = None
    for modname in CHATINTERFACE_IMPORT_TRY:
        try:
            mod = __import__(modname, fromlist=[CHATINTERFACE_CLASS_NAME])
            return getattr(mod, CHATINTERFACE_CLASS_NAME)
        except Exception as e:
            last_exc = e
    raise ImportError(f"Impossible d’importer {CHATINTERFACE_CLASS_NAME} depuis {CHATINTERFACE_IMPORT_TRY}: {last_exc}")

# --- Driver ---
def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_BASE_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    logger = EvalLogger(out_dir)
    logger.log_system("Driver démarré", {"out_dir": str(out_dir)})

    if not EXPECTED_SYSTEM_PROMPT.exists():
        logger.log_system("AVERTISSEMENT: system_prompt.txt manquant", {"expected_path": str(EXPECTED_SYSTEM_PROMPT)})

    class Tee:
        def __init__(self, *streams): self.streams = streams
        def write(self, s): [st.write(s) or st.flush() for st in self.streams if hasattr(st, "write")]
        def flush(self): [st.flush() for st in self.streams if hasattr(st, "flush")]

    orig_out, orig_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = Tee(sys.stdout, logger._session), Tee(sys.stderr, logger._session)

    try:
        app_mod = __import__(APP_IMPORT_PATH, fromlist=[APP_CLASS_NAME])
        AppClass = getattr(app_mod, APP_CLASS_NAME)
        ChatInterfaceClass = try_import_chatinterface()

        scenario_steps = load_scenario(DEFAULT_SCENARIO_PATH)
        logger.log_system("Scénario chargé", {"steps": len(scenario_steps)})

        original_methods = {}
        step_index = {"value": 0}

        def install_hooks(chat):
            if hasattr(chat, HOOKS["update_bubble_text"]):
                original_methods[HOOKS["update_bubble_text"]] = getattr(chat, HOOKS["update_bubble_text"])
                def wrapped_update(text):
                    logger.on_assistant_partial(text or "")
                    return original_methods[HOOKS["update_bubble_text"]](text)
                setattr(chat, HOOKS["update_bubble_text"], wrapped_update)

            if hasattr(chat, HOOKS["on_stream_end_final"]):
                original_methods[HOOKS["on_stream_end_final"]] = getattr(chat, HOOKS["on_stream_end_final"])
                def wrapped_end():
                    full = getattr(chat, "partial_response", "")
                    logger.on_assistant_complete(full or "")
                    next_step(chat)
                    return original_methods[HOOKS["on_stream_end_final"]]()
                setattr(chat, HOOKS["on_stream_end_final"], wrapped_end)

        def next_step(chat):
            step_index["value"] += 1
            if step_index["value"] >= len(scenario_steps):
                logger.log_system("Scénario terminé -> arrêt")
                Clock.schedule_once(lambda dt: App.get_running_app().stop(), 0.5)
                return

            step = scenario_steps[step_index["value"]]
            action = step.get("action")

            if action == "send_user":
                txt = step.get("text", "")
                # 📌 Nouveau : log explicite comme message utilisateur
                logger.log_event("user", txt, {"source": "scenario_step"})
                logger.log_system(f"Envoi question : {txt}")
                if hasattr(chat, "input"):
                    chat.input.text = txt
                Clock.schedule_once(lambda dt: getattr(chat, HOOKS["send_message"])(chat.send_button), SEND_DELAY_MS/1000)

            elif action == "wait":
                ms = int(step.get("ms", 500))
                logger.log_system(f"Attente {ms}ms")
                Clock.schedule_once(lambda dt: next_step(chat), ms/1000)

            elif action == "expect_reply":
                pattern = step.get("regex", "")
                timeout = int(step.get("timeout_ms", DEFAULT_EXPECT_TIMEOUT_MS))
                logger.log_system(f"Attente réponse correspondant à {pattern}")

                start_ts = datetime.now()
                def _check(dt):
                    acc = logger._assistant_accumulator
                    ok = re.search(pattern, acc or "", flags=re.S | re.I)
                    elapsed = (datetime.now() - start_ts).total_seconds() * 1000
                    if ok:
                        logger.log_system("expect_reply OK", {"regex": pattern, "elapsed_ms": elapsed})
                        next_step(chat)
                    elif elapsed < timeout:
                        Clock.schedule_once(_check, 0.25)
                    else:
                        logger.log_system("expect_reply TIMEOUT", {"regex": pattern, "elapsed_ms": elapsed})
                        next_step(chat)
                Clock.schedule_once(_check, 0.1)

            elif action == "stop":
                logger.log_system("Arrêt demandé par scénario")
                Clock.schedule_once(lambda dt: App.get_running_app().stop(), 0.5)

        original_on_start = getattr(AppClass, "on_start", None)
        def wrapped_on_start(self):
            chat = getattr(self, "root", None)
            if chat is None:
                raise RuntimeError("App.root non initialisé")
            install_hooks(chat)
            logger.log_system("Hooks installés")
            step_index["value"] = -1
            next_step(chat)
            if callable(original_on_start):
                return original_on_start(self)

        setattr(AppClass, "on_start", wrapped_on_start)

        logger.log_system("Lancement app Kivy")
        AppClass().run()
        logger.log_system("Application terminée")

    except Exception as e:
        logger.log_system("ERREUR FATALE", {"exc": repr(e), "trace": traceback.format_exc()})
        raise
    finally:
        sys.stdout, sys.stderr = orig_out, orig_err
        logger.close()

if __name__ == "__main__":
    main()
