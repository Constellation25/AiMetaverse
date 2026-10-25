AI Metaverse — Clone Yourself Virtually
A self-contained, multi-page web platform that lets visitors clone themselves into a personalized AI agent through a selfie, a voice recording, and a birthday — then chat with a BonziBuddy-style humanoid companion that learns, schedules, jokes, and speaks in five distinct personas.
🌌 Overview
Built as a zero-build-step static site (double-click index.html to run), AI Metaverse combines:
A 19-page marketing + app hub (why-ai, enterprise, tools, labs, education, worlds, shop, metabox, news, contact, developers, avatar-create, avatar dashboard, generated agents, privacy/terms, signup/signin)
A floating humanoid companion dock with three switchable faces and five voice personas
A clone-yourself wizard that forges a downloadable standalone agent page
A Python/Eel desktop bridge for offline TTS/STT and hardware integration
A constellation canvas header with cursor-reactive particle network
Every nav, footer, and tile link resolves to a real static page — no dead anchors.
🧬 The Clone-Yourself Pipeline
avatar-create.html walks users through four gated steps:
Step
Input
Output
1 · Selfie
Photo upload or camera capture
Face detection, brightness/warmth/palette analysis
2 · Voice
Mic recording or WAV upload
Duration, RMS loudness, fundamental frequency (autocorrelation), voice character classification
3 · Birthday
Date picker
Zodiac sign, Chinese animal, life-path number, 6-trait personality vector (Courage, Wit, Empathy, Ambition, Curiosity, Calm)
4 · Forge
Name + role + voice style
Downloadable standalone agent.html + Ready Player Me GLB capture
The generated agent page is fully self-contained — its own brain, voice, personality, and model card — and can be hosted anywhere.
🤖 The Humanoid Companion
A floating dock (bottom-right) with a pulsing launcher, greeting on first open, and three switchable faces:
Face
Style
Tech
Spatial (default)
Head sculpted from flowing light-ribbons (based on Unsplash reference)
16 gradient SVG ribbons, sway animation, blinking eye-glow, lip-sync mouth bar
Real
Photoreal AI-generated portrait
CSS eyelid blinks, breathing zoom, mouth-glow synced to --mouth variable
Robot
Brushed metal with visor eyes
Articulated jaw grille, pulsing antenna, scale-Y eye blinks
Click-to-Talk
One big gradient button cycles through states:
Idle → Listening (magenta pulse + live interim captions) → Thinking (amber) → Speaking (lime, mouth animating). Gracefully degrades to typed input when SpeechRecognition is unavailable.
Five Voice Personas
Each retints the dock and adjusts pitch/rate/voice selection:
ARIA — warm & human
ATLAS — deep & grounded
NOVA — bright & upbeat
ORACLE — measured & wise
PIXEL — playful robot
BonziBuddy Energy (Without the Spyware)
The companion shares one brain with the Metabox and all forged agents. It:
Greets visitors into the world of the Ai Metaverse
Learns likes ("I really like virtual fashion" → recalled later)
Keeps a schedule ("remember demo day friday" → "what's on my schedule?")
Tells jokes, reads news, delivers hugs with feeling
Idles with chatter and blinks on a randomized cycle
Falls back to the shared AIMV_BRAIN for anything outside its own intents
📂 Repository Structure
aimetaverse/
├── index.html              # Landing page + constellation header
├── why-ai.html             # 7 feature groups + accordion
├── enterprise.html         # Digital twins, training, workshops
├── tools.html              # MagicStudio, Wordtune, Acrolinx, Brandwatch, Zoom…
├── labs.html               # Craiyon + Boris Dayma story
├── education.html          # AI programming certification
├── worlds.html             # 49 virtual worlds (Tivoli, Somnium, VRChat…)
├── shop.html               # Virtual retail + Meta-Port
├── metabox.html            # Standalone chat console
├── news.html               # Blog posts grid
├── contact.html            # Greensboro address, hours badge, form
├── signup.html / signin.html
├── privacy.html / terms.html
├── developers.html         # Ready Player Me SDK map
├── avatar-create.html      # 4-step clone wizard
├── avatar.html             # Dashboard for forged agents
├── agents/
│   └── agent.html          # Template for generated standalone agents
├── assets/
│   ├── site.css            # Shared shell, subpage components, forms
│   ├── site.js             # Constellation, reveals, counters, humanoid injection
│   ├── avatar.js           # Clone engine + agent persona brain
│   ├── humanoid.css        # Companion dock + faces
│   ├── humanoid.js         # STT/TTS, personas, shared brain routing
│   └── face-real.jpg       # Photoreal companion face (71 KB)
├── py/
│   ├── main.py             # Eel bridge: user_said, listen_once, avatar_say, capabilities
│   └── requirements.txt    # eel, pyttsx3, SpeechRecognition, PyAudio
├── gen_pages.py            # Static page generator (re-runnable)
└── README.md
🚀 Quick Start
Static mode (no install)
bash
# Just open index.html in any modern browser
open index.html
Desktop mode (Python TTS/STT bridge)
bash
cd py
pip install -r requirements.txt
python main.py
# Opens a local window at http://localhost:8080 with full voice pipeline
The page auto-detects the Eel bridge and routes voice through pyttsx3 while the browser stays silent and only lip-syncs.
🧠 Architecture Highlights
Shared brain pattern: AIMV_BRAIN is defined once in index.html and reused by the Metabox, the companion dock, and every generated agent.
Path-aware asset loading: site.js detects whether the page lives in /agents/ and adjusts relative paths for the humanoid injection.
Canvas fallback: The constellation animation wraps getContext('2d') in a try/catch so the header degrades to plain glass in canvas-less contexts.
Deterministic persona math: Birthday → zodiac → life-path → trait vector uses fixed seed math so the same birthday always produces the same agent personality.
Voice analysis without decoding: Fundamental frequency is measured via autocorrelation on a Float32Array window; duration comes from <audio> metadata as a fallback.
🔮 Planned / In-Progress Features
The following are scoped for the next iteration:
Visible humanoid image stage in the hero (the companion becomes the centerpiece, not a corner dock)
Suggestive-prompt chips in the prompt box, seeded from the repo's knowledge brain
Alibaba / Qwen ad-serve slot under every prompt box
APIKonnect onboarding tab — checkbox-driven sign-in + token generation for ~250 enterprise APIs (ChatGPT, Gemini, Grok, Blackbox, Qwen, Kimi, Muse, Copilot, GitHub, Vercel, Cloudflare, Azure Cognitive Services, CrowdStrike, Google Cloud AI, IBM Watson, DeepAI, ParallelDots, Alexa Skill APIs, Salesforce Einstein, and the full list provided)
DevZone terminal — in-page shell that bridges to Linux, Termux, or any user terminal via WebSocket/SSH
Scheduled tasks & reminders — "remind me at 3pm" → companion pings with a spoken alert
Agentic + communicative actions — the companion can proactively draft, email, post, and chain tools on the user's behalf
🧪 Testing
Every page was verified headlessly with JSDOM:
Zero uncaught JS errors across index, subpages, wizard, dashboard, and generated agents
Voice analysis measured 220.02 Hz from a synthetic 220 Hz test tone
STT → chat → spoken reply pipeline verified end-to-end
Persona switching, face switching, mute toggle, and deep-link #virtual-worlds all pass
All 19+ pages resolve their internal links (no broken href or src)
📜 License & Credits
Photoreal face: AI-generated (not a real person's likeness)
Spatial face: inspired by a Unsplash light-ribbon head reference
Companion personality: BonziBuddy energy, reimplemented cleanly
Voice personas: pitch/rate mapped to OS-installed voices (character carries everywhere)
Powered by Kre8Tive Koncepts · Greensboro, NC ·
