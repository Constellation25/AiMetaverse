# Prompter — Avatar Prompt Selector (Guided Prompt Library)

Embedded module: **`prompter.html`** (and `prompter/index.html`) — opened by the
**"Select Avatar Prompts with Prompter"** tile on the home page (Explore the Ai Metaverse
grid) and the **`Prompter — Prompt Library`** tag in the all-rooms / site-map strip.

Source document preserved verbatim in `store/prompter.html`. The embed scopes its CSS under
`.pr-embed`, keeps the module's own toolbar (search + View Repo) as an app chrome bar, and
inlines the Tailwind runtime with the module's `brand` color palette
(`corePlugins:{preflight:false}`, Inter + JetBrains Mono, Font Awesome). The full-screen
`h-screen` app layout is re-hosted inside a height-bounded `.pr-embed` panel so it sits
cleanly within the Ai Metaverse shell; on narrow screens the avatar sidebar collapses and
the library takes the full width.

## Key Features of this Implementation

- **Avatar Selection Sidebar:** Quickly filter the library by specific AI tools (Cursor,
  Devin, Replit, Windsurf, Anthropic/Claude, Manus, Trae, and Open Source — Qwen/Kilo),
  categorized exactly as in the `x1xhlol/system-prompts` repo.
- **Deterministic Suggestion Engine:** The left panel updates based on the selected avatar.
  Selecting "Windsurf" deterministically suggests "Tools Wave 11" because that is the most
  critical prompt for that tool's workflow; "All" surfaces the most universally applicable
  prompts. Clicking a suggestion fills the search and filters the grid.
- **Guided Scrolling Library:** A clean, responsive grid of prompt cards with tags,
  descriptions, and source file names, plus a real-time search bar that filters by title,
  tag (e.g. `#Agent`, `#CLI`), or description.
- **Template & Fork Actions:**
  - **Copy** — instantly copies the raw prompt text to the clipboard.
  - **Fork** — saves the prompt into a local "workspace" library persisted in
    `localStorage` (`aimv_prompt_forks`, de-duplicated by title) and confirms with a toast
    showing how many prompts you've forked. *(Upstream the fork buttons only fired a
    placeholder toast — "(In real timer)" / "(In real timr)"; those typos are fixed and the
    action now actually persists.)*
- **Immersive Modal Viewer:** Clicking any card opens a dark-mode modal with monospace,
  syntax-friendly formatting (JetBrains Mono) to review the full system prompt before
  committing to it. Cancel / copy / fork live in the modal footer; the modal also closes on
  backdrop click.
- **View Repo** is wired to the real source: `https://github.com/x1xhlol/system-prompts`.

This gives a professional, "IDE-like" interface to browse, select, and deploy the best
system prompts from the open-source community — and a natural on-ramp to
[clone yourself virtually](avatar-create.html): fork a system prompt, then forge a
companion that runs on it.

## Verified

- `tools/tpr.js` (jsdom) — **39/39 checks**: initial render (9 avatars / 8 prompts),
  avatar filtering via a real inline-`onclick` click, live search + empty state, suggestion
  click-to-filter, modal open/close, clipboard copy, and fork → `localStorage` persistence
  with de-duplication.
- `tools/audit.py` — **367 links, 0 broken**, all 36 subpages linked from the home page.

## Related pages

- `avatar-create/index.html` — the 4-step clone/agent forge (attach a forked prompt to your agent)
- `ai-education-hub/index.html` — AI Education & Prompt Hub (quizzes, 1000+ prompt library, certifications)
- `agents/agent/index.html` — your live forged agent persona
