#!/usr/bin/env python3
"""Replace the `author` student numbers in an L3 export with salted hashes.

The published l3.json is downloadable by anyone at /ipt/l3.json, and the raw
`author` values are TU/e student numbers - directly re-identifiable personal
data. Hashing keeps "same author" groupable (useful in the dashboard) without
publishing the identifier.

The salt MUST stay secret. A bare hash of a 7-9 digit number is trivially
brute-forced: the whole keyspace is a few hundred million SHA-256 calls. With a
secret salt it is not.

The salt is read from, in order:
  1. the QUIZ_AUTHOR_SALT environment variable
  2. .author_salt in the repo root (gitignored, created on first run)

Keep .author_salt backed up somewhere safe - lose it and the hashes from a later
pipeline run will not match the ones already published.

Usage:
    python3 scripts/anonymize_authors.py frontend/public/l3.json
    python3 scripts/anonymize_authors.py frontend/public/l3.json --check
"""

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SALT_FILE = REPO_ROOT / ".author_salt"
# What this script produces, so a second run is a no-op.
HASHED = re.compile(r"^s-[0-9a-f]{10}$")


def load_salt() -> str:
    env_salt = os.environ.get("QUIZ_AUTHOR_SALT")
    if env_salt:
        return env_salt

    if SALT_FILE.exists():
        salt = SALT_FILE.read_text(encoding="utf-8").strip()
        if salt:
            return salt

    salt = secrets.token_hex(32)
    SALT_FILE.write_text(salt + "\n", encoding="utf-8")
    SALT_FILE.chmod(0o600)
    print(f"Generated a new salt at {SALT_FILE} - back this up, and never commit it.")
    return salt


def hash_author(author: str, salt: str) -> str:
    digest = hmac.new(salt.encode(), str(author).strip().encode(), hashlib.sha256)
    return f"s-{digest.hexdigest()[:10]}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="frontend/public/l3.json")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if any raw student number is still present",
    )
    args = parser.parse_args()

    path = Path(args.path)
    questions = json.loads(path.read_text(encoding="utf-8"))

    raw = [
        q["id"]
        for q in questions
        if q.get("author") and not HASHED.match(str(q["author"]).strip())
    ]

    if args.check:
        if raw:
            print(f"{path}: {len(raw)} un-hashed authors, e.g. question {raw[:5]}")
            return 1
        print(f"{path}: all authors are hashed")
        return 0

    if not raw:
        print(f"{path}: already anonymised, nothing to do")
        return 0

    salt = load_salt()
    for question in questions:
        author = question.get("author")
        if author and not HASHED.match(str(author).strip()):
            question["author"] = hash_author(author, salt)

    path.write_text(
        json.dumps(questions, ensure_ascii=False, indent=None), encoding="utf-8"
    )
    distinct = len({q["author"] for q in questions if q.get("author")})
    print(f"{path}: hashed {len(raw)} authors into {distinct} distinct tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
