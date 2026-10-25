# C25 FaceForge — Standalone AI Face-Swap & Video Reface Engine

A **standalone, white-label alternative to Reface, HeyGen and Viggle**, built as our own
proprietary AI Face Swap & Video Reface engine and fully integrated into the
Constellation25 / Ai Metaverse ecosystem.

Industry-standard open-source stack: **InsightFace + ONNX Runtime** — the same technology
behind Roop and ReActor.

🏗️ **THE TECH STACK**
- **Frontend:** HTML5, Tailwind CSS, Vanilla JS (drag & drop UI) — embedded in this site at
  `faceforge.html` / `faceforge/` and opened by the *"Create Videos & Face Swaps with Re-Face AI"* tile.
- **Backend:** Python FastAPI (lightweight, fast) — `faceforge/app.py` in this repo.
- **AI engine:** `insightface` + `onnxruntime` + `opencv-python` (local processing).
- **Note:** If Termux struggles with ONNX compilation, this same backend code can be deployed
  to a $0.20/hour RunPod GPU or connected to the Replicate API with a one-line change.

---

## 💻 STEP 1 — PROJECT SETUP

Run `faceforge/setup-termux.sh` in Termux (or any Linux shell) to create the structure and
install dependencies:

```bash
bash faceforge/setup-termux.sh
```

What it does:

```bash
#!/data/data/com.termux/files/usr/bin/bash
echo "🚀 Initializing C25 FaceForge..."

FACEFORGE_ROOT="$HOME/constellation25/faceforge"
mkdir -p "$FACEFORGE_ROOT"/{uploads,outputs,models}
cd "$FACEFORGE_ROOT"

# Create a virtual environment (recommended for Termux)
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install fastapi uvicorn python-multipart opencv-python numpy pillow

# Install InsightFace and ONNX Runtime
# (Note: If onnxruntime fails on Termux, use 'onnxruntime-qnn' or deploy to a cloud GPU)
pip install insightface onnxruntime

echo "✅ Dependencies installed. Downloading AI model..."

# Download the pre-trained InsightFace swap model (inswapper_128.onnx)
wget -O models/inswapper_128.onnx \
  "https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx"

echo "✅ C25 FaceForge Setup Complete!"
```

## 🧠 STEP 2 — THE AI FACE SWAP ENGINE (BACKEND)

`faceforge/app.py` (in this repo) handles uploads and runs the swap:

- `POST /api/swap` — multipart `source_file` + `target_file` → InsightFace `buffalo_l`
  detection + `inswapper_128` swap → `{"success": true, "output_url": "/outputs/…"}`.
- `GET /outputs/{filename}` — serves the rendered image.
- CORS is wide open (`allow_origins=["*"]`) so the GitHub Pages front-end can call a local
  or LAN backend directly from the browser.
- Uploads are deleted after processing; only outputs persist.

Image-to-image is the MVP path; video reface = frame extraction + per-frame swap +
ffmpeg re-mux (same primitives, looped).

## 🎨 STEP 3 — THE FRONTEND INTERFACE

The sleek standalone web app is `store/faceforge.html` in this repo, embedded site-wide as
the `faceforge.html` subpage (self-contained: inlined Tailwind runtime, scoped CSS).
The embedded copy auto-detects its backend:

```js
const API_URL = (location.port === '8000') ? '' : 'http://localhost:8000';
```

so it talks to same-origin when served by the backend itself, and to your local/LAN
FaceForge server when browsed from GitHub Pages or anywhere else. Without a backend the
UI still previews uploads and reports "❌ Network error. Is the Python backend running?"
honestly instead of faking a swap.

## 🚀 STEP 4 — LAUNCH YOUR STANDALONE APP

Open two Termux sessions (or use tmux).

**Session 1 (backend):**
```bash
cd ~/constellation25/faceforge
source venv/bin/activate
python3 app.py
```

**Session 2 (frontend):**
```bash
cd ~/constellation25/faceforge
python3 -m http.server 8080
```

Open your phone's browser at `http://localhost:8080` — or serve the whole Ai Metaverse
site from the repo root and use the *Create Videos & Face Swaps* tile; it calls the same
`:8000` API.

---

## Ecosystem wiring

- Site tile **"Create Videos & Face Swaps with Re-Face AI"** → `faceforge/index.html`.
- Companion brain answers face-swap questions and points here.
- `py/server.py` (site backend) and `faceforge/app.py` (swap engine) can run side by side
  on ports 8000/8001 — point `API_URL` at whichever hosts `/api/swap`.
- Consent & ethics: swap only faces you have permission to use; generated media should be
  watermarked or disclosed per your platform policy.
