#!/usr/bin/env python3
"""Apply a question-review findings file to the shipped question set.

A findings file is a JSON array of entries shaped like

    {"id": 460, "verdict": "fix" | "disable", "problem": "...", "reason": "...",
     "confidence": "high" | "medium",
     "changes": {"question_title": ..., "correct_answer": ..., "distractor_1": ...,
                 "distractor_2": ..., "distractor_3": ..., "description_llm": ...}}

`fix` overwrites just the listed fields (`changes` may also carry an integer
`chapter_id` to move a misfiled question); `disable` sets is_disabled to "1" so
the app hides the question without losing it. Everything is validated before the
file is written: unknown ids, empty or duplicate options, and explanation markup
the build would reject all abort the run.

    python3 scripts/apply_question_review.py data/question_review_2026-09.json
    python3 scripts/apply_question_review.py findings.json --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_FIELDS = (
    "question_title",
    "correct_answer",
    "distractor_1",
    "distractor_2",
    "distractor_3",
    "description_llm",
)
OPTION_FIELDS = TEXT_FIELDS[1:5]
ALLOWED_TAGS = {"div", "p", "b", "i", "ul", "li", "br", "strong", "em"}
# Same pattern scripts/build_site.sh rejects.
BROKEN_MARKUP = re.compile(r"<p[A-Za-z]|</(?![A-Za-z]|>)")


def validate_question(q):
    options = [str(q.get(f) or "").strip() for f in OPTION_FIELDS]
    if any(not o for o in options):
        raise ValueError(f"id {q['id']}: an option is empty")
    if len({o.lower().rstrip(".") for o in options}) < 4:
        raise ValueError(f"id {q['id']}: options are not distinct: {options}")
    if not str(q.get("question_title") or "").strip():
        raise ValueError(f"id {q['id']}: empty question_title")
    html = str(q.get("description_llm") or "")
    if BROKEN_MARKUP.search(html):
        raise ValueError(f"id {q['id']}: malformed explanation markup")
    tags = {t.lower() for t in re.findall(r"</?\s*([A-Za-z][A-Za-z0-9]*)", html)}
    if tags - ALLOWED_TAGS:
        raise ValueError(f"id {q['id']}: explanation uses tags {sorted(tags - ALLOWED_TAGS)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("findings", type=Path)
    ap.add_argument("--json", type=Path, default=Path("frontend/public/l3.json"))
    ap.add_argument("--dry-run", action="store_true", help="report, but do not write")
    args = ap.parse_args()

    questions = json.loads(args.json.read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in questions}
    findings = json.loads(args.findings.read_text(encoding="utf-8"))

    seen = set()
    fixed = disabled = 0
    for f in findings:
        qid = f["id"]
        if qid in seen:
            sys.exit(f"id {qid} appears twice in the findings")
        seen.add(qid)
        q = by_id.get(qid)
        if q is None:
            sys.exit(f"id {qid} is not in {args.json}")

        if f["verdict"] == "disable":
            q["is_disabled"] = "1"
            disabled += 1
            continue
        if f["verdict"] != "fix":
            sys.exit(f"id {qid}: unknown verdict {f['verdict']!r}")

        changes = f.get("changes") or {}
        unknown = set(changes) - set(TEXT_FIELDS) - {"chapter_id"}
        if unknown:
            sys.exit(f"id {qid}: cannot change {sorted(unknown)}")
        if not changes:
            sys.exit(f"id {qid}: verdict is fix but there are no changes")
        for field, value in changes.items():
            if field == "chapter_id":
                if not isinstance(value, int) or not 1 <= value <= 16:
                    sys.exit(f"id {qid}: chapter_id must be an integer from 1 to 16")
                q[field] = value
                continue
            if not isinstance(value, str):
                sys.exit(f"id {qid}: {field} must be a string")
            q[field] = value.strip()
        try:
            validate_question(q)
        except ValueError as e:
            sys.exit(str(e))
        fixed += 1

    print(f"{fixed} fixed, {disabled} disabled, {len(questions) - len(seen)} untouched")
    if args.dry_run:
        return
    args.json.write_text(json.dumps(questions, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
