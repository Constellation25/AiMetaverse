# Ai Metaverse — static site + humanoid companion + clone-yourself pipeline

A 19-page static rebuild of the archived `aimetaverse.cloud`, with a BonziBuddy-style
**humanoid companion** on every page and a four-step **"clone yourself virtually"** flow
(selfie → voice → birthday → your own AI agent). No build step, no server required.

```
aimetaverse/
├── index.html            ← landing / app page (hero, Metabox chat, explore grid, CTA)
├── why-ai.html           ← the seven pillars, expanded
├── enterprise.html       ← custom agent models, digital twins, engagement table
├── tools.html            ← Free AI Tools Directory (sponsored + in-house)
├── labs.html             ← Ai-Labs: Craiyon, generation modes, sandbox
├── education.html        ← AI + metaverse knowledge clouds, certification
├── worlds.html           ← 49 named virtual worlds + Cardboard
├── shop.html             ← Virtual Shopping Kre8tor, stores, BitBucks
├── metabox.html          ← standalone Metabox chat page
├── news.html             ← release-notes blog
├── contact.html          ← address/phone/hours with live open-closed badge + form
├── signup.html / signin.html
├── privacy.html / terms.html
├── developers.html       ← agent spec schema, Eel bridge, Ready Player Me SDK map
├── avatar-create.html    ← THE FORGE: selfie → voice → birthday → agent (+RPM)
├── avatar.html           ← dashboard of your stored clone + agent chat + wipe
├── agents/agent.html     ← in-browser home of your forged agent
├── assets/
│   ├── site.css / site.js        ← shared shell: constellation header, nav, footer,
│   │                                cookie banner, scroll progress, reveals
│   ├── humanoid.css / humanoid.js← the companion (faces, personas, talk, brain)
│   ├── avatar.js                 ← clone pipeline engine + agent page generator
│   └── face-real.jpg             ← photoreal companion face (900px, 71 KB)
├── py/main.py + requirements.txt ← optional Python/Eel backend (desktop TTS/STT/LLM)
└── gen_pages.py                  ← regenerates the 17 content subpages
```

Open `index.html` directly, or serve the folder (`python -m http.server`) — everything
works either way. The only network requests are Google Fonts and links you click.

---

## 1 · The humanoid companion (every page)

A floating launcher in the bottom-right corner opens the **companion dock**.

**Three faces** (persisted in `localStorage`):
| Face | What it is |
|---|---|
| **Spatial** (default) | A head sculpted from flowing light-ribbons — the site's reinterpretation of the layered-strand reference art. SVG, animated sway, eye-glow blinks, mouth light-bar lip-sync |
| **Real** | A photoreal photographed face (`assets/face-real.jpg`) with CSS eyelid blinks, breathing zoom, sheen sweep and a mouth glow driven by the same `--mouth` variable |
| **Robot** | Brushed-metal head with gradient visor eyes, articulated jaw grille and pulsing antenna |

**Five voice personas** (Web Speech TTS; pitch/rate + preferred-voice matching + accent colour):
`ARIA` warm & human · `ATLAS` deep & grounded · `NOVA` bright & upbeat · `ORACLE` measured & wise · `PIXEL` playful robot.
No `speechSynthesis`? The dock flips to captions + simulated mouth movement.

**CLICK TO TALK** — the big button under the face runs `SpeechRecognition` with live
interim captions, then thinks and answers out loud. States: idle → listening (magenta
pulse) → thinking (amber) → speaking (lime, mouth animates; tap to stop).

