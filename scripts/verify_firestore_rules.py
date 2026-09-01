#!/usr/bin/env python3
"""Check the DEPLOYED Firestore security rules, without changing any data.

The Rules Playground tests the rules you have pasted into the console. This
tests the rules that are actually live, from outside, with nothing but the
public web API key - the same position a student's browser (or an attacker) is
in.

Nothing is mutated. Every write probe carries a `currentDocument.updateTime`
precondition set to an impossible timestamp, so even a write the rules ALLOW
cannot commit. The rules are evaluated first, so the status code tells us the
verdict:

    403 PERMISSION_DENIED   -> the rules rejected it
    400 FAILED_PRECONDITION -> the rules allowed it, the precondition stopped it

Run it before and after `firebase deploy --only firestore:rules`:

    python3 scripts/verify_firestore_rules.py
"""

import json
import urllib.error
import urllib.parse
import urllib.request

PROJECT = "intro-psych-quiz-592fb"
# Public by design; a Firebase web API key is an identifier, not a secret.
API_KEY = "AIzaSyDdeQI0zLemr3lZRdJZbYvgh7Lh8i3xQSM"
ROOT = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents"
DOC = "questions/1"
# Long in the past, so `currentDocument.updateTime` can never match.
IMPOSSIBLE_TIME = "2001-01-01T00:00:00.000000Z"


def request(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        try:
            return error.code, json.loads(body)
        except ValueError:
            return error.code, {"raw": body[:200]}


def commit_probe(writes):
    """Issue a write that cannot possibly land, and report the rules verdict."""
    status, body = request(
        "POST",
        f"{ROOT}:commit?key={API_KEY}",
        {"writes": writes},
    )
    if status == 403:
        return "denied", body
    if status == 400 and "FAILED_PRECONDITION" in json.dumps(body):
        return "allowed", body
    return f"unexpected HTTP {status}", body


def guarded(update, fields):
    return [
        {
            "update": update,
            "updateMask": {"fieldPaths": fields},
            "currentDocument": {"updateTime": IMPOSSIBLE_TIME},
        }
    ]


def main() -> int:
    print(f"Probing the live rules on {PROJECT} (nothing is modified)\n")

    # Read the current counter so the "+1" probe is a genuine increment.
    status, doc = request("GET", f"{ROOT}/{DOC}?key={API_KEY}")
    read_ok = status == 200
    current = 0
    if read_ok:
        field = doc.get("fields", {}).get("times_answered", {})
        current = int(field.get("integerValue", 0))

    name = f"projects/{PROJECT}/databases/(default)/documents/{DOC}"

    checks = []
    checks.append(("get a question", "allowed" if read_ok else "denied", "allowed"))

    status, _ = request(
        "POST",
        f"{ROOT}:runQuery?key={API_KEY}",
        {"structuredQuery": {"from": [{"collectionId": "questions"}], "limit": 2}},
    )
    checks.append(
        ("list the whole collection", "allowed" if status == 200 else "denied", "denied")
    )

    verdict, _ = commit_probe(
        guarded(
            {"name": name, "fields": {"times_answered": {"integerValue": str(current + 1)}}},
            ["times_answered"],
        )
    )
    checks.append(("increment a counter by 1", verdict, "allowed"))

    verdict, _ = commit_probe(
        guarded(
            {"name": name, "fields": {"times_answered": {"integerValue": "999999"}}},
            ["times_answered"],
        )
    )
    checks.append(("set a counter to 999999", verdict, "denied"))

    verdict, _ = commit_probe(
        guarded(
            {"name": name, "fields": {"question_title": {"stringValue": "x"}}},
            ["question_title"],
        )
    )
    checks.append(("write an arbitrary field", verdict, "denied"))

    verdict, _ = commit_probe(
        [{"delete": name, "currentDocument": {"updateTime": IMPOSSIBLE_TIME}}]
    )
    checks.append(("delete a question", verdict, "denied"))

    failures = 0
    for label, got, want in checks:
        ok = got == want
        failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {label:28} {got:10} (want {want})")

    print()
    if failures:
        print(f"{failures} of {len(checks)} checks disagree with the intended rules.")
        print("If you have not deployed firestore.rules yet, that is expected.")
    else:
        print("All checks match firestore.rules. The database is locked down.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
