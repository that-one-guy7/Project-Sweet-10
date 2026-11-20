#!/usr/bin/env python3
"""Read-only verification of a local XNU checkout against the project source lock."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "xnu" / "BASELINE.lock.json"


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

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    expected = lock["commit_sha"]
    actual = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()
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
