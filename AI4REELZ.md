# Ai4Reelz — Cinematic AI Video Orchestration (Constellation25)

Official Ai4Reelz portal notes: how to use it, and what ships inside the embed.

## 🚀 How to Use This

1. **Save the file:** the source document lives at `store/ai4reelz.html`; the generated,
   site-integrated page is `ai4reelz.html` (+ folder copy `ai4reelz/index.html`).
2. **Open in browser:** double-click `ai4reelz.html` (fully self-contained — inlined
   Tailwind runtime, scoped CSS, no external assets required) or visit
   `https://constillation25.github.io/AiMetaverse/ai4reelz/` once deployed.
3. **Test the workflow:** scroll to **“Initialize Your Video Workflow”**, select your
   preferences (niche, format, voice/likeness), and click **“Route to C25 Agents &
   Generate”**. Watch the simulated terminal output show exactly how **EARTH, VENUS,
   JUPITER, MARS, SATURN and PLUTO** handle the request — including the chosen niche in
   the parsed-intent line and SATURN injecting the disclosure metadata step.
4. **Deploy:** ready to host on GitHub Pages or Netlify as-is, and already integrated
   directly into the Aimetaverse / Constellation25 ecosystem as the official Ai4Reelz
   portal: the home page tile **“Create YouTube / Social Media Videos with AI”**, the
   site-map chip **“Ai4Reelz Video Studio”**, and the footer link all open it.

## ✅ Features Included

- **Agent Routing Visualization** — clearly maps user inputs to specific C25 agents
  (VENUS for scripting, JUPITER for avatars & voice synthesis, MARS for editing /
  upscaling, SATURN for compliance & QA, PLUTO for forensic logging).
- **Cinematic Prompting Guide** — the strict rules that prevent “AI slop”: bind actions
  with *“while”*, one verb per subject, prioritize concrete nouns, always upscale &
  enhance (4K @ 60/120 FPS via MARS).
- **Compliance Dashboard** — explicitly outlines YouTube’s mandatory AI-disclosure
  labels, automatic enforcement when disclosure is missed, and the minor-edits exemption
  (description-only disclosure).
- **Interactive Onboarding** — a functional form asking the three critical questions
  (Content Niche, Preferred Format, Voice & Likeness Preference) that triggers the
  simulated agent-routing terminal sequence.
- **Constellation25 Branding** — seamless integration with the Kre8tive Konceptz LTD
  aesthetic: glassmorphism panels, cyan/purple gradients, Space Grotesk typography,
  grid backdrop, and the `c25` Tailwind palette (inlined runtime, `preflight` disabled
  so it never touches the host site’s styles).

## Ecosystem wiring

- Embedded copy is scoped under `.ar-embed`; the store’s own fixed `nav` and `footer`
  are stripped because the site shell provides both.
- `Qwen + Ollama` badge retained: the routing narrative matches the local-brain options
  in `py/main.py` (`AIMV_LLM=ollama`) and the APIKonnect Qwen connector.
- Companion cross-talk: ask the humanoid “make me a YouTube video” and it routes here.