**Companion kit (the BonziBuddy energy, minus the spyware):**
- greets you by name of the metaverse when first opened, remembers you across sessions
- **learns what you like** (“I love virtual fashion”) and brings it up later
- **keeps a schedule** (“remember demo day on friday” → “what's on my schedule?”)
- tells **jokes**, **trivia**, late-breaking **news**, and delivers **hugs** with feeling
- six clickable capability cards, idle chatter while open, blinks and floats constantly
- shares one brain with the Metabox (`window.AIMV_BRAIN`) and routes to `py/main.py`
  automatically when the Eel bridge is present (`window.eel.user_said`, `avatar_say`)

Everything the companion stores lives under `localStorage` keys `aimv_*`; nothing uploads.

## 2 · Clone yourself virtually (`avatar-create.html`)

1. **Selfie / image** — live camera (`getUserMedia`, mirrored capture) or drag-drop upload.
   Downscaled to ≤560 px, analysed on-device (brightness, warmth, dominant hue, skin-tone
   coverage, optional `FaceDetector`), and the palette retints the UI.
2. **Voice snippet** — `MediaRecorder` with live waveform, 20 s cap; or upload audio.
   Decoded with Web Audio: fundamental pitch via autocorrelation, RMS loudness, pace →
   a *voice character* (“High & energetic”). The audio blob is **never persisted**.
3. **Birthday** — zodiac sign/element/ruler, Chinese zodiac, life-path number (masters
   11/22 kept), birth weekday, age in days, countdown — blended into a deterministic
   six-trait personality vector with animated bars.
4. **Forge the agent** — name, role, voice style, temperature → staged build log
   (build→train→validate→test→deploy) → live agent + **downloadable standalone agent
   page** (works offline, has its own persona chat + mic) + **JSON model card**.

**Ready Player Me**: launch the creator in a modal iframe (`frameApi`), the
`v1.avatar.exported` message is captured into the profile; or paste a `.glb` URL.
`developers.html` maps every RPM repo (visage, Unity/Unreal SDKs, iframe example…) to
where it plugs in, with copy-paste render code.

`avatar.html` shows the stored clone (portrait, voice profile, trait bars, agents) and
chats with your agent; “Delete everything” wipes all `aimv_*` keys.

## 3 · Python backend (optional)

```bash
pip install -r py/requirements.txt
python py/main.py                    # Chrome/Edge app window, :8080
AIMV_LLM=ollama python py/main.py    # local Llama brain instead of the local KB
```
`eel.expose`: `user_said()` (brain + pyttsx3 voice + `eel.avatar_say` lip-sync),
`listen_once()` (desktop mic), `speak_only()`, `capabilities()`. Degrades cleanly when
espeak/mic/LLM are missing — the browser simply keeps owning that layer.


## 5 · The humanoid image, suggestive prompts & ads

- **The face is the hero — inside an orb.** The stage is a circular glass orb: your generated
  orb art (`assets/face-orb.jpg`) as the base texture on a live `<canvas class="orb-canvas">`
  (drifting constellation + pulse), a spinning prismatic rim, glass highlight and two dashed
  orbit rings. The **spatial light-ribbon head floats inside it** by default; a three-button
  switcher under the hero orb flips to the photoreal portrait (`assets/face-real.jpg`) or the
  robot head, in sync with the dock. The launcher and dock avatar dot are pocket-orbs of the
  same art.
- **The face is the hero.** `index.html` mounts the companion stage directly in the hero:
  the photoreal portrait (`assets/face-real.jpg`, default face) inside an orbital ring, with
  its own **CLICK TO TALK** button, joke/trivia/hug buttons, suggestion chips and ad slot.
  The floating dock on every page carries the same stage in miniature.
- **Suggestive prompting** — every prompt surface (dock, hero stage, Metabox console,
  metabox.html) renders ✨ chips drawn from the repo brain; after each reply the chips
  regenerate into contextual follow-ups ("Make it cyberpunk", "List my reminders"…).
- **Ad-serve box** — under every prompt box sits a sponsored slot labelled
  "Sponsored · served by Alibaba & Qwen", rotating six creatives (Model Studio, Qwen-Max,
  Qwen-VL, PAI-EAS, Qwen-Agent, Tongyi Tingwu) every 9 s with real outbound links and a
  manual refresh. Swap `ADS` in `assets/humanoid.js` for a live network tag when you have one.

## 6 · APIKonnect (onboarding tab) & DevZone

- `apikonnect.html` — onboarding checklist that ticks itself from local storage;
  10 enterprise LLM cards (ChatGPT, Gemini, Grok, Blackbox, **Qwen**, Kimi, Muse,
  Copilot, Vercel, Cloudflare); **299 de-duplicated AI APIs** from the directory with
  search + category filters; every tick becomes a **connector**: *Sign & generate token*
  (`ak_live_…`), copy, **upload** (metadata only), **download** (connector JSON bundle),
  **share**, revoke. Tokens persist under `aimv_apik`.
- `devzone.html` — in-page terminal (`help ls cd cat connect bridge status apis reminders
  tasks forge open echo whoami date clear`, history with ↑/↓), `cat spec` prints your live
  agent model card, `connect termux` copies the phone pairing one-liner, `connect ssh
  user@host` registers a bridge host, and `bridge` reports whether the Eel backend is live.

## 7 · Agentic & communicative companion

Natural language, anywhere on the site:
`remind me to ship in 10 minutes` / `at 5pm` / `on friday` → spoken ⏰ toast fires on any
open page when due · `add task …`, `list tasks`, `complete task …` · `deliver a message to
Ada: …` → logged delivery in the current persona voice (`delivered messages` to audit) ·
agentik row in the dock: **Plan my day** (reminders + tasks + birth-chart energy),
**Art prompt** (persona-driven Craiyon prompt, copied to clipboard), **Remind**, **APIKonnect**.


## 9 · FastAPI companion backend (`py/server.py`)

GitHub Pages serves the **static** half (every subpage self-contained, flat + folder
`index.html`). `py/server.py` is the optional **live** half — one process, no build:

```bash
pip install -r py/requirements.txt
uvicorn py.server:app --port 8000        # serves the site AND the APIs below
```

| Endpoint | Purpose |
|---|---|
| `GET /` + static mount | serves the whole site locally (same files Pages hosts) |
| `POST /api/dial` | Twilio bridge for the CRM "Dial" button — real call when `TWILIO_ACCOUNT_SID/AUTH_TOKEN/FROM` are set, simulated otherwise |
| `POST /api/v1/outbound/call` · `/handoff` | Commz webhooks from the FastAPI scaffold block |
| `POST /api/llm` | LLM proxy: Ollama (`OLLAMA_URL`) or OpenAI (`OPENAI_API_KEY`) — keys stay server-side |
| `GET/POST/DELETE /api/leads` | shared lead store (`py-data/leads.json`) so the CRM survives devices |

Point the CRM's **Integrations → call endpoint** at `http://localhost:8000/api/dial`
(or the deployed URL) and the Dial buttons place real calls. Without the server every
embed keeps working on its offline simulations — nothing breaks.

## 8 · Verified headlessly (jsdom)

Zero uncaught JS errors across index, subpages, wizard, dashboard and generated agents.
Exercised end-to-end: constellation render, dock greet/persona/face switching, STT result
+ permission-denied paths, 220 Hz test tone measured at 220.02 Hz, birthday → Leo/Goat/
life-path-6 vector, forge → download → standalone agent chat intents (identity, persona,
voice, role, RPM, privacy, worlds, thanks), schedule + likes memory, metabox page chat,
dashboard restore, wipe. Regenerate content pages any time with `python3 gen_pages.py`.
