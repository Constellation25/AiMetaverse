#!/usr/bin/env bash
# Usage:  ./deploy.sh /path/to/your/constillation25.github.io-clone
# Syncs this folder into the repo clone, commits and pushes. Pages rebuilds automatically.
set -euo pipefail
REPO="${1:?usage: ./deploy.sh /path/to/repo-clone}"
SRC="$(cd "$(dirname "$0")" && pwd)"

[ -d "$REPO/.git" ] || { echo "not a git clone: $REPO" >&2; exit 1; }

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete --exclude '.git' "$SRC/" "$REPO/"
else
  # portable fallback: remove git-tracked files, then copy the tree with tar
  ( cd "$REPO" && git ls-files -z | xargs -0 -r rm -f )
  ( cd "$SRC" && tar cf - --exclude='.git' --exclude='.github/pages.yml' . ) | ( cd "$REPO" && tar xf - )
fi

# Jekyll must never touch this repo (pure static site)
touch "$REPO/.nojekyll"

cd "$REPO"
git add -A
if git diff --cached --quiet; then
  echo "nothing changed — no commit needed"
else
  git commit -m "site update $(date -u +%Y-%m-%dT%H:%MZ)"
  git push origin HEAD
  echo
  echo "pushed. Pages rebuilds in ~30-90 s ->  https://constillation25.github.io/"
fi
