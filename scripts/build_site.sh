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
# frontend/public/l3.json holds the whole question set, explanations included,
# pretty-printed so a question change shows up in a diff. That single file is
# split in two on the way out - see "Splitting the explanations" below.
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
# Pin the Nitro preset. Nitro sniffs the environment and picks a preset on its
# own: on Cloudflare Pages it chose `cloudflare-pages`, which builds a Worker
# instead of a static site - no HTML shell, and the assets nested under the
# baseURL. This site is plain static files on any host, so say so explicitly and
# get an identical build everywhere.
export NITRO_PRESET=static
npx nuxt generate

echo "==> Assembling $OUT"
# Nitro has shipped both layouts: assets at the root of .output/public, and
# assets nested under the baseURL. Take whichever one actually holds the app.
GENERATED="$REPO_ROOT/frontend/.output/public"
if [ -f "$GENERATED/$BASE_PATH/index.html" ]; then
  GENERATED="$GENERATED/$BASE_PATH"
fi
[ -f "$GENERATED/index.html" ] || {
  echo "::error::no index.html under frontend/.output/public - did the Nitro preset change?" >&2
  find "$REPO_ROOT/frontend/.output/public" -maxdepth 2 -name '*.html' >&2 || true
  exit 1
}

rm -rf "$OUT"
mkdir -p "$OUT/$BASE_PATH"
cp -r "$GENERATED/." "$OUT/$BASE_PATH/"
cp -r "$REPO_ROOT/deploy/root/." "$OUT/"
# macOS AppleDouble files must never be published
find "$OUT" -name '._*' -delete

echo "==> Splitting the explanations out of l3.json"
# Two thirds of l3.json is description_llm, and none of it is needed until a
# student has answered something. Ship the questions on their own and put the
# explanations in a file the app fetches once the browser goes idle. The repo
# keeps one pretty-printed source file; only the built output is split, so
# question diffs stay readable and no script has to know about this.
node - "$OUT/$BASE_PATH" <<'JS'
const fs = require("node:fs");
const dir = process.argv[2];
const questions = JSON.parse(fs.readFileSync(`${dir}/l3.json`, "utf8"));

const explanations = {};
for (const question of questions) {
  explanations[question.id] = question.description_llm ?? "";
  delete question.description_llm;
}

// Minified: these two are only ever read by the app, never by a human.
fs.writeFileSync(`${dir}/l3.json`, JSON.stringify(questions));
fs.writeFileSync(`${dir}/explanations.json`, JSON.stringify(explanations));

const kb = (f) => Math.round(fs.statSync(`${dir}/${f}`).size / 1024);
console.log(`    l3.json ${kb("l3.json")} kB, explanations.json ${kb("explanations.json")} kB`);
JS

echo "==> Checking the build"
fail() { echo "::error::$1" >&2; exit 1; }

[ -f "$OUT/$BASE_PATH/index.html" ]        || fail "missing $BASE_PATH/index.html"
[ -f "$OUT/$BASE_PATH/l3.json" ]           || fail "missing $BASE_PATH/l3.json"
[ -f "$OUT/$BASE_PATH/explanations.json" ] || fail "missing $BASE_PATH/explanations.json"
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

# Node rather than python3: node is guaranteed present here (we just ran the
# Nuxt build with it), whereas the build image's Python is not ours to rely on.
node - "$OUT/$BASE_PATH/l3.json" <<'JS'
// `node -` reads the script from stdin, so the file argument lands in argv[2].
const questions = JSON.parse(require("node:fs").readFileSync(process.argv[2], "utf8"));
const die = (m) => { console.error(`::error::${m}`); process.exit(1); };

if (questions.length <= 500) die(`only ${questions.length} questions in l3.json`);

// The published data must never carry raw student numbers again.
const raw = questions.filter((q) => q.author && /^\d+$/.test(String(q.author).trim()));
if (raw.length) die(`${raw.length} questions still have un-hashed authors, e.g. ${raw.slice(0, 5).map((q) => q.id)}`);

// Explanations were split into their own file above, so they are checked from
// there. Every question needs one: a missing entry is a silent "No explanation
// available." in the sidebar, which is exactly the kind of thing that only
// turns up when a student asks why.
const explanationsPath = process.argv[2].replace(/l3\.json$/, "explanations.json");
let explanations;
try {
  explanations = JSON.parse(require("node:fs").readFileSync(explanationsPath, "utf8"));
} catch (e) {
  die(`explanations.json missing or unreadable (${e.message}) - did the split step run?`);
}

const orphans = questions.filter((q) => !String(explanations[q.id] ?? "").trim());
if (orphans.length) die(`${orphans.length} questions have no explanation, e.g. ${orphans.slice(0, 5).map((q) => q.id)}`);

if (questions.some((q) => "description_llm" in q)) die("l3.json still carries description_llm - the split step did not run");

// `<pFoo` and `</<` make the browser swallow a whole sentence of explanation.
const bad = Object.entries(explanations).filter(([, html]) => /<p[A-Za-z]|<\/(?![A-Za-z]|>)/.test(html || ""));
if (bad.length) die(`malformed explanation markup in ${bad.slice(0, 5).map(([id]) => id)} - run scripts/fix_l3_html.py`);

console.log(`    ${questions.length} questions, authors hashed, ${Object.keys(explanations).length} explanations, markup clean`);

// The community stats the app shows come from this snapshot, not Firestore.
const statsPath = process.argv[2].replace(/l3\.json$/, "stats.json");
let stats;
try {
  stats = JSON.parse(require("node:fs").readFileSync(statsPath, "utf8"));
} catch (e) {
  die(`stats.json missing or unreadable (${e.message}) - run node scripts/fetch_stats_snapshot.mjs`);
}
if (!stats.questions || typeof stats.questions !== "object") die("stats.json has no questions object");
const ageDays = (Date.now() - Date.parse(stats.fetched_at)) / 86400000;
if (!(ageDays < 60)) console.warn(`::warning::stats.json is ${Math.round(ageDays)} days old - is the refresh workflow running?`);
console.log(`    stats snapshot: ${Object.keys(stats.questions).length} questions, ${Math.round(ageDays)} days old`);
JS

echo "==> Built $(du -sh "$OUT" | cut -f1) into $OUT"
