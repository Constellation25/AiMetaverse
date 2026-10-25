#!/usr/bin/env python3
"""
main.py — Python backend for the Ai Metaverse humanoid UI (VERSED'ai).

Architecture
------------
    index.html  (GUI: constellation header + SVG humanoid avatar)
        ^  |
        |  |  eel.expose() / eel.js RPC
        v  |
    main.py     (STT  ->  brain  ->  TTS)

The web page auto-detects this backend: when ``window.eel.user_said`` exists the
avatar routes every message here instead of answering in the browser, and the
tray status flips to "Online · Python/Eel bridge".

Run
---
    pip install -r requirements.txt
    python main.py                 # opens a Chrome/Edge app window
    python main.py --browser       # opens in your default browser tab
    python main.py --port 8080     # serve only, no window (open http://localhost:8080)

Voice hardware is optional:
  * no microphone  -> STT is skipped, the browser mic button still works via Web Speech
  * no audio out   -> pyttsx3 silently no-ops, replies are still returned to the avatar
"""

from __future__ import annotations

import argparse
import os
import queue
import re
import shutil
import sys
import threading
from datetime import datetime

import eel

# ---------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.dirname(HERE)          # .../aimetaverse  (contains index.html)
INDEX = "index.html"

# ---------------------------------------------------------------- config
LLM_BACKEND = os.environ.get("AIMV_LLM", "local").lower()   # local | openai | ollama
OPENAI_MODEL = os.environ.get("AIMV_OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.environ.get("AIMV_OLLAMA_MODEL", "llama3.1")
OLLAMA_URL = os.environ.get("AIMV_OLLAMA_URL", "http://localhost:11434")
TTS_ENABLED = os.environ.get("AIMV_TTS", "1") != "0"
TTS_RATE = int(os.environ.get("AIMV_TTS_RATE", "182"))
TTS_VOICE_HINT = os.environ.get("AIMV_TTS_VOICE", "female")
STT_LANG = os.environ.get("AIMV_STT_LANG", "en-US")

SYSTEM_PROMPT = (
    "You are VERSED'ai, the humanoid concierge of the Ai Metaverse — an AI-powered "
    "metaverse hub in Greensboro, North Carolina. You help visitors clone a virtual "
    "avatar from a selfie, a voice snippet and a birthday; generate royalty-free art "
    "with Craiyon; explore 100s of metaverse environments; use the free AI tools "
    "directory; learn AI programming with certification; and deploy custom enterprise "
    "agent models. Answer in two or three short spoken sentences, warm and concrete. "
    "Never invent prices or availability."
)

# ---------------------------------------------------------------- optional deps
def _have(module: str) -> bool:
    try:
        __import__(module)
        return True
    except Exception:
        return False


HAS_TTS = TTS_ENABLED and _have("pyttsx3")
HAS_STT = _have("speech_recognition")
HAS_MIC = bool(shutil.which("arecord") or shutil.which("sox") or shutil.which("ffmpeg")
               or sys.platform in ("win32", "darwin"))

# ---------------------------------------------------------------- TTS engine
_tts_engine = None
_tts_tried = False
_tts_lock = threading.Lock()
_tts_queue: "queue.Queue[str]" = queue.Queue()


def _init_tts():
    """Initialise pyttsx3 once, on a worker thread (it owns its own event loop)."""
    global _tts_engine, _tts_tried
    if not HAS_TTS:
        return None
    with _tts_lock:
        if _tts_engine is not None or _tts_tried:
            return _tts_engine                      # never retry a missing audio backend
        _tts_tried = True
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", TTS_RATE)
            engine.setProperty("volume", 1.0)
            voices = engine.getProperty("voices") or []
            pick = None
            if TTS_VOICE_HINT == "female":
                pick = next((v for v in voices if re.search(r"zira|samantha|female|aria|susan|hazel", v.name, re.I)), None)
            _tts_engine = engine
            if pick:
                try:
                    engine.setProperty("voice", pick.id)
                except Exception:
                    pass
            threading(target=_tts_worker, daemon=True).start()
        except Exception as exc:                      # no audio device, missing lib, etc.
            print(f"[tts] disabled: {exc}")
            _tts_engine = None
    return _tts_engine


def _tts_worker() -> None:
    """Serialise speech so overlapping replies never garble each other."""
    engine = _tts_engine
    while True:
        text = _tts_queue.get()
        if text is None:
            break
        try:
            engine.stop()
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            print(f"[tts] {exc}")
        finally:
            _tts_queue.task_done()


def say(text: str) -> None:
    """Queue text for spoken output (non-blocking)."""
    if not HAS_TTS:
        return
    _init_tts()
    if _tts_engine is None:
        return
    clean = re.sub(r"<[^>]+>", " ", str(text))
    clean = re.sub(r"\s+", " ", clean).strip()
    if clean:
        _tts_queue.put(clean)


# ---------------------------------------------------------------- STT engine
def _stt_listen(timeout: float = 6.0, phrase_limit: float = 12.0) -> str:
    """Capture one utterance from the default microphone."""
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    with sr.Microphone(sample_rate=16000) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.35)
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
    try:
        return recognizer.recognize_google(audio, language=STT_LANG)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        raise RuntimeError(f"speech service unavailable: {exc}") from exc


