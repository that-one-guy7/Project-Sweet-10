#!/usr/bin/env python3
"""Read-only sanity checks for the Project Sweet-10 documentation scaffold."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    "README.md",
    "docs/feasibility.md",
    "docs/hardware-audit.md",
    "docs/boot-architecture.md",
    "docs/milestone-tracker.md",
    "research/REFERENCES.md",
]
missing = [name for name in required if not (root / name).is_file()]
if missing:
    print("Missing required files:", *missing, sep="\n- ")
    sys.exit(1)
readme = (root / "README.md").read_text(encoding="utf-8")
if "iPhone9,1" not in readme or "not ready to boot or flash" not in readme:
    print("Target or safety notice missing.")
    sys.exit(1)
print("Project Sweet-10 scaffold checks passed.")
