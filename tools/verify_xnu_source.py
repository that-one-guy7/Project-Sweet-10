#!/usr/bin/env python3
"""Read-only verification of a local XNU checkout against the project source lock."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "xnu" / "BASELINE.lock.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 tools/verify_xnu_source.py PATH_TO_XNU_CHECKOUT")
        return 2
    checkout = Path(sys.argv[1]).resolve()
    if not LOCK.is_file():
        print(f"Missing source lock: {LOCK}")
        return 1
    if not (checkout / ".git").exists():
        print(f"Not a Git checkout: {checkout}")
        return 1

    try:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read source lock: {exc}")
        return 1

    expected = lock.get("commit_sha")
    if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
        print("Invalid or missing commit_sha in source lock (expected 40 lowercase hex characters).")
        return 1

    try:
        actual = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as exc:
        print(f"Cannot read XNU checkout revision: {exc.output.strip()}")
        return 1

    print(f"Expected XNU commit: {expected}")
    print(f"Actual XNU commit:   {actual}")
    if actual != expected:
        print("FAIL: checkout does not match the pinned XNU commit.")
        return 1
    print("PASS: checkout matches the pinned source commit.")
    print("NOTE: source identity does not prove iPhone9,1 support or a kernel build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
