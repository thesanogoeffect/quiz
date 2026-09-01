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
| `deploy/root/` | Files copied to the site root by CI (CNAME, `/` and `/itp/` redirects) |
| `.github/workflows/deploy.yml` | Builds and publishes to GitHub Pages |

## Running the app locally

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000/ipt/
```

The dev server serves the app under the `/ipt/` base path, same as production.

To reproduce a production build:

```bash
cd frontend
npx nuxt generate --preset github_pages
npx serve .output/public     # note: this serves at / , not /ipt/
```

## How it is deployed

`.github/workflows/deploy.yml` runs on every push to `main` that touches `frontend/` or `deploy/`:

1. `npm ci` + `npx nuxt generate --preset github_pages` → static output in `frontend/.output/public`
2. that output is copied into `dist/ipt/` (the app's `app.baseURL` is `/ipt/`, so it *must* live
   under that directory), and `deploy/root/` is copied to `dist/`
3. a sanity check asserts the key files exist and `l3.json` still parses
4. the artifact is published to GitHub Pages

`deploy/root/` provides:

- `CNAME` — the custom domain `quiz.jakubwerner.com`
- `index.html` / `404.html` — redirect the site root and unknown paths to `/ipt/`
- `itp/index.html` — `/itp/` is a common typo for `/ipt/`; redirect instead of 404

### One-time setup on a fresh repo

1. **Settings → Pages → Source: GitHub Actions**
2. **Settings → Pages → Custom domain:** `quiz.jakubwerner.com`, then tick *Enforce HTTPS*
3. **DNS:** point `quiz.jakubwerner.com` at GitHub Pages —
   `CNAME quiz.jakubwerner.com → thesanogoeffect.github.io`
   (in Cloudflare, set the record to **DNS only**, not proxied, so GitHub can issue the certificate)

### Adding another subject later

The app is deliberately mounted at a subpath so more courses can be added alongside it. To add one,
build that app with its own `app.baseURL` and copy it into another directory under `dist/` in the
workflow's *Assemble site* step.

## Updating the questions

`frontend/public/l3.json` is what the app loads at runtime. The pipeline that produces it lives in
`scripts/` — see `workflows/pipeline_steps.txt` for the intended order. After regenerating, run the
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
Firestore collection called `questions`, keyed by the question id as a string. The Firebase web
config in `frontend/app/plugins/firebase.client.js` is public by design — a web API key is an
identifier, not a secret. What actually protects the data is the security rules.

`firestore.rules` restricts the collection to: read one document by id, and move one of the seven
known counters by exactly ±1. Nothing else — no arbitrary field writes, no collection listing, no
create or delete.

```bash
firebase deploy --only firestore:rules
```

**Deploy these — the database is currently wide open.** Verified against the live project on
2026-09-01 with non-mutating probes (each write carried an impossible `updateTime` precondition, so
the rules were evaluated but nothing could commit): an unauthenticated client can today set any
field to any value, delete a question document, and page through the whole collection. The rules
close all three.

Nothing in the app breaks: the browser only ever calls `getDoc` and `updateDoc` with
`increment(±1)` — there is no `getDocs`, `query`, `setDoc`, `addDoc`, `deleteDoc` or `onSnapshot`
anywhere in `frontend/app/`. The Python pipeline in `scripts/` does list the collection, but it
uses `firebase_admin`, which bypasses security rules entirely.

The rules themselves have not been executed against the live project, so before deploying, paste
them into the Firebase console → Firestore → Rules → Rules Playground and confirm the cases listed
at the top of the file. If they turn out too strict the quiz keeps working — the client logs a
warning and carries on — but the community counters stop moving.

Worth doing at some point: turn on [App Check](https://firebase.google.com/docs/app-check) with
reCAPTCHA v3 (it is free on every plan, Spark included). The rules stop a client writing
*nonsense*, but nothing currently stops one writing *a lot*.

### Is Firestore the right choice, and can it cost anything?

Short answer: yes, and no. Measured on 2026-09-01:

- The app does **one document read and one document write per question served**. Nothing else
  touches the database.
- The free (Spark) quota is 50,000 reads and 20,000 writes per day. **Writes bind first**, so the
  ceiling is about 20,000 questions answered per day — roughly 330 students doing 60 questions
  each, or 200 doing 100.
- Lifetime usage to date is **131,380 questions asked / 124,675 answered**. Even if every one of
  those had happened in a single 20-day exam period, that is a third of the daily free quota.
- **On Spark a bill is not possible.** No payment method is attached, and exceeding the quota
  returns `RESOURCE_EXHAUSTED` until it resets around midnight Pacific — Firebase suspends the
  product rather than charging.
  ([plans](https://firebase.google.com/docs/projects/billing/firebase-pricing-plans),
  [error codes](https://cloud.google.com/firestore/docs/understand-error-codes))
- Even on Blaze the numbers are trivial: the app's entire lifetime, if the free tier did not exist,
  costs well under a euro at list price. Reaching $1 in a *single day* needs several hundred
  thousand questions answered that day.

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
