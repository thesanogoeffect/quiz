#!/usr/bin/env python3
"""Repair malformed HTML in the description_llm field of an L3 export.

The LLM occasionally emits `<pSome text</p>` (a missing `>`), which the browser
parses as a tag named `pSome` whose attributes swallow the whole sentence - the
text simply vanishes from the explanation panel. It also sometimes closes a tag
with the invalid `</>`.

Run after regenerating l3.json:

    python3 scripts/fix_l3_html.py frontend/public/l3.json
"""

import json
import re
import sys
from pathlib import Path

# `<pWord` -> `<p>Word`, and the same for the other block tags we see.
MISSING_GT = re.compile(r"<(p|div|li|ul|ol|b|i)(?=[A-Z])")
# `</>` is not a valid end tag; every occurrence in the corpus closes a <b>.
BAD_END_TAG = "</>"
# A truncated end tag such as `stereotyping</</b>` - the browser reads `</<` as
# a bogus comment and swallows the rest of the paragraph. Drop the stray opener.
TRUNCATED_END_TAG = re.compile(r"</(?=[^A-Za-z/>])")


def fix_html(text: str) -> str:
    if not text:
        return text
    fixed = MISSING_GT.sub(lambda m: f"<{m.group(1)}>", text)
    fixed = fixed.replace(BAD_END_TAG, "</b>")
    return TRUNCATED_END_TAG.sub("", fixed)


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "frontend/public/l3.json")
    questions = json.loads(path.read_text(encoding="utf-8"))

    changed = []
    for question in questions:
        original = question.get("description_llm")
        repaired = fix_html(original)
        if repaired != original:
            question["description_llm"] = repaired
            changed.append(question["id"])

    if not changed:
        print(f"{path}: nothing to fix")
        return 0

    path.write_text(
        json.dumps(questions, ensure_ascii=False, indent=None), encoding="utf-8"
    )
    print(f"{path}: repaired {len(changed)} explanations -> {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
