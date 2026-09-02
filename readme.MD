# Intro to P&T Quiz

A student-made quiz app for the **Introduction to Psychology & Technology** course at TU/e Eindhoven.

**Live:** <https://quiz.jakubwerner.com/ipt/>

Built by Jakub Werner. Thanks to prof. Daniël Lakens for endorsing the idea, and to Tim, Aaravee,
Naomi, Eline, Finn and Hubert. This is not an official part of the TU/e course, just a passion
project — I am not responsible for any mistakes or inaccuracies.

---

## Repository layout

| Path | What it is |
| --- | --- |
| `frontend/` | The Nuxt 4 + Vuetify 3 app that students actually use |
| `frontend/public/l3.json` | The question set the app ships with (the "L3" export) |
| `scripts/` | The data pipeline: Google Sheets → SQLite (`data/l2.db`) → LLM enrichment → `l3.json` |
| `dashboard/` | Streamlit dashboards for browsing/administering questions |
| `data/` | `l2.db` (working database) plus the generated `l3.csv` / `l3.json` |
| `deploy/root/` | Files copied to the site root by the build (redirects, robots.txt, sitemap) |
| `scripts/build_site.sh` | Builds and assembles `dist/` — what Cloudflare Pages runs |

## Running the app locally

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000/ipt/
```

The dev server serves the app under the `/ipt/` base path, same as production.

To reproduce exactly what Cloudflare builds:

```bash
bash scripts/build_site.sh
npx serve dist               # then open http://localhost:3000/ipt/
```

## How it is deployed

**Cloudflare Pages**, building straight from this repository. Cloudflare serves private repos on
the free plan (GitHub Pages does not), gives unlimited bandwidth and 500 builds/month, and since
the DNS for `jakubwerner.com` already lives in Cloudflare the custom domain needs no manual record.

Everything about the build lives in `scripts/build_site.sh`, so it cannot drift between Cloudflare
and your laptop:

```bash
bash scripts/build_site.sh     # -> ./dist
npx serve dist                 # then open http://localhost:3000/ipt/
```

It builds the Nuxt app, assembles `dist/`, and then refuses to finish if anything is wrong — a
missing route, assets that do not match the base path, a page with no `<title>`, fewer than 500
questions, an un-hashed student number, or malformed explanation markup.

### The layout it produces

```
dist/
  index.html      redirect to /ipt/
  404.html        maps known routes into /ipt/, everything else to /ipt/
  itp/index.html  /itp/ is a common typo for /ipt/
  robots.txt      these only work at the origin root, not under /ipt/
  sitemap.xml
  ipt/            the Nuxt app (app.baseURL is /ipt/, so it MUST live in this directory)
