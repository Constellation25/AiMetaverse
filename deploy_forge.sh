#!/usr/bin/env bash
# DEPLOY FORGE v1 — universal Git + Vercel deployment template
# Usage:
#   ./deploy_forge.sh /path/to/build
#   ./deploy_forge.sh /path/to/build --deploy [remote-url]
set -uo pipefail

TARGET="${1:-.}"
MODE="${2:-template}"
REMOTE="${3:-}"

[ -d "$TARGET" ] || { echo "[!] Directory not found: $TARGET"; exit 1; }
cd "$TARGET" || exit 1
ABS="$(pwd)"; NAME="$(basename "$ABS")"
echo "=================================================="
echo " DEPLOY FORGE v1 — $NAME"
echo "=================================================="

# ---------- 1. DETECT BUILD TYPE ----------
TYPE="static"
if [ -f package.json ]; then
  if   grep -q '"next"' package.json;         then TYPE="next"
  elif grep -q '"react-scripts"' package.json; then TYPE="cra"
  elif grep -q '"vue"' package.json;           then TYPE="vue"
  elif grep -q '"svelte"' package.json;        then TYPE="svelte"
  elif grep -q '"astro"' package.json;         then TYPE="astro"
  else TYPE="node"; fi
elif ls *.py api/*.py 2>/dev/null | grep -q .; then TYPE="python"
elif ls *.md 2>/dev/null | grep -q . && ! ls *.html 2>/dev/null | grep -q .; then TYPE="vault"
fi
echo "[+] Build type: $TYPE"

# ---------- 2. RESOLVE OUTPUT DIRECTORY ----------
OUT="."
for cand in public dist build out; do
  if [ -d "$cand" ] && [ -f "$cand/index.html" ]; then OUT="$cand"; break; fi
done

# ---------- 3. VAULT FALLBACK (md-only builds get a live index) ----------
if [ "$TYPE" = "vault" ]; then
  { echo '<!DOCTYPE html><html><head><meta charset="utf-8"><title>'"$NAME"'</title></head><body>'
    echo '<h1>'"$NAME"'</h1><ul>'
    for f in *.md; do [ -e "$f" ] && echo "<li><a href=\"$f\">$f</a></li>"; done
    echo '</ul></body></html>'; } > index.html
  OUT="."
  echo "[+] Generated index.html for markdown vault."
fi
if [ "$TYPE" = "static" ] && [ "$OUT" = "." ] && [ ! -f index.html ]; then
  echo "[!] No index.html found. Static deploy needs one. Aborting."; exit 1;
fi
echo "[+] Output directory: $OUT"

# ---------- 4. GIT TEMPLATE ----------
cat > .gitignore << 'GI'
node_modules/
.vercel/
.env
.env.*
__pycache__/
*.pyc
.DS_Store
*.log
GI

if [ ! -d .git ]; then git init -b main; echo "[+] git initialized."; fi
git config user.name  >/dev/null 2>&1 || git config user.name  "Cygel White"
git config user.email >/dev/null 2>&1 || git config user.email "sovereign@local"
if [ -n "$REMOTE" ]; then
  git remote remove origin 2>/dev/null; git remote add origin "$REMOTE"
  echo "[+] Remote set: $REMOTE"
fi

# ---------- 5. VERCEL TEMPLATE ----------
case "$TYPE" in
  next)   echo '{"framework":"nextjs"}' > vercel.json ;;
  cra)    echo '{"framework":"create-react-app"}' > vercel.json ;;
  vue)    echo '{"framework":"vuejs"}' > vercel.json ;;
  svelte) echo '{"framework":"svelte"}' > vercel.json ;;
  astro)  echo '{"framework":"astro"}' > vercel.json ;;
  node)   echo '{"framework":null,"buildCommand":"npm run build"}' > vercel.json ;;
  python) echo '{"framework":null,"buildCommand":null,"rewrites":[{"source":"/(.*)","destination":"/api/index"}]}' > vercel.json ;;
  *)      echo "{\"framework\":null,\"buildCommand\":null,\"outputDirectory\":\"$OUT\",\"cleanUrls\":true}" > vercel.json ;;
esac
echo "[+] vercel.json written for type: $TYPE"

# ---------- 6. DASHBOARD MIRROR SHEET ----------
cat > DEPLOYMENT_TEMPLATE.md << DM
# Deployment Template — $NAME
Type: $TYPE | Output: $OUT | Generated: $(date -u +%FT%TZ)

Vercel dashboard must mirror vercel.json:
- Root Directory: (leave EMPTY)
- Framework Preset: $TYPE
- Build Command: (blank for static/vault/python, else npm run build)
- Output Directory: $OUT
- Data Preferences: keep AI training DISABLED
DM

# ---------- 7. REUSABLE ONE-TOUCH DEPLOY ----------
cat > deploy.sh << 'DS'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
git add -A
git commit -m "build: $(date -u +%FT%TZ)" || true
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
vercel deploy --prod --yes
echo "[✓] Deployed to production."
DS
chmod +x deploy.sh

# ---------- 8. OPTIONAL LIVE DEPLOY ----------
if [ "$MODE" = "--deploy" ]; then
  command -v vercel >/dev/null 2>&1 || npm i -g vercel >/dev/null 2>&1
  git add -A
  git commit -m "deploy-forge: template $(date -u +%FT%TZ)" || true
  git push -u origin main 2>/dev/null || git push -u origin master
  vercel link --yes
  vercel deploy --prod --yes
fi

echo "=================================================="
echo "[✓] FORGE COMPLETE — $NAME"
echo "    Templates: .gitignore vercel.json deploy.sh DEPLOYMENT_TEMPLATE.md"
echo "    Future builds: cd $ABS && ./deploy.sh"
echo "=================================================="
