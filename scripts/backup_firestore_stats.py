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

Note: listing the collection is what the *current* rules allow. The rules in
firestore.rules set `allow list: if false`, so after deploying them this script
needs an admin credential (see scripts/firestore.py) or must fetch documents by
id one at a time.
"""

import argparse
import datetime
import json
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT = "intro-psych-quiz-592fb"
# Public by design - a Firebase web API key identifies the project, it is not a
# secret. Access is governed by the security rules.
API_KEY = "AIzaSyDdeQI0zLemr3lZRdJZbYvgh7Lh8i3xQSM"
BASE = (
    f"https://firestore.googleapis.com/v1/projects/{PROJECT}"
    "/databases/(default)/documents/questions"
)
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


def fetch_all():
    documents = []
    token = None
    while True:
        params = {"pageSize": "300", "key": API_KEY}
        if token:
            params["pageToken"] = token
        url = f"{BASE}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=60) as response:
            page = json.load(response)
        documents += page.get("documents", [])
        token = page.get("nextPageToken")
        if not token:
            break
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
