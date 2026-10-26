# Deploying & updating this site on GitHub Pages

Your repo (`constillation25.github.io`) is a **user/site repo**, so the site serves from the
repository root at `https://constillation25.github.io/`. The site is 100% static
(HTML/CSS/JS/JPEG, all links relative), which means **no build step is ever needed**.

You have two valid sources. Pick **one** in *Settings → Pages → Source*:

| | Path A — Deploy from a branch | Path B — GitHub Actions ("Static HTML") |
|---|---|---|
| Settings choice | Source: **Deploy from a branch**, Branch: `main`, folder `/ (root)` | Source: **GitHub Actions**, then run the suggested **Static HTML** workflow once (it just adds `.github/workflows/pages.yml`, already included here) |
| Config files needed | `.nojekyll` (included) | `.nojekyll` + `.github/workflows/pages.yml` (both included) |
| Pros | Zero moving parts, rebuilds on every push | Run history, PR/preview-friendly, explicit artifact |
| Cons | No workflow run log in Pages UI | One extra YAML to keep |

**Recommendation: Path A.** Fewer moving parts for a no-build static site; the Actions
path only earns its keep if you later add a build step or want preview deployments.
If you choose Path A, delete `.github/workflows/pages.yml` (or leave it — it only runs
when Source = Actions, but deleting avoids confusion). If you choose Path B, the
workflow uploads the repo root as-is (`path: '.'`), so `py/`, `gen_pages.py` etc. are
published too — harmless, and handy for sharing `py/main.py`.

---

## One-time setup

```bash
# 1. clone the repo that backs your Pages site
git clone https://github.com/constillation25/constillation25.github.io.git
cd constillation25.github.io

# 2. put the site files at the repository root
#    (copy everything from this folder: *.html, assets/, agents/, .nojekyll, …)
rsync -a --delete --exclude '.git' /path/to/aimetaverse/ ./
touch .nojekyll                 # stops Pages from running Jekyll over the site

# 3. first push
git add -A
git commit -m "Ai Metaverse site: static pages + humanoid companion"
git push origin main
```

Then in the GitHub UI: **Settings → Pages → Source → Deploy from a branch → `main` / `/ (root)` → Save.**
(After the first push the Pages settings in your screenshot will show a *Visit site* link.)

## The update loop (the actual answer to "how do I update it")

Every time you change anything here:

```bash
./deploy.sh /path/to/constillation25.github.io     # rsync + commit + push in one step
```

or by hand:

```bash
cd /path/to/constillation25.github.io
# …copy over the changed files, or edit them in place…
git add -A && git commit -m "update humanoid ads" && git push origin main
```

or with **no git on your machine**: github.com → repo → press <kbd>.</kbd> (github.dev) →
drag-drop the changed files into the explorer → Commit & push in the Source Control panel.
Or pure web UI: open a file → pencil icon → paste → *Commit changes*. Fine for text files;
use the clone/`deploy.sh` route for binaries like `assets/*.jpg`.

**What happens after push:** Pages detects the new commit on `main` and re-publishes
automatically — typically 30–90 s. Watch it at *Settings → Pages* ("Your site is live at…"),
the *Actions* tab (Path B), or the deploy commit status on the repo home page.

## Verify a deploy

```bash
curl -sI https://constillation25.github.io/ | head -3          # 200 + server: GitHub Pages
curl -s  https://constillation25.github.io/assets/humanoid.js | head -2   # asset shipped
```
Then hard-refresh the browser (Ctrl/Cmd-Shift-R) — Pages/CDN caches aggressively; a
"stale" site is almost always browser cache, not a failed deploy.

## Gotchas specific to this site

- **`.nojekyll` is mandatory-ish.** Without it Pages runs Jekyll; nothing breaks today
  (no `_`-prefixed files), but any future `_includes`-style name or Gemfile would bite.
- **HTTPS is enforced** on `*.github.io` — good: `getUserMedia` (camera/mic),
  `MediaRecorder` and `SpeechRecognition` only work in secure contexts, so
  CLICK TO TALK and the selfie capture work on Pages out of the box.
- **The Python backend does not run on Pages.** `py/main.py` is a local/desktop bridge;
  on the live site the companion simply reports "Python bridge: not connected" and uses
  browser TTS/STT. Nothing errors.
