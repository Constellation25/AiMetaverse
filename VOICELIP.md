# Voice & Lip-Sync Studio — Upload Your Voice to Attach to Avatar

Embedded module: **`voice-lipsync.html`** (and `voice-lipsync/index.html`) — opened by the
**"Upload Your Voice to Attach to Avatar / Voice cloning & lip-sync"** tile on the home
page (the first door of the Explore grid), the **`Voice & Lip-Sync Studio`** tag in the
all-rooms / site-map strip, and the **Create** column of the site footer. It is also
cross-linked from `avatar-create.html` and from the Virtual Twin Studio callout chain.

Source document preserved verbatim in `store/voicelip.html`. The embed scopes its CSS
under `.vl-embed`, strips the module's own header/footer chrome (the Ai Metaverse shell
provides it), keeps the `bg-grid` backdrop on the module's `<main>`, and inlines the
Tailwind runtime with the module's `c25` palette, Inter / Space Grotesk fonts and its
custom `scan`, `pulse-glow` (purple) and `wave` animations
(`corePlugins:{preflight:false}`, Font Awesome via CDN).

## Key Features of this Build

- **Dual Avatar Support:** a toggle lets the user choose between uploading a **Still
  Photo** or a **Video Template** — the file input's `accept` switches between
  `image/*` and `video/*`, and the active button is highlighted.
- **Voice Cloning Upload:** a dedicated audio file uploader that queues the file for
  biometric voice cloning (mimicking ElevenLabs), showing the file name and a toast.
- **Script Input:** a textarea with a live character counter for the avatar to speak,
  noting multi-lingual auto-translation support.
- **Cinematic Render Simulation:**
  - a high-tech **scanning** animation sweeps over the avatar;
  - a detailed progress bar with changing status messages (*Cloning Voice Biometrics →
    Mapping Facial Landmarks (68 points) → Generating Audio Track → Rendering Lip-Sync
    Video (phoneme alignment) → Finalizing Output*).
- **Simulated Talking Preview:** once complete, the right panel shows the avatar with a
  dynamic 40-bar audio visualizer and a CSS-animated "mouth" overlay that opens and
  closes to simulate realistic lip-syncing to the generated script (98.4% accuracy
  badge, quoted script display).
- **100% Static & Private:** all processing is simulated client-side in the browser. No
  audio or images are ever sent to a server.

## Embed fixes over the upstream document

- **Dead "Export MP4" button wired:** it now downloads the rendered avatar media as
  `c25-lipsync-render.<ext>` (data-URI anchor, extension sniffed from the upload) and
  confirms with a toast — nothing leaves the browser.
- **Declared-but-unused `isRendering` flag wired** as a re-entrancy guard: double-clicking
  *Generate* mid-render no longer stacks overlapping render chains; it is released on
  completion and on *New*.
- **Timer leak fixed:** the render `setTimeout` chain and the 150 ms talking
  `setInterval` are tracked in `vlTimers` and all cleared by `resetStudio()` — after
  *New*, a half-finished render can no longer resurrect the stage or keep the mouth
  twitching.
- `.innerText` → `.textContent` (6 places) for jsdom/DOM consistency.
- The script textarea got `maxlength="500"` so it honors its own `0 / 500 chars` counter.
- Toast pinned bottom-left at `z-index:160` so it never covers the site-wide humanoid
  companion dock.
- Custom keyframes (`scan`, `pulse-glow`, `wave`) are declared unconditionally in the
  embed overrides so the animations survive CSS scoping (site-wide `@keyframes` fix).

## Verification

- `NODE_PATH=/tmp/node_modules node tools/tvl.js` — jsdom suite: **ALL PASS (64 checks)**
  covering structure/scoping, avatar-source toggle, upload previews, all three guard
  toasts, the render pipeline (45% landmark step → completion), visualizer + mouth
  animation, export download, full reset (incl. timer-cleared assertions) and zero JS
  errors. The suite caught an unbalanced `tailwind.config` brace during integration —
  fixed before commit.
- `python3 tools/audit.py` — **380 links, 0 broken, 38 flat pages, full index coverage.**
- `tools/tvt.js` (Virtual Twin Studio) re-run after the shared `assets/site.js` footer
  change: **ALL PASS (51 checks)**.

## Wiring checklist (all done)

- `gen_pages.py`: loader + `KNOWN` + `P['voice-lipsync.html']`; `gen_extra.py`: `KNOWN`.
- `index.html`: first Explore tile re-pointed `avatar-create/` → `voice-lipsync/` (new
  mic-and-waveform icon), site-map tag added next to Virtual Twin Studio.
- `assets/site.js`: footer **Create** column entry.
- `avatar-create.html`: callout now also links the Voice & Lip-Sync Studio (flat +
  folder copy re-synced).
