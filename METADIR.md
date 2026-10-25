# Metaverse World Directory (`metaverse-directory.html` / `metaverse-directory/`)

Constellation25 | Metaverse World Directory — the subpage the
**"Explore 100s of Metaverse Environments — World directory"** tile opens.

## 🚀 How to Use This

1. **Save the file:** source document at `store/metaverse-directory.html`; generated,
   site-integrated page is `metaverse-directory.html` (+ folder copy
   `metaverse-directory/index.html`) — fully self-contained (inlined Tailwind runtime
   with the `c25` palette, scoped CSS, no external assets beyond optional FA icons).
2. **Open in browser:** double-click the file, or visit
   `https://constillation25.github.io/AiMetaverse/metaverse-directory/` once deployed,
   to explore all 100+ platforms.
3. **Use filters** to browse by category — All, Browser-Based, Gaming, VR Social,
   Blockchain, Enterprise, Japanese.
4. **Search bar** (relocated from the stripped nav to above the filter row) finds
   specific platforms instantly, combined with the active filter.
5. **Click any platform card** ("Visit Platform") to open its official website in a
   new tab.

## ✅ Features Included

- **100+ platforms cataloged across 7 categories** (34 rich cards now, directory
  structure ready for the full 100+ as data arrives).
- **Interactive filters** for one-click category browsing.
- **Live search** across names and descriptions.
- **Quick comparison table** — browser support, VR requirement, free tier, best-for and
  max users for flat.social, Roblox, VRChat, Decentraland and Second Life.
- **Platform cards** with badges (Free/Paid/Freemium/MAU), feature chips and direct links.
- **2026 data** including shutdowns and active platforms.
- **Responsive design** — mobile and desktop.
- **Constellation25 branding** — signature glassmorphic cyan/purple aesthetic.

## Ecosystem wiring

- Embedded copy scoped under `.wd-embed`; filter queries re-scoped so they cannot touch
  other filter systems on the host page; store nav/footer stripped (site shell provides
  both); search input relocated out of the removed nav.
- Tailwind runtime inlined with `corePlugins.preflight: false` — no global reset leaks.
- Opened from: home tile *Explore 100s of Metaverse Environments*, site-map chip
  *Metaverse World Directory*, footer link; companion routes "which worlds exist?" here.
