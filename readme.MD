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

**These rules have not been tested against the live project.** Before deploying, paste them into
the Firebase console → Firestore → Rules → Rules Playground and confirm the cases listed at the top
of the file. If they turn out too strict the quiz keeps working — the client logs a warning and
carries on — but the community counters stop moving.

Worth doing at some point: turn on [App Check](https://firebase.google.com/docs/app-check) with
reCAPTCHA v3. The rules stop a client writing *nonsense*, but nothing currently stops one writing
*a lot*, and the free tier allows 20k writes a day.
