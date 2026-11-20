#!/usr/bin/env python3
"""Read-only verification of a local PongoOS checkout against the project source lock."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "pongo" / "BASELINE.lock.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_REPOSITORY = "checkra1n/PongoOS"


def load_lock():
    """Load and validate the pinned upstream identity."""
    if not LOCK.is_file():
        raise ValueError(f"Missing source lock: {LOCK}")
    try:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read source lock: {exc}") from exc

    if lock.get("repository") != EXPECTED_REPOSITORY:
        raise ValueError(
            f"Invalid repository in source lock; expected {EXPECTED_REPOSITORY}."
        )
    expected = lock.get("commit_sha")
    if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
        raise ValueError(
            "Invalid or missing commit_sha in PongoOS source lock "
            "(expected 40 lowercase hex characters)."
        )
    return lock


def verify_checkout(checkout, expected):
    """Return True only when checkout HEAD matches the supplied full Git SHA."""
    checkout = Path(checkout).resolve()
    if not checkout.is_dir() or not (checkout / ".git").exists():
        print(f"Not a Git checkout: {checkout}")
        return False
    if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
        print("Invalid expected commit SHA.")
        return False

    try:
        actual = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.output.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        print(f"Cannot read PongoOS checkout revision: {detail}")
        return False

    print(f"Expected PongoOS commit: {expected}")
    print(f"Actual PongoOS commit:   {actual}")
    if actual != expected:
        print("FAIL: checkout does not match the pinned PongoOS commit.")
        return False
    print("PASS: checkout matches the pinned PongoOS source commit.")
    print("NOTE: source identity does not prove iPhone9,1 runtime compatibility.")
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 tools/verify_pongo_source.py PATH_TO_PONGOOS_CHECKOUT")
        return 2
    try:
        lock = load_lock()
    except ValueError as exc:
        print(exc)
        return 1
    return 0 if verify_checkout(sys.argv[1], lock["commit_sha"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
