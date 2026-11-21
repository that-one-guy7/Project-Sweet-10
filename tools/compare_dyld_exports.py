#!/usr/bin/env python3
"""Compare dyld export-trie names and kinds from saved ipsw text logs.

This is a host-side text parser. It reads saved parser output only; it does
not open shared caches, extract Mach-O files, load code, or contact devices.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


EXPORT_HEADER = "Dyld Exports"
EXPORT_ROW = re.compile(
    r"^\s*(0x[0-9a-fA-F]+):\s+\(([^)]+)\)\s+(.+?)\s*$"
)


class ExportAuditError(ValueError):
    """Raised when a saved ipsw log has no usable Dyld Exports section."""


@dataclass(frozen=True)
class ExportRecord:
    address: str
    kind: str
    name: str


def parse_export_log(path: Path) -> list[ExportRecord]:
    """Read the first ipsw `Dyld Exports` section in a saved parser log.

    Addresses are retained in records for source-specific reference only;
    the comparison below intentionally ignores them.
    """
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ExportAuditError(f"cannot read {path}: {exc}") from exc

    try:
        start = next(
            i for i, line in enumerate(lines)
            if line.strip() == EXPORT_HEADER
        )
    except StopIteration as exc:
        raise ExportAuditError(
            f"{path}: no `{EXPORT_HEADER}` section; "
            "this is not an empty-export result"
        ) from exc

    records: list[ExportRecord] = []
    saw_row = False
    for line in lines[start + 1 :]:
        if not line.strip():
            if saw_row:
                break
            continue
        if set(line.strip()) == {"-"}:
            continue

        match = EXPORT_ROW.match(line)
        if match:
            address, kind, name = match.groups()
            records.append(
                ExportRecord(address=address, kind=kind, name=name)
            )
            saw_row = True
        elif saw_row:
            break
        # Ignore only preamble before the first row (normally the underline).

    if not records:
        raise ExportAuditError(
            f"{path}: found `{EXPORT_HEADER}` but parsed no rows; preserve "
            "this as an unresolved parser/output case rather than treating "
            "it as no exports"
        )
    return records


def _names_with_duplicates(counts: Counter[str]) -> list[str]:
    return sorted(name for name, count in counts.items() if count > 1)


def compare_exports(
    target: list[ExportRecord],
    donor: list[ExportRecord],
    pair_label: str,
) -> str:
    """Return an exact multiset comparison of export names and kinds."""
    target_typed = Counter((row.name, row.kind) for row in target)
    donor_typed = Counter((row.name, row.kind) for row in donor)
    target_name_counts = Counter(row.name for row in target)
    donor_name_counts = Counter(row.name for row in donor)

    target_names = set(target_name_counts)
    donor_names = set(donor_name_counts)
    common_names = target_names & donor_names

    target_only = sorted(target_names - donor_names)
    donor_only = sorted(donor_names - target_names)
    kind_differences = []
    target_kinds_by_name: dict[str, set[str]] = {}
    donor_kinds_by_name: dict[str, set[str]] = {}
    for row in target:
        target_kinds_by_name.setdefault(row.name, set()).add(row.kind)
    for row in donor:
        donor_kinds_by_name.setdefault(row.name, set()).add(row.kind)
    for name in sorted(common_names):
        target_kinds = sorted(target_kinds_by_name[name])
        donor_kinds = sorted(donor_kinds_by_name[name])
        if target_kinds != donor_kinds:
            kind_differences.append((name, target_kinds, donor_kinds))

    target_only_typed = sorted((target_typed - donor_typed).items())
    donor_only_typed = sorted((donor_typed - target_typed).items())

    lines = [
        f"Export comparison: {pair_label}",
        f"Target export rows: {len(target)}",
        f"Target unique names: {len(target_names)}",
        "Target duplicate names: "
        + (", ".join(_names_with_duplicates(target_name_counts)) or "(none)"),
        f"Donor export rows: {len(donor)}",
        f"Donor unique names: {len(donor_names)}",
        "Donor duplicate names: "
        + (", ".join(_names_with_duplicates(donor_name_counts)) or "(none)"),
        f"Common unique names: {len(common_names)}",
        f"Target-only names: {', '.join(target_only) or '(none)'}",
        f"Donor-only names: {', '.join(donor_only) or '(none)'}",
        "Names with differing export kinds:",
    ]
    if kind_differences:
        for name, target_kinds, donor_kinds in kind_differences:
            lines.append(
                f"  {name}: target={','.join(target_kinds)}; "
                f"donor={','.join(donor_kinds)}"
            )
    else:
        lines.append("  (none)")

    lines.append("Target-only typed rows:")
    if target_only_typed:
        lines.extend(
            f"  ({kind}) {name} x{count}"
            for (name, kind), count in target_only_typed
        )
    else:
        lines.append("  (none)")

    lines.append("Donor-only typed rows:")
    if donor_only_typed:
        lines.extend(
            f"  ({kind}) {name} x{count}"
            for (name, kind), count in donor_only_typed
        )
    else:
        lines.append("  (none)")

    lines.extend(
        [
            "",
            "Addresses were deliberately excluded from comparison because cache layouts differ.",
            "Matching names/kinds do not prove implementation, ABI, runtime, or hardware compatibility.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare Dyld Exports sections from saved ipsw parser logs."
    )
    parser.add_argument("--target", required=True, type=Path, help="19H422 export log")
    parser.add_argument("--donor", required=True, type=Path, help="20H392 export log")
    parser.add_argument("--pair", default="target versus donor", help="image pair label")
    args = parser.parse_args()

    try:
        target = parse_export_log(args.target)
        donor = parse_export_log(args.donor)
    except ExportAuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(compare_exports(target, donor, args.pair))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
