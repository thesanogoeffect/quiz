#!/usr/bin/env bash
#
# Scrub TU/e student numbers out of the git history, so this repository can be
# made public.
#
# The working tree is already clean - scripts/anonymize_authors.py replaced the
# `author` values in frontend/public/l3.json with salted hashes. But the raw
# numbers are still in old commits:
#
#   frontend/public/l3.json   "author":"1727427"      (commits 184ffcb, 9ed14d8)
#   data/l3.csv               ,1727427,               (commit 9ed14d8)
#   dashboard/l3.csv          ,1727427,               (commit 2399716)
#   data/l2.db                SQLite rows             (commit 9ed14d8)
#
# THIS REWRITES HISTORY. Every commit hash after the first affected commit
# changes, so it needs a force-push and everyone with a clone must re-clone.
# Run it on a FRESH CLONE, check the result, then force-push.
#
#   git clone git@github.com:thesanogoeffect/quiz.git quiz-clean
#   cd quiz-clean
#   ../quiz/scripts/purge_student_numbers_from_history.sh --yes
#
# Requires git-filter-repo:  pipx install git-filter-repo   (or pip install --user)
#
# AFTERWARDS, and before making the repo public:
#   - Ask GitHub Support to purge cached views of the old commits. Force-pushing
#     does NOT remove blobs that are already reachable by hash on github.com.
#   - Check for forks. A fork keeps its own copy of the old objects.
#   - Rotate nothing else - the Firebase web key in the repo is public by design.

set -euo pipefail

if [[ "${1:-}" != "--yes" ]]; then
  echo "This rewrites git history. Re-run with --yes once you have read the header." >&2
  exit 1
fi

if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "git-filter-repo not found. Install it with: pipx install git-filter-repo" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is dirty. Run this on a clean, fresh clone." >&2
  exit 1
fi

echo "==> Dropping the working-data files from every commit"
# These are pipeline scratch files, not app data - they should never have been
# committed, and nothing in frontend/ reads them.
git filter-repo --force \
  --path data/l2.db \
  --path data/l3.csv \
  --path dashboard/l3.csv \
  --path data/l3.json \
  --invert-paths

echo "==> Redacting author numbers inside the historical l3.json blobs"
# frontend/public/l3.json has to stay - it is the question set the app loads -
# so redact the field instead of deleting the file.
REPLACEMENTS="$(mktemp)"
trap 'rm -f "$REPLACEMENTS"' EXIT
cat >"$REPLACEMENTS" <<'EOF'
regex:"author"\s*:\s*"[0-9]{5,10}"==>"author": "redacted"
EOF
git filter-repo --force --replace-text "$REPLACEMENTS"

echo
echo "==> Verifying no raw student numbers remain in any reachable blob"
if git rev-list --all --objects \
  | awk '{print $1}' \
  | git cat-file --batch-check='%(objecttype) %(objectname)' \
  | awk '$1=="blob"{print $2}' \
  | while read -r blob; do git cat-file blob "$blob"; done \
  | grep -qE '"author"\s*:\s*"[0-9]{5,10}"'; then
  echo "STILL FOUND raw author numbers - do not publish. Investigate before pushing." >&2
  exit 1
fi
echo "Clean."

cat <<'EOF'

Next steps (nothing has been pushed):
  1. git log --stat        # sanity-check the rewritten history
  2. git remote add origin git@github.com:thesanogoeffect/quiz.git
  3. git push --force --all && git push --force --tags
  4. Contact GitHub Support to purge cached views of the old commit hashes
  5. Only then flip the repository to public
EOF
