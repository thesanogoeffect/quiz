#!/usr/bin/env bash
#
# Build the deployable site into ./dist.
#
# This is the single source of truth for how the site is assembled - Cloudflare
# Pages, GitHub Actions and a local check all call this same script, so the
# build cannot drift between them.
#
#   dist/
#     index.html      redirect to /ipt/
#     404.html        maps known routes into /ipt/, everything else to /ipt/
#     itp/index.html  /itp/ is a common typo for /ipt/
#     robots.txt      only works at the origin root, not under /ipt/
#     sitemap.xml
#     ipt/            the Nuxt app (its app.baseURL is /ipt/, so it MUST live here)
#
# Usage:  bash scripts/build_site.sh
#         OUT=somewhere bash scripts/build_site.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${OUT:-$REPO_ROOT/dist}"
BASE_PATH="ipt"

cd "$REPO_ROOT/frontend"

echo "==> Installing dependencies"
if [ -f package-lock.json ]; then
  npm ci --no-audit --no-fund
else
  npm install --no-audit --no-fund
fi

echo "==> Building the Nuxt app"
npx nuxt generate

echo "==> Assembling $OUT"
rm -rf "$OUT"
mkdir -p "$OUT/$BASE_PATH"
cp -r "$REPO_ROOT/frontend/.output/public/." "$OUT/$BASE_PATH/"
cp -r "$REPO_ROOT/deploy/root/." "$OUT/"
# macOS AppleDouble files must never be published
find "$OUT" -name '._*' -delete

echo "==> Checking the build"
fail() { echo "::error::$1" >&2; exit 1; }

[ -f "$OUT/$BASE_PATH/index.html" ]        || fail "missing $BASE_PATH/index.html"
[ -f "$OUT/$BASE_PATH/l3.json" ]           || fail "missing $BASE_PATH/l3.json"
[ -f "$OUT/$BASE_PATH/about/index.html" ]  || fail "missing $BASE_PATH/about/index.html"
[ -f "$OUT/$BASE_PATH/questions/index.html" ] || fail "missing $BASE_PATH/questions/index.html"
[ -f "$OUT/index.html" ]                   || fail "missing the root redirect"
[ -f "$OUT/404.html" ]                     || fail "missing 404.html"
[ -f "$OUT/robots.txt" ]                   || fail "missing robots.txt"

# If the base path and the built asset URLs ever disagree, every asset 404s and
# the app shows a blank page. Catch that here rather than in production.
grep -q "/$BASE_PATH/_nuxt/" "$OUT/$BASE_PATH/index.html" \
  || fail "index.html does not reference /$BASE_PATH/_nuxt/ - is app.baseURL still '/$BASE_PATH/'?"

grep -q "<title>" "$OUT/$BASE_PATH/index.html" \
  || fail "index.html has no <title> - is it set in nuxt.config app.head?"

python3 - "$OUT/$BASE_PATH/l3.json" <<'PY'
import json, re, sys
questions = json.load(open(sys.argv[1]))
assert len(questions) > 500, f"only {len(questions)} questions"
# The published data must never carry raw student numbers again.
raw = [q["id"] for q in questions if q.get("author") and str(q["author"]).strip().isdigit()]
assert not raw, f"{len(raw)} questions still have un-hashed authors, e.g. {raw[:5]}"
bad = [q["id"] for q in questions if re.search(r"<p[A-Za-z]|</(?![A-Za-z]|>)", q.get("description_llm") or "")]
assert not bad, f"malformed explanation markup in {bad[:5]} - run scripts/fix_l3_html.py"
print(f"    {len(questions)} questions, authors hashed, markup clean")
PY

echo "==> Built $(du -sh "$OUT" | cut -f1) into $OUT"
