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
| `deploy/root/` | Files copied to the site root by CI (redirects, robots.txt, sitemap) |
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

- `index.html` / `404.html` — redirect the site root and unknown paths to `/ipt/`. The 404 maps
  known routes across (`/itp/questions` → `/ipt/questions/`) and sends anything else to `/ipt/`,
  which is a real file, so it cannot loop.
- `itp/index.html` — `/itp/` is a common typo for `/ipt/`; redirect instead of 404
- `robots.txt` and `sitemap.xml` — these only work at the origin root, not under `/ipt/`

There is deliberately **no `CNAME` file**: GitHub ignores one when the site is published from a
custom Actions workflow ("any existing `CNAME` file is ignored and is not required" —
[docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)).
The domain is set in repository settings instead.

### First deploy — order matters

As of 2026-09-01 this has never run: `has_pages` is `false`, there are zero workflow runs, and
`quiz.jakubwerner.com` has no public DNS record. Do these in order. **Adding DNS first would point
students at GitHub's "there isn't a site here" 404, which browsers cache** — worse than the current
NXDOMAIN.

1. **Push to `main`.** The workflow only triggers on `push: branches: [main]`, and
   `actions/configure-pages` enables Pages for you on the first successful run.
   Watch it with `gh run watch`.
2. **Verify on the default domain first:** `https://thesanogoeffect.github.io/quiz/ipt/`.
   If that works, the app works, and anything left is DNS.
3. **Settings → Pages → Custom domain:** `quiz.jakubwerner.com`. This — not a file in the repo —
   is what sets the domain.
4. **Cloudflare:** one `CNAME` record, `quiz` → `thesanogoeffect.github.io`, proxy **off**
   (grey cloud). An orange-clouded record breaks GitHub's domain verification and certificate
   issuance.
5. **Wait** — the certificate can take up to 24 hours. Then tick *Enforce HTTPS*, and check from
   outside your tailnet: `dig @1.1.1.1 quiz.jakubwerner.com`, or a phone on mobile data.

Note that `jakubwerner.com` is routed to a Tailscale address on your own machines, so
`quiz.jakubwerner.com` resolving locally proves nothing about whether students can reach it.

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
npx firebase-tools login          # one-off, opens a browser
npx firebase-tools deploy --only firestore:rules
```

`.firebaserc` pins the project, so neither command needs `--project`. Before deploying, back the
counters up (`python3 scripts/backup_firestore_stats.py`) — note that the new rules set
`allow list: if false`, so after this the backup script needs an admin credential rather than the
public key, and `scripts/firestore.py` (which uses `firebase_admin`) becomes the way to read the
collection in bulk.

Sanity-check in the console first — Firestore → Rules → Rules Playground:

| Simulation | Location | Expect |
| --- | --- | --- |
| `get` | `/questions/1` | **Allow** |
| `list` | `/questions` | **Deny** |
| `update` with `{times_answered: <current + 1>}` | `/questions/1` | **Allow** |
| `update` with `{times_answered: 999999}` | `/questions/1` | **Deny** |
| `update` with `{question_title: "x"}` | `/questions/1` | **Deny** |
| `delete` | `/questions/1` | **Deny** |

If any row disagrees, do not deploy — the counters would silently stop moving.

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