# ---------------------------------------------------------------- brain
LOCAL_KB = [
    (("avatar", "clone", "selfie", "birth chart", "horoscope"),
     "To clone yourself virtually: upload a selfie, attach a ten second voice snippet, "
     "and enter your birthday so I can mimic your horoscope traits. Your avatar is then "
     "ready for any of our one hundred plus environments."),
    (("craiyon", "art", "image", "draw", "royalty"),
     "Craiyon turns any text prompt into royalty free images. It was built in house by our "
     "CEO and lead researcher Boris Dayma, and it lives inside Ai-Labs with free cloud storage."),
    (("world", "environment", "explore", "vrchat", "somnium", "planet", "mars"),
     "I can stream any world to your Meta-Port — Tivoli Cloud, Somnium Space, VRChat, Mona, "
     "Spatial and hundreds more, including a virtual trip to Mars."),
    (("free", "tool", "tools", "directory", "price", "cost"),
     "The free AI tools directory covers writing, image, video, music and social tools, and "
     "members get free storage cloud services. Upgraded accounts unlock our most advanced models."),
    (("enterprise", "business", "agent", "digital twin", "crm", "telemarketer", "biometric"),
     "For enterprise we deploy purpose driven custom agent models, digital twins of offices and "
     "storefronts, a free AI CRM, AI telemarketers, and biometric payments with MyBUY'o."),
    (("learn", "education", "certif", "course", "programming", "code", "python"),
     "Ai Education teaches AI programming and development with a certification on completion — "
     "neural networks, deep learning, computer vision, NLP, robotics and autonomous systems."),
    (("video", "youtube", "face swap", "reface", "social"),
     "You can create YouTube and social videos with AI, including Re-Face AI face swaps — "
     "script, render, caption and publish from one workspace."),
    (("shop", "store", "fashion", "decor", "bitbuck", "reward", "buy"),
     "Millions of virtual fashion, home decor and clothing items are in world. Set up a virtual "
     "retail store, take biometric payments, and earn BitBucks round up rewards."),
    (("music", "song", "lyric", "record", "concert"),
     "Ai Records writes and produces original lyrics and tracks, and you can host a virtual "
     "concert in your own environment for the community."),
    (("hello", "hi ", "hey", "who are you", "your name"),
     "Hello, I am VERSED'ai, your humanoid guide to the Ai Metaverse. I can clone your avatar, "
     "generate royalty free art, or open any virtual world for you."),
    (("hour", "open", "address", "where", "contact", "phone"),
     "We are at 1007 Yanceyville Street in Greensboro, North Carolina, open weekdays nine to five, "
     "and you can reach us on 336 805 0229."),
]

FALLBACK = ("I can help with avatars, free AI art, virtual worlds, AI education, or enterprise "
            "agent models. Which one should we start with?")


def _local_brain(text: str) -> str:
    low = f" {text.lower()} "
    best, best_hits = FALLBACK, 0
    for keys, reply in LOCAL_KB:
        hits = sum(1 for k in keys if k in low)
        if hits > best_hits:
            best, best_hits = reply, hits
    return best


def _openai_brain(text: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": text}],
        max_tokens=180,
        temperature=0.7,
    )
    return (resp.choices[0].message.content or "").strip()


