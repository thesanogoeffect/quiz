#!/usr/bin/env python3
"""Point at the questions most likely to be wrong, using community stats.

Below-chance correct rates and heavy flagging turned out to be a reliable
signal during the September 2026 review (see data/question_review_2026-09.json
and README.md): 99 of the 136 questions this triage flagged needed a real fix.
Re-run it whenever frontend/public/stats.json is refreshed with a new season
of answers, to find what is worth a look before the next review pass.

    python3 scripts/triage_questions.py                    # top 40 by score
    python3 scripts/triage_questions.py --min-n 50 --top 80
    python3 scripts/triage_questions.py --chapter 7
"""

import argparse
import json
from pathlib import Path


def score(stats):
    """Higher = more likely to need a look. Same weights as the review rubric."""
    n = stats["times_answered"]
    if n == 0:
        return 0.0
    rate = stats["times_answered_correct"] / n
    points = 3 if rate < 0.35 else 2 if rate < 0.45 else 1 if rate < 0.55 else 0
    points += min(stats["times_flagged"], 10) / 2
    points += max(0, stats["times_downvoted"] - stats["times_upvoted"]) / 2
    return points


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--questions", type=Path, default=Path("frontend/public/l3.json"))
    ap.add_argument("--stats", type=Path, default=Path("frontend/public/stats.json"))
    ap.add_argument("--min-n", type=int, default=30, help="ignore questions answered fewer times than this")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--chapter", type=int, help="restrict to one chapter id")
    args = ap.parse_args()

    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    stats = json.loads(args.stats.read_text(encoding="utf-8"))["questions"]

    rows = []
    for q in questions:
        if str(q.get("is_disabled")).strip().lower() in ("1", "true", "yes"):
            continue
        if args.chapter is not None and q["chapter_id"] != args.chapter:
            continue
        s = stats.get(str(q["id"]))
        if not s or s["times_answered"] < args.min_n:
            continue
        rows.append((score(s), q, s))

    rows.sort(key=lambda r: -r[0])
    for sc, q, s in rows[: args.top]:
        if sc <= 0:
            break
        n, correct = s["times_answered"], s["times_answered_correct"]
        print(
            f"{sc:4.1f}  id={q['id']:<5} ch={q['chapter_id']:<2} rate={correct/n:.2f} "
            f"n={n:<4} flag={s['times_flagged']:<3} up={s['times_upvoted']:<3} "
            f"down={s['times_downvoted']:<3} {q['source']:<22} {q['question_title'][:70]}"
        )


if __name__ == "__main__":
    main()