- **`localStorage` is per-origin.** Test data from `localhost`/file previews does not
  follow you to `constillation25.github.io` — re-forge your agent there once.
- **Relative paths everywhere.** The site also works if you ever move it to a *project*
  repo URL (`username.github.io/repo/`) — no base-url config needed.
- **Binary assets are committed normally** (`assets/face-real.jpg` 71 KB, `face-orb.jpg`
  24 KB, inline data-URI in `index.html` ~20 KB). Repo stays well under any limit.
- **Case sensitivity:** Pages serves on Linux — `Face-Real.JPG` ≠ `face-real.jpg`.
  Keep filenames exactly as referenced.
- **Cache-busting:** if a deploy seems stuck, the asset URL is unchanged so browsers may
  hold old CSS/JS for a while. Quick fix: hard-refresh; nuclear fix: bump a query string
  (`assets/site.css?v=2`) — only needed after big CSS/JS overhauls.

## Custom domain (later, optional)

1. DNS: `CNAME www → constillation25.github.io` (or `A` records for an apex domain).
2. Add a `CNAME` file at the repo root containing `www.yourdomain.com`.
3. Settings → Pages → Custom domain → save → wait for *HTTPS* to tick (letsencrypt, ~1 h).
   The *Enforce HTTPS* box in your screenshot stays checked either way.

## Regenerating content pages

`gen_pages.py` / `gen_extra.py` rebuild the 19 content pages from templates. Run them
*here*, then `./deploy.sh …` — never edit generated pages by hand on GitHub, or the next
regen will overwrite your edits.

---

## Recovery note (2026-10-25): "subpages 404 / update failed"

**What happened:** the live repo at `/` contained only
`index.html` + `.nojekyll` — every subpage and the whole `assets/` folder returned 404,
because the previous update pushed a single file.

**Permanent fix applied:** every page is now **fully self-contained** — CSS, JS (shell,
companion, forge) and both face images (data-URI) are inlined into each `.html`.
There are **zero external asset references left**, so any page that reaches the server
works completely on its own, on Pages, in the in-app preview, or offline from a USB stick.
The `assets/` folder remains only as the maintained source for the generators.

**Redeploy (pick one):**

1. **Web UI, no git (fastest):** GitHub → repo `AiMetaverse` → *Add file → Upload files* →
   drag the 21 `.html` files + `agents/agent.html` + `.nojekyll` from
   `aimetaverse-github-pages.zip` (or this folder) → *Commit changes* to `main`.
   Overwrite when prompted. Done — Pages republishes in ~1 min.
2. **One command:** `./deploy.sh /path/to/AiMetaverse-clone` (rsync/tar + commit + push).
3. **github.dev:** press `.` on the repo, drag the files in, commit & push.

**Verify:**
```
https:///why-ai.html        -> 200
https:///avatar-create.html -> 200
https:///apikonnect.html    -> 200
```
If a page still 404s after a successful push: Settings → Pages → confirm **Source**
branch matches the branch you pushed (`main` vs `master`), folder `/ (root)`.

---

## Structure update (latest): folder index.html for every module

Every module now ships **twice**: `foo.html` **and** `foo/index.html` (byte-similar, differing
only in a `<base>` tag). All internal links use directory form (`why-ai/index.html`), so
every URL shape works on Pages and offline:

```
/AiMetaverse/why-ai.html          -> flat copy
/AiMetaverse/why-ai/              -> folder copy (GitHub serves index.html)
/AiMetaverse/why-ai/index.html    -> folder copy, explicit
/AiMetaverse/agents/agent/        -> nested folder copy (base ../../)
```

Upload **all 43 files** from `aimetaverse-github-pages.zip` (21 flat + 21 folder copies +
`.nojekyll`). New since last bundle: `communities.html` + `communities/index.html`
(the embedded *Find Friends / Metaverse Communities* storefront-style page, last nav tab).

To embed another page you send: drop the original in `store/`, add one entry in
`gen_pages.py` (CSS is auto-scoped under `.mvc-embed`-style wrappers, JS queries are
re-scoped, card links rewired), run `python3 gen_pages.py`, redeploy.
