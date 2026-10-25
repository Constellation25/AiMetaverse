#!/usr/bin/env python3
"""
server.py — optional FastAPI backend for the Ai Metaverse static site.

GitHub Pages hosts the STATIC site (every page is self-contained: inline CSS/JS,
flat foo.html + foo/index.html copies). This server is the *live* half you point
the embeds at from their Integrations panels:

    uvicorn py.server:app --host 0.0.0.0 --port 8000     (from the repo root)
    # or
    python -m py.server                                   (same thing)

Endpoints
---------
GET  /                      -> serves the static site (index.html etc.)
GET  /api/health            -> liveness + endpoint map
POST /api/dial              -> Twilio bridge for the Agentik CRM "Dial" button
                               {to, name} -> real call if TWILIO_* env set, else simulated
POST /api/v1/outbound/call  -> Commz scaffold webhook (lead -> AI call logic)
POST /api/v1/outbound/handoff -> Commz human-handoff webhook
POST /api/llm               -> LLM proxy: Ollama (OLLAMA_URL) or OpenAI (OPENAI_API_KEY)
                               keeps keys server-side; the browser never sees them
GET  /api/leads             -> shared lead store (JSON file)
POST /api/leads             -> append a lead
DELETE /api/leads/{id}      -> remove a lead

Env
---
TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_FROM  enable real calls (pip install twilio)
OLLAMA_URL (default http://localhost:11434)           local brain
OPENAI_API_KEY + OPENAI_MODEL (default gpt-4o-mini)   cloud brain
LEADS_FILE (default py-data/leads.json)               persistence path
"""
from __future__ import annotations

import json
import logging
import os
import threading
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent          # repo / site root
DATA = Path(os.environ.get("LEADS_FILE", ROOT / "py-data" / "leads.json"))
LOG = logging.getLogger("aimv.server")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Ai Metaverse backend", version="1.1.0",
              description="Static-site companion: Twilio dial bridge, Commz webhooks, LLM proxy, lead store.")

_lock = threading.Lock()


# ------------------------------------------------------------------ models
class DialReq(BaseModel):
    to: str
    name: str = "Valued Customer"
    message: str | None = None


class OutboundReq(BaseModel):
    name: str = "Valued Customer"
    phone: str | None = None
    intent: str = "general_inquiry"


class HandoffReq(BaseModel):
    reason: str | None = None
    transcript_summary: str | None = None


class LlmReq(BaseModel):
    prompt: str
    provider: str | None = None          # ollama | openai | auto
    model: str | None = None
    system: str = "You are a concise assistant for the Ai Metaverse site."


class LeadReq(BaseModel):
    name: str
    company: str = ""
    phone: str = ""
    value: int = 0
    status: str = "New"
    source: str = "api"


# ------------------------------------------------------------------ helpers
def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _twilio():
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    tok = os.environ.get("TWILIO_AUTH_TOKEN")
    frm = os.environ.get("TWILIO_FROM")
    if not (sid and tok and frm):
        return None
    try:
        from twilio.rest import Client           # optional dependency
        return Client(sid, tok), frm
    except Exception as exc:                     # pragma: no cover
        LOG.warning("twilio sdk unavailable: %s", exc)
        return None


def _place_call(req: DialReq) -> dict:
    tw = _twilio()
    say = req.message or (f"Hello, this is an automated call from the Ai Metaverse. "
                          f"{req.name}, your Ai telemarketer would like to follow up with you.")
    if tw:
        client, frm = tw
        call = client.calls.create(
            to=req.to, from_=frm,
            twiml=f'<Response><Say voice="alice">{say}</Say></Response>',
        )
        LOG.info("TWILIO CALL %s -> %s (%s)", req.name, req.to, call.sid)
        return {"status": "queued", "sid": call.sid, "provider": "twilio", "at": _now()}
    LOG.info("SIMULATED CALL %s -> %s", req.name, req.to)
    return {"status": "simulated", "provider": "none",
            "note": "Set TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN/TWILIO_FROM for real calls.",
            "to": req.to, "name": req.name, "at": _now()}


def _http_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 90) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _load_leads() -> list:
    if not DATA.exists():
        return []
    try:
        return json.loads(DATA.read_text())
    except Exception:
        return []


