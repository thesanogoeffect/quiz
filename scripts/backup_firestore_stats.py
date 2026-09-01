#!/usr/bin/env python3
"""Back up the per-question counters from Firestore to a local JSON file.

These counters are the only thing in this project that cannot be regenerated:
the questions come from the pipeline, the app is in git, but two years of
students answering questions exists nowhere else. Run this before touching the
security rules, before any migration, and every so often anyway.

Uses the public web API key and the REST API, so it needs no admin credentials
and no extra dependencies - reading a question document is allowed by the
security rules.

    python3 scripts/backup_firestore_stats.py                     # -> data/firestore-backup-<date>.json
    python3 scripts/backup_firestore_stats.py --out somewhere.json
    python3 scripts/backup_firestore_stats.py --summary           # totals only, no file

The deployed rules set `allow list: if false`, so this cannot page through the
collection. It fetches documents by name with `:batchGet` instead, which the
rules evaluate as `get` - allowed. Ids are contiguous from 1, so it walks the
range and stops once it has seen a long enough run of absent ids.
"""

import argparse
import datetime
import json
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = "intro-psych-quiz-592fb"
# Public by design - a Firebase web API key identifies the project, it is not a
# secret. Access is governed by the security rules.
API_KEY = "AIzaSyDdeQI0zLemr3lZRdJZbYvgh7Lh8i3xQSM"
ROOT = (
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}"
    "/databases/(default)/documents"
)
# Fully-qualified document names, as :batchGet wants them.
DOC_ROOT = f"projects/{PROJECT}/databases/(default)/documents"
COUNTERS = [
    "times_asked",
    "times_answered",
    "times_answered_correct",
    "times_skipped",
    "times_flagged",
    "times_upvoted",
    "times_downvoted",
]


def value_of(field):
    """Unwrap a Firestore REST typed value."""
    if "integerValue" in field:
        return int(field["integerValue"])
    if "doubleValue" in field:
        return float(field["doubleValue"])
    if "stringValue" in field:
        return field["stringValue"]
    if "booleanValue" in field:
        return field["booleanValue"]
    return None


# How many consecutive absent ids to tolerate before deciding we are past the
# end of the collection. Comfortably larger than any gap the pipeline leaves.
STRIDE = 200
GIVE_UP_AFTER = 400


def batch_get(ids):
    """Fetch questions by id. Governed by `allow get`, not `allow list`."""
    payload = {"documents": [f"{DOC_ROOT}/questions/{i}" for i in ids]}
    request = urllib.request.Request(
        f"{ROOT}:batchGet?key={API_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            entries = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 403:
            raise SystemExit(
                "Firestore refused the read (HTTP 403).\n"
                "The rules allow `get` on questions/{id}, so this should work with\n"
                "no credentials. Check that firestore.rules is still deployed:\n"
                "    python3 scripts/verify_firestore_rules.py"
            ) from error
        raise SystemExit(
            f"Firestore returned HTTP {error.code}: {error.read().decode()[:300]}"
        ) from error
    return [entry["found"] for entry in entries if "found" in entry]


def fetch_all():
    documents = []
    start = 1
    misses = 0
    while misses < GIVE_UP_AFTER:
        found = batch_get(range(start, start + STRIDE))
        documents += found
        # A whole stride with nothing in it means we are probably past the end;
        # keep going a little in case the pipeline left a gap.
        misses = 0 if found else misses + STRIDE
        start += STRIDE
    return documents


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="where to write the backup")
    parser.add_argument(
        "--summary", action="store_true", help="print totals instead of writing a file"
    )
    args = parser.parse_args()

    documents = fetch_all()
    stats = {}
    for document in documents:
        doc_id = document["name"].rsplit("/", 1)[-1]
        fields = document.get("fields", {})
        stats[doc_id] = {key: value_of(value) for key, value in fields.items()}

    totals = {
        counter: sum(row.get(counter) or 0 for row in stats.values())
        for counter in COUNTERS
    }

    print(f"{len(stats)} question documents")
    for counter in COUNTERS:
        print(f"  {counter:24} {totals[counter]:>10,}")

    if args.summary:
        return 0

    default = (
        Path("data")
        / f"firestore-backup-{datetime.date.today().isoformat()}.json"
    )
    out = Path(args.out) if args.out else default
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "project": PROJECT,
                "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "document_count": len(stats),
                "totals": totals,
                "questions": stats,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nwrote {out} ({out.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