def _ollama_brain(text: str) -> str:
    try:
        import requests
    except ImportError:
        import urllib.request, json
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/chat",
            data=json.dumps({
                "model": OLLAMA_MODEL,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                             {"role": "user", "content": text}],
                "stream": False,
            }).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())["message"]["content"].strip()
    resp = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": OLLAMA_MODEL,
              "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                           {"role": "user", "content": text}],
              "stream": False},
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()


def think(text: str) -> str:
    """Route the utterance to the configured brain, degrading gracefully."""
    if LLM_BACKEND == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            return _local_brain(text)
        try:
            return _openai_brain(text)
        except Exception as exc:
            print(f"[brain] openai failed ({exc}); using local knowledge base")
            return _local_brain(text)
    if LLM_BACKEND == "ollama":
        try:
            return _ollama_brain(text)
        except Exception as exc:
            print(f"[brain] ollama failed ({exc}); using local knowledge base")
            return _local_brain(text)
    return _local_brain(text)


# ---------------------------------------------------------------- eel RPC
eel.init(WEB_DIR)


@eel.expose
def user_said(text: str) -> str:
    """Called by the avatar whenever the visitor speaks or types. Returns the reply."""
    text = re.sub(r"<[^>]+>", " ", str(text or "")).strip()
    if not text:
        return "I did not catch that — could you say it again?"
    print(f"[{datetime.now():%H:%M:%S}] user : {text}")
    reply = think(text)
    print(f"[{datetime.now():%H:%M:%S}] ai   : {reply}")
    say(reply)                       # spoken through the desktop speakers
    eel.avatar_say(reply)            # and lip-synced by the browser avatar
    return reply


@eel.expose
def listen_once() -> str:
    """Capture one utterance with Python STT (useful when the browser mic is blocked)."""
    if not HAS_STT:
        return ""
    if not HAS_MIC:
        return ""
    try:
        return _stt_listen()
    except Exception as exc:
        print(f"[stt] {exc}")
        return ""


@eel.expose
def speak_only(text: str) -> None:
    """Speak arbitrary text through pyttsx3 without a reply round-trip."""
    say(text)


@eel.expose
def capabilities() -> dict:
    """Report what this backend can do, so the UI can label its buttons honestly."""
    _init_tts()                      # lazy: only touches the audio device when asked
    return {
        "tts": bool(HAS_TTS and _tts_engine is not None),
        "stt": bool(HAS_STT and HAS_MIC),
        "brain": LLM_BACKEND if (LLM_BACKEND != "openai" or os.environ.get("OPENAI_API_KEY")) else "local",
        "voice_hint": TTS_VOICE_HINT,
        "started": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------- entry point
def main() -> None:
    ap = argparse.ArgumentParser(description="Ai Metaverse humanoid UI backend")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--browser", action="store_true", help="open in the default browser tab")
    ap.add_argument("--no-window", action="store_true", help="serve only, do not open anything")
    ap.add_argument("--chrome", default=None, help="path to Chrome/Edge executable")
    args = ap.parse_args()

    if not os.path.isfile(os.path.join(WEB_DIR, INDEX)):
        sys.exit(f"[fatal] {INDEX} not found in {WEB_DIR}")

    _init_tts()
    print("=" * 66)
    print(" Ai Metaverse — humanoid UI backend")
    print("=" * 66)
    print(f"  web root : {WEB_DIR}")
    print(f"  brain    : {LLM_BACKEND}")
    print(f"  TTS      : {'pyttsx3 ready' if HAS_TTS else 'unavailable (browser TTS will be used)'}")
    print(f"  STT      : {'SpeechRecognition ready' if (HAS_STT and HAS_MIC) else 'unavailable (browser mic will be used)'}")
    print(f"  url      : http://{args.host}:{args.port}")
    print("=" * 66)

    start_opts = {
        "size": (1280, 860),
        "port": args.port,
        "host": args.host,
        "close_callback": lambda *_: sys.exit(0),
    }
    if args.chrome:
        start_opts["chrome_app_args"] = {"path": args.chrome}

    if args.no_window:
        mode = None
    elif args.browser:
        mode = "default"
    else:
        mode = "chrome"

    try:
        eel.start(INDEX, mode=mode, block=True, **start_opts)
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as exc:
        # Chrome/Edge missing -> fall back to whatever browser is available
        print(f"[eel] app window failed ({exc}); retrying in default browser")
        eel.start(INDEX, mode=None, block=True, port=args.port, host=args.host)


if __name__ == "__main__":
    main()