def _save_leads(rows: list) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(rows, indent=2))


# ------------------------------------------------------------------ api
@app.get("/api/health")
def health():
    return {
        "ok": True,
        "service": app.title,
        "version": app.version,
        "static_root": str(ROOT),
        "twilio": bool(_twilio()),
        "ollama": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "leads": len(_load_leads()),
        "endpoints": ["/api/health", "/api/dial", "/api/v1/outbound/call",
                      "/api/v1/outbound/handoff", "/api/llm", "/api/leads"],
        "at": _now(),
    }


@app.post("/api/dial")
def dial(req: DialReq):
    return _place_call(req)


@app.post("/api/v1/outbound/call")
def outbound(req: OutboundReq):
    LOG.info("COMMZ INITIATING CALL: %s at %s | intent=%s", req.name, req.phone, req.intent)
    if req.phone:
        res = _place_call(DialReq(to=req.phone, name=req.name,
                                  message=f"Hi {req.name}, this is your Ai Metaverse agent calling about {req.intent.replace('_', ' ')}."))
    else:
        res = {"status": "dialing", "provider": "none", "note": "no phone supplied; logged only"}
    return {"status": res.get("status"), "lead": req.name, "intent": req.intent,
            "call": res, "timestamp": _now()}


@app.post("/api/v1/outbound/handoff")
def handoff(req: HandoffReq):
    LOG.warning("HUMAN HANDOFF: %s | %s", req.reason, (req.transcript_summary or "")[:200])
    return {"status": "handoff_initiated", "reason": req.reason, "at": _now()}


@app.post("/api/llm")
def llm(req: LlmReq):
    provider = (req.provider or "auto").lower()
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    openai_key = os.environ.get("OPENAI_API_KEY")
    msgs = [{"role": "system", "content": req.system}, {"role": "user", "content": req.prompt}]

    if provider in ("ollama", "auto") :
        try:
            j = _http_json(ollama_url + "/api/chat",
                           {"model": req.model or os.environ.get("OLLAMA_MODEL", "llama3.1"),
                            "stream": False, "messages": msgs}, timeout=120)
            return {"provider": "ollama", "text": j["message"]["content"], "at": _now()}
        except Exception as exc:
            if provider == "ollama":
                raise HTTPException(502, f"ollama unreachable: {exc}")
            LOG.info("ollama miss (%s); trying next provider", exc)
    if provider in ("openai", "auto") and openai_key:
        try:
            j = _http_json("https://api.openai.com/v1/chat/completions",
                           {"model": req.model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                            "messages": msgs},
                           headers={"Authorization": f"Bearer {openai_key}"}, timeout=120)
            return {"provider": "openai", "text": j["choices"][0]["message"]["content"], "at": _now()}
        except Exception as exc:
            raise HTTPException(502, f"openai error: {exc}")
    raise HTTPException(503, "No LLM configured. Set OLLAMA_URL (local) or OPENAI_API_KEY (cloud), "
                          "or leave the site on its built-in offline brain.")


@app.get("/api/leads")
def leads_get():
    return {"leads": _load_leads(), "at": _now()}


@app.post("/api/leads")
def leads_post(req: LeadReq):
    with _lock:
        rows = _load_leads()
        row = req.dict()
        row["id"] = int(datetime.now(timezone.utc).timestamp() * 1000)
        row["at"] = _now()
        rows.append(row)
        _save_leads(rows)
    LOG.info("LEAD ADDED %s (%s)", req.name, req.company)
    return {"ok": True, "lead": row, "count": len(rows)}


@app.delete("/api/leads/{lead_id}")
def leads_delete(lead_id: int):
    with _lock:
        rows = _load_leads()
        before = len(rows)
        rows = [r for r in rows if r.get("id") != lead_id]
        if len(rows) == before:
            raise HTTPException(404, "lead not found")
        _save_leads(rows)
    return {"ok": True, "count": len(rows)}


# ------------------------------------------------------------------ static site (last)
@app.get("/")
def root():
    return FileResponse(ROOT / "index.html")


app.mount("/", StaticFiles(directory=ROOT, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
