# VR Access & Hardware Hub (`vr-hub.html` / `vr-hub/`)

Constellation25 | VR Access & Hardware Hub — the subpage that the
**"Access VR Virtual Reality Platforms — Cardboard to HMD"** tile opens.

## 🚀 How to Use This

1. **Save the file:** source document lives at `store/vr-hub.html`; the generated,
   site-integrated page is `vr-hub.html` (+ folder copy `vr-hub/index.html`) — fully
   self-contained (inlined Tailwind runtime with the `c25` palette, scoped CSS, no
   external assets required beyond optional Font Awesome icons).
2. **Open in browser:** double-click `vr-hub.html`, or visit
   `https://constillation25.github.io/AiMetaverse/vr-hub/` once deployed.
3. **Test the interactivity:**
   - Click the **Entry-Level (Mobile)**, **Mid-Range (Tethered)** and **Premium
     (Standalone)** tabs to see the dynamic content change (setup, access path,
     experience tier, recommended apps / launchers / headsets).
   - Click the **"Setup Guide"** button under the Mid-Range (Tethered) section to
     reveal the step-by-step **SteamVR** setup instructions (install → connect →
     room setup → troubleshooting tip), and the ✕ to collapse it again.
4. **Deploy:** ready to host on GitHub Pages or Netlify as-is, and already integrated
   into the Constellation25 ecosystem (home tile, site-map chip, footer link).

## ✅ Features Included

- **Interactive Hardware Spectrum** — tabbed interface letting users instantly find the
  setup and experience details for their specific VR tier (Mobile 3DoF, Tethered 6DoF,
  Standalone/MR).
- **On-Demand Setup Guides** — a dedicated, collapsible SteamVR setup section walking
  through installation, headset connection and room setup, plus a troubleshooting tip
  for the "Headset Disconnected" error.
- **Clear Call-to-Action** — directs users who need further help to either browse a
  headset store or contact VR support.
- **Constellation25 Branding** — maintains the sleek glassmorphic cyan/purple/emerald
  gradient aesthetic established across the ecosystem.

## Ecosystem wiring

- Embedded copy scoped under `.vr-embed`; tab queries re-scoped so they can never touch
  other tab systems on the host page; the store's fixed `nav`/`footer` are stripped
  because the site shell provides both.
- Tailwind runtime is inlined with `corePlugins.preflight: false`, so the hub's styles
  cannot reset the host page.
- Companion cross-talk: ask the humanoid "which headset should I buy?" and it routes
  here via the Worlds/VR answers.