```

### One-time Cloudflare setup

1. **Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git**, and pick
   `thesanogoeffect/quiz`. Authorise the Cloudflare GitHub App for this repo — private is fine.
2. Build settings:

   | Setting | Value |
   | --- | --- |
   | Framework preset | None |
   | Build command | `bash scripts/build_site.sh` |
   | Build output directory | `dist` |
   | Root directory | `/` (leave empty) |

   `.node-version` pins Node 22, so nothing else needs configuring.
3. Deploy, and check the `*.pages.dev` URL Cloudflare gives you — visit `/ipt/` on it. If the quiz
   loads there, the app works and anything left is DNS.
4. **Custom domains → Set up a custom domain →** `quiz.jakubwerner.com`. Because the zone is already
   on Cloudflare, it creates the record and the certificate itself; there is nothing to add by hand.
5. Verify from outside your tailnet — `dig @1.1.1.1 quiz.jakubwerner.com`, or a phone on mobile
   data. `jakubwerner.com` is routed to a Tailscale address on your own machines, so the name
   resolving on your laptop proves nothing about whether students can reach it.

Every push to `main` redeploys. Pull requests get their own preview URL.

### Adding another subject later

The app is deliberately mounted at a subpath so more courses can live alongside it. To add one,
build that app with its own `app.baseURL` and copy it into another directory under `dist/` in
`scripts/build_site.sh`.

## Updating the questions

`frontend/public/l3.json` is what the app loads at runtime. The pipeline that produces it lives in
`scripts/` — see `scripts/pipeline_steps.txt` for the intended order. After regenerating, run the
two clean-up steps and copy the result into `frontend/public/l3.json`; pushing redeploys
automatically.

```bash
python3 scripts/fix_l3_html.py       frontend/public/l3.json   # repair `<pFoo` / `</>` in explanations
python3 scripts/anonymize_authors.py frontend/public/l3.json   # hash student numbers
python3 scripts/anonymize_authors.py frontend/public/l3.json --check   # fails if any raw id remains
```

The app also normalises data as it loads (trims whitespace, strips leftover `a.`/`b.` option
prefixes, keeps "none of the above"-style options in last position, repairs malformed explanation
markup), so the raw export does not have to be perfect.

### The September 2026 review

Every active question was reviewed against the OpenStax Psychology 2e text on 2026-09-02, one
LLM reviewer per chapter, with the community stats (correct rate, flags, votes) attached as a
signal. Below-chance correct rates turned out to be a reliable pointer to wrong keys. The full
record is `data/question_review_2026-09.json`: one entry per touched question with the verdict,
the problem, the reason (citing the book section) and the exact fields that changed. The rubric
the reviewers followed is `data/question_review_rubric.md`, so the pass can be repeated.

| Outcome | Questions |
| --- | --- |
| Active before / after | 956 / 829 |
| Wrong key corrected | 25 |
| Other fixes (ambiguous, broken stem, weak distractor, typo, wrong explanation) | 99 |
| Moved to the chapter they actually belong to | 44 |
| Disabled as duplicates | 79 |
| Disabled as unanswerable from the book or unsalvageable | 48 |

Disabled questions stay in the file with `is_disabled: "1"`, so any of them can be brought back by
flipping the flag. To apply a findings file (this one, or a future one in the same format):

```bash
python3 scripts/apply_question_review.py data/question_review_2026-09.json --dry-run
python3 scripts/apply_question_review.py data/question_review_2026-09.json
```

The community counters of a re-keyed question describe the old key, so the "x% got this right"
panel is misleading for those until they are reset. That needs the admin credential:

```bash
python3 scripts/backup_firestore_stats.py                                        # first
python3 scripts/reset_question_stats.py data/question_review_2026-09.json --dry-run
python3 scripts/reset_question_stats.py data/question_review_2026-09.json
```

### Privacy

The published `l3.json` is downloadable by anyone. The `author` column originally held TU/e student
numbers, which are directly re-identifiable personal data, so it now holds salted HMAC tokens
(`s-1a2b3c4d5e`) instead. Questions by the same student still share a token, but the number itself is
not published, and the app does not display the field at all.

- The salt lives in `.author_salt` (gitignored, `chmod 600`) or `$QUIZ_AUTHOR_SALT`.
  **Back it up.** Lose it and a future pipeline run produces different tokens.
- `data/l2.db`, `data/l3.csv`, `data/l3.json` and `dashboard/l3.csv` keep the real mapping and are no
  longer tracked by git.
- Those files *are* still in the git history. **Before making this repository public**, run
  `scripts/purge_student_numbers_from_history.sh` on a fresh clone — read its header first, it
  rewrites history and needs a force-push.
- `dashboard/l2_admin_dashboard.py` can edit questions and reset Firestore stats using an admin
  credential and has no authentication. Run it on localhost only; never deploy it.

### Per-question fields

`id`, `question_title`, `chapter_id`, `correct_answer`, `distractor_1..3`, `source`, `author`,
`description_llm`, `is_disabled`. Setting `is_disabled` to a truthy value (`1`, `true`, `"1"`)
hides a question from the quiz — note that the string `"0"` counts as *not* disabled.

Chapters listed in `BANLIST_CHAPTERS` (`frontend/app/stores/question.js`) are excluded everywhere,
regardless of what is in the data. Chapters 11, 13 and 16 are out of scope for this course.

## Community stats

Per-question counters (times asked/answered/correct/skipped/flagged, up- and downvotes) live in a
Firestore collection called `questions`, keyed by the question id as a string.

**The app never reads Firestore.** It loads `frontend/public/stats.json`, a snapshot of all the
counters that ships with the build, and bumps its in-memory copy as the student answers and votes,
so the numbers on screen include their own actions. Only the counter *writes* go to Firestore,
fire-and-forget. This keeps every network dependency off the path between a student and the next
question, and costs zero document reads. The sidebar shows the snapshot's date.

`.github/workflows/refresh-stats.yml` regenerates the snapshot every Monday (or on demand from the
Actions tab) and commits it, which triggers the normal Cloudflare deploy. To refresh by hand:

```bash
node scripts/fetch_stats_snapshot.mjs     # -> frontend/public/stats.json, then commit
```

The build refuses to finish without a parseable snapshot and warns when it is over 60 days old. The Firebase web
config in `frontend/app/plugins/firebase.client.js` is public by design — a web API key is an
identifier, not a secret. What actually protects the data is the security rules.

`firestore.rules` restricts the collection to: read one document by id, and move one of the seven
known counters by exactly ±1. Nothing else — no arbitrary field writes, no collection listing, no
create or delete.

```bash
npx firebase-tools login          # one-off, opens a browser
npx firebase-tools deploy --only firestore:rules
```

`.firebaserc` pins the project, so neither command needs `--project`. Back the counters up first
(`python3 scripts/backup_firestore_stats.py`) — that is the one thing here which cannot be
regenerated. The rules set `allow list: if false`, so nothing can page through the collection any
more; the backup script fetches documents by name with `:batchGet`, which the rules evaluate as
`get`, and so still needs no credentials. `scripts/firestore.py` (`firebase_admin`) bypasses the
rules entirely and is the way in for anything that must write in bulk.

Check the *deployed* rules from outside, before and after — this beats the Rules Playground,
which only tests what you have pasted into the console rather than what is live:

```bash
python3 scripts/verify_firestore_rules.py
```

It probes with nothing but the public web key, from the same position a student's browser is in,
and changes nothing: every write probe carries an impossible `currentDocument.updateTime`, so even
a write the rules *allow* cannot commit (403 means the rules refused it, 400 FAILED_PRECONDITION
means they permitted it).

It checks both directions: that the rules are tight (no listing, no arbitrary writes, no deletes)
*and* that they are not too tight — the app bumps three counters in a single write when you answer
a question, and un-voting sends −1, so those exact shapes are probed too. Rules that look correct
in the Playground can still freeze the counters.

Baseline on 2026-09-01, before deploying, was **4 of 6 failing** — listing the collection, setting a
counter to 999999, writing an arbitrary field and deleting a question were all permitted. After
deploying on 2026-09-02 it reports **13 of 13**, and a fresh backup matched the pre-deploy one on
all 1,048 documents field for field, so the lockdown moved no data.

You can also sanity-check in the console — Firestore → Rules → Rules Playground:

| Simulation | Location | Expect |
| --- | --- | --- |
| `get` | `/questions/1` | **Allow** |
| `list` | `/questions` | **Deny** |
| `update` with `{times_answered: <current + 1>}` | `/questions/1` | **Allow** |
| `update` with `{times_answered: 999999}` | `/questions/1` | **Deny** |
| `update` with `{question_title: "x"}` | `/questions/1` | **Deny** |
| `delete` | `/questions/1` | **Deny** |

If any row disagrees, do not deploy — the counters would silently stop moving.

The rules were deployed on 2026-09-02. Before that the database was wide open: an unauthenticated
client could set any field to any value, delete a question document, and page through the whole
collection. Nothing in the app depends on any of that — the browser only ever calls `updateDoc` with
`increment(±1)`; there is no `getDoc`, `getDocs`, `query`, `setDoc`, `addDoc`, `deleteDoc`
or `onSnapshot` anywhere in `frontend/app/`. The Python pipeline in `scripts/` does list the
collection, but it uses `firebase_admin`, which bypasses security rules entirely.

Worth doing at some point: turn on [App Check](https://firebase.google.com/docs/app-check) with
reCAPTCHA v3 (it is free on every plan, Spark included). The rules stop a client writing
*nonsense*, but nothing currently stops one writing *a lot*.

### Is Firestore the right choice, and can it cost anything?

Short answer: yes, and no. Measured on 2026-09-01:

- The app does **one document write per question served** and no reads at all (the stats come
  from the shipped snapshot; the weekly refresh reads every document once).
- The free (Spark) quota is 50,000 reads and 20,000 writes per day, so the ceiling is about
  20,000 questions answered per day — roughly 330 students doing 60 questions each, or 200
  doing 100.
- Lifetime usage to date is **131,380 questions asked / 124,675 answered**. Even if every one of
  those had happened in a single 20-day exam period, that is a third of the daily free quota.
- **On Spark a bill is not possible.** No payment method is attached, and exceeding the quota
  returns `RESOURCE_EXHAUSTED` until it resets around midnight Pacific — Firebase suspends the
  product rather than charging.
  ([plans](https://firebase.google.com/docs/projects/billing/firebase-pricing-plans),
  [error codes](https://cloud.google.com/firestore/docs/understand-error-codes))
- Even on Blaze the numbers are trivial: the app's entire lifetime, if the free tier did not exist,
  costs **$0.16–$0.32** at list price. Reaching $1 in a *single day* needs roughly 444,000 questions
  answered that day — about 4,400 students doing 100 each.
- That range is the region, not uncertainty: a single-region US location (`us-central1`) is
  $0.03/100k reads and $0.09/100k writes; the US multi-region (`nam5`) is exactly double, $0.06 and
  $0.18 ([pricing](https://cloud.google.com/firestore/pricing)). Which one this project uses is
  shown at the top of Firebase console → Firestore Database; it needs an OAuth credential to read
  via the API, so it is a console lookup.
- Deploying the security rules adds **no** read cost. Rules only bill extra reads when they call
  `get()` / `exists()` to look at another document; `firestore.rules` uses only `resource.data` and
  `request.resource.data`.
- One caveat if the project ever grows: the free quota covers the `(default)` database only. A
  second, named database requires billing and gets **no** free quota at all.

The one thing that genuinely costs something is bundle size: the Firebase SDK is **332 KB raw /
83 KB gzipped**, about a third of the app's JavaScript, for seven integer counters. That is the
only real argument for changing anything, and it is not worth a rewrite.

Alternatives were checked and rejected: Workers KV allows only 1,000 writes/day; Supabase pauses
free projects after a week idle (fatal for a course app used in bursts); Realtime Database caps
Spark at 100 simultaneous connections. Cloudflare D1 does have ~5x the write headroom and also
cannot bill you, but it needs a Worker in front of it, i.e. a server to maintain. Only move if
writes actually start failing across multiple days.

Back the counters up before touching any of this — they are the only thing here that cannot be
regenerated:

```bash
python3 scripts/backup_firestore_stats.py     # -> data/firestore-backup-<date>.json (gitignored)
```

### Local development does not write to the live database

`frontend/app/plugins/firebase.client.js` marks the connection read-only when the page is served
from `localhost`, `127.0.0.1` or a `.local` host: community stats still load, but no counter
updates are sent. Running the quiz locally used to add phantom answers to the real totals. Append
`?firestore=live` to override.
