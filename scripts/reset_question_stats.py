#!/usr/bin/env python3
"""Reset the community counters of questions whose correct answer changed.

After a review re-keys a question, its Firestore stats (times answered
correctly, votes, flags) describe the OLD key, and the app would keep showing
students a misleading "x% got this right". This resets every counter of each
question listed in a review file whose `correct_answer` was changed, and the
votes/flags of every other fixed question. Disabled questions are left alone.

Needs firebase_credentials.json in the working directory (a service-account
key; it bypasses the security rules). Back the counters up first:

    python3 scripts/backup_firestore_stats.py
    python3 scripts/reset_question_stats.py data/question_review_2026-09.json --dry-run
    python3 scripts/reset_question_stats.py data/question_review_2026-09.json
"""

import argparse
import json
from pathlib import Path

ALL_COUNTERS = {
    "times_asked": 0,
    "times_answered": 0,
    "times_answered_correct": 0,
    "times_skipped": 0,
    "times_flagged": 0,
    "times_upvoted": 0,
    "times_downvoted": 0,
}
FEEDBACK_COUNTERS = {"times_flagged": 0, "times_upvoted": 0, "times_downvoted": 0}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("review", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    findings = json.loads(args.review.read_text(encoding="utf-8"))
    # A key that changed meaning invalidates the answer history. A typo fix or a
    # chapter move with a wording tweak does not, so those keep their counters.
    def rekeyed_meaning(f):
        return "correct_answer" in f.get("changes", {}) and f.get("problem") not in ("typo", "off_topic")

    fixes = [f for f in findings if f["verdict"] == "fix"]
    rekeyed = sorted(f["id"] for f in fixes if rekeyed_meaning(f))
    fixed = sorted(f["id"] for f in fixes if not rekeyed_meaning(f))
    print(f"{len(rekeyed)} re-keyed questions: all counters -> 0")
    print(f"{len(fixed)} other fixed questions: flags and votes -> 0")
    if args.dry_run:
        print("re-keyed:", rekeyed)
        return

    import firebase_admin
    from firebase_admin import credentials, firestore

    firebase_admin.initialize_app(credentials.Certificate("firebase_credentials.json"))
    questions = firestore.client().collection("questions")
    batch = firestore.client().batch()
    n = 0
    for qid, values in [(q, ALL_COUNTERS) for q in rekeyed] + [(q, FEEDBACK_COUNTERS) for q in fixed]:
        batch.update(questions.document(str(qid)), values)
        n += 1
        if n % 400 == 0:  # Firestore batches hold at most 500 writes
            batch.commit()
            batch = firestore.client().batch()
    batch.commit()
    print(f"updated {n} documents")


if __name__ == "__main__":
    main()
