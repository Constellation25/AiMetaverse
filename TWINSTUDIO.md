# Virtual Twin Studio — Create Myself as an AI Agent

Embedded module: **`twin-studio.html`** (and `twin-studio/index.html`) — opened by the
**"Virtual Twin Studio"** tile on the home page (Explore the Ai Metaverse grid, now
twenty-three doors), the **`Virtual Twin Studio`** tag in the all-rooms / site-map strip,
and the **Create** column of the site footer.

Source document preserved verbatim in `store/vtwin.html`. The embed scopes its CSS under
`.vt-embed`, strips the module's own header/footer chrome (the Ai Metaverse shell provides
it), and inlines the Tailwind runtime with the module's `c25` palette, Inter / Space
Grotesk fonts and its custom `scan`, `pulse-glow` and `float` animations
(`corePlugins:{preflight:false}`, Font Awesome via CDN).

## Key Features of this Implementation

- **"Create Myself as an AI Agent" box:** the glowing, pulse-animated call-to-action card
  that defines the studio's purpose and launches the synthesis.
- **Spatial Image Sync:** a drop-zone-style uploader that previews the image client-side
  (FileReader → data URI) and uses it as the render-stage backdrop.
- **Voice Snippet Upload:** a dedicated audio uploader that queues the file for
  "biometric cloning" and confirms with a toast.
- **Persona Matrix:** a traits textarea that is woven verbatim into the twin's first
  greeting once the render completes.
- **Cinematic render sequence:** idle stage → scan-line animation with progress bar and
  status steps (mapping mesh → analyzing voice → compiling persona → initializing agent)
  → revealed **Agent Online** twin UI with a 40-bar simulated voice visualizer and a chat
  panel.
- **Talking twin chat (new):** the previously decorative input is wired — type and press
  Enter (or tap the mic) and your twin answers through the site-wide humanoid companion
  brain (`AIMV_HUMANOID.brain`), speaks the reply aloud, and the mic button hands off to
  the companion's speech recognition. User input is HTML-escaped.
- **100% static & private:** all processing is simulated client-side; images and voice
  snippets never leave the browser.

## Embed fixes over the upstream document

- Repaired broken markup: stray `6` after the preview `<img>`, `</div` missing its `>` on
  the creation box, footer `</p` and toast `</` (header/footer stripped anyway, toast
  closed properly).
- `.innerText` → `.textContent` (3 places) for jsdom/DOM consistency.
- Visualizer `setInterval`s are tracked (`vtVizTimers`) and cleared on **Reset** — upstream
  leaked 40 forever-intervals per render.
- Module JS wrapped in an IIFE with only the four inline-handler functions exported, so it
  can't clobber the shell.
- Toast relocated to bottom-left (`z-index:160`) — bottom-right is occupied by the humanoid
  companion dock.
- `@keyframes scan` is emitted unconditionally: Tailwind only outputs config keyframes for
  *used* `animate-*` utilities, and `scan` is referenced from scoped CSS
  (`.scanning .scan-line`), not a utility class.
- `bg-grid` backdrop moved from the stripped `<body>` onto the module's `<main>`.

## Verified

- `tools/tvt.js` (jsdom) — **51/51 checks**: structure/scoping/keyframes, upload previews
  (image data-URI + voice filename), no-image guard toast, full render timeline (50 %
  midpoint status → 100 % completion), persona-woven greeting, 40 visualizer bars,
  brain-routed chat reply + speak, mic → companion `listen`, XSS escaping, and full Reset
  state restoration, with zero unexpected JS errors.
- `tools/audit.py` — **371 links, 0 broken**, all 37 subpages linked from the home page.

## Related pages

- `avatar-create/index.html` — the real 4-step clone/agent forge (selfie → voice pitch →
  birth chart → downloadable agent); the studio callout cross-links to it, and
  avatar-create links back to the studio.
- `agents/agent/index.html` — your live forged agent persona
- `prompter/index.html` — fork a system prompt, then give your twin its behaviour
