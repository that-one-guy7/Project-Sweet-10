#!/usr/bin/env python3
"""Compare Dyld Exports sections from saved ipsw dyld macho text logs.

The tool reads text logs only. It does not open shared caches or Mach-O
binaries, extract images, access a device, or modify input files. Export-name
similarity is not proof of implementation or ABI compatibility.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXPORT_ROW_RE = re.compile(
    r"^\s*(0x[0-9a-fA-F]+):\s*\(([^)]*)\)\s*(\S(?:.*\S)?)\s*$"
)


class ExportLogError(ValueError):
    """Raised when a saved ipsw log has no usable Dyld Exports section."""


@dataclass(frozen=True)
class ExportRow:
    """One parser-printed export row; address is cache-local metadata."""

    address: int
    kind: str
    name: str


def parse_export_log_text(text: str, source: str = "<text>") -> list[ExportRow]:
    """Parse the first non-empty Dyld Exports section in an ipsw text log."""
    lines = text.splitlines()
    heading_indices = [
        index for index, line in enumerate(lines) if line.strip() == "Dyld Exports"
    ]
    if not heading_indices:
        raise ExportLogError(f"{source}: no 'Dyld Exports' section was printed")

    rows: list[ExportRow] = []
    started = False
    for line in lines[heading_indices[0] + 1 :]:
        match = EXPORT_ROW_RE.match(line)
        if match:
            address_text, kind, name = match.groups()
            if not name:
                raise ExportLogError(f"{source}: export row has an empty symbol name")
            rows.append(ExportRow(int(address_text, 16), kind.strip(), name.strip()))
            started = True
            continue

        # ipsw prints a dashed underline below the heading; ignore pre-row
        # decoration, but terminate once the actual row block has begun.
        if started:
            break
        if not line.strip() or set(line.strip()) == {"-"}:
            continue

    if not rows:
        raise ExportLogError(
            f"{source}: 'Dyld Exports' section was present but contained no parsed rows"
        )
    return rows


def read_export_log(path: Path) -> list[ExportRow]:
    """Read and parse one UTF-8 ipsw output log."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ExportLogError(f"cannot read {path}: {exc}") from exc
    return parse_export_log_text(content, str(path))


def group_by_name(rows: Iterable[ExportRow]) -> dict[str, list[ExportRow]]:
    grouped: dict[str, list[ExportRow]] = defaultdict(list)
    for row in rows:
        grouped[row.name].append(row)
    return dict(grouped)


def _format_rows(rows: list[ExportRow]) -> str:
    values = [f"{row.kind}@0x{row.address:x}" for row in rows]
    return "[" + ", ".join(values) + "]"


def _kind_category(kind: str) -> str:
    """Normalize resolver addresses while preserving the resolver category."""
    return "resolver" if kind.startswith("resolver=") else kind


def _resolver_addresses(rows: list[ExportRow]) -> Counter[int]:
    """Return cache-local resolver addresses printed for resolver exports."""
    addresses: Counter[int] = Counter()
    for row in rows:
        if row.kind.startswith("resolver=0x"):
            try:
                addresses[int(row.kind.split("=", 1)[1], 16)] += 1
            except ValueError:
                continue
    return addresses


def _format_addresses(addresses: Counter[int]) -> str:
    return "[" + ", ".join(
        f"0x{address:x} x{count}" for address, count in sorted(addresses.items())
    ) + "]"


def compare_exports(target_rows: list[ExportRow], donor_rows: list[ExportRow]) -> str:
    """Create a deterministic summary of names, kinds, duplicates, and addresses."""
    target = group_by_name(target_rows)
    donor = group_by_name(donor_rows)
    target_names = set(target)
    donor_names = set(donor)
    common_names = target_names & donor_names
    target_only = sorted(target_names - donor_names)
    donor_only = sorted(donor_names - target_names)
    duplicate_target = sorted(name for name, entries in target.items() if len(entries) > 1)
    duplicate_donor = sorted(name for name, entries in donor.items() if len(entries) > 1)

    kind_differences: list[tuple[str, list[ExportRow], list[ExportRow]]] = []
    resolver_address_differences: list[tuple[str, Counter[int], Counter[int]]] = []
    for name in sorted(common_names):
        target_kinds = Counter(_kind_category(row.kind) for row in target[name])
        donor_kinds = Counter(_kind_category(row.kind) for row in donor[name])
        if target_kinds != donor_kinds:
            kind_differences.append((name, target[name], donor[name]))

        target_resolvers = _resolver_addresses(target[name])
        donor_resolvers = _resolver_addresses(donor[name])
        if target_resolvers and donor_resolvers and target_resolvers != donor_resolvers:
            resolver_address_differences.append((name, target_resolvers, donor_resolvers))

    address_differences = sum(
        target[name][0].address != donor[name][0].address for name in common_names
    )

    lines = [
        "Project Sweet-10: dyld export-name comparison",
        "Source: saved ipsw dyld macho --symbols -V text logs",
        "",
        f"Target export rows: {len(target_rows)}",
        f"Target unique names: {len(target_names)}",
        f"Target duplicate-name count: {len(duplicate_target)}",
        f"Donor export rows: {len(donor_rows)}",
        f"Donor unique names: {len(donor_names)}",
        f"Donor duplicate-name count: {len(duplicate_donor)}",
        f"Common unique names: {len(common_names)}",
        f"Target-only unique names: {len(target_only)}",
        f"Donor-only unique names: {len(donor_only)}",
        f"Common names with differing export-kind categories: {len(kind_differences)}",
        f"Common resolver names with different printed resolver addresses: {len(resolver_address_differences)}",
        f"Common names with different first printed export addresses: {address_differences}",
        "",
        "Target-only export names:",
    ]
    lines.extend(
        f"  {name}: {_format_rows(target[name])}" for name in target_only
    )
    if not target_only:
        lines.append("  (none)")

    lines.append("\nDonor-only export names:")
    lines.extend(f"  {name}: {_format_rows(donor[name])}" for name in donor_only)
    if not donor_only:
        lines.append("  (none)")

    lines.append("\nCommon names with differing export-kind categories:")
    lines.extend(
        f"  {name}: target={_format_rows(left)}; donor={_format_rows(right)}"
        for name, left, right in kind_differences
    )
    if not kind_differences:
        lines.append("  (none)")

    lines.append("\nCommon resolver names with different printed resolver addresses:")
    lines.extend(
        f"  {name}: target={_format_addresses(left)}; donor={_format_addresses(right)}"
        for name, left, right in resolver_address_differences
    )
    if not resolver_address_differences:
        lines.append("  (none)")

    lines.extend(
        [
            "",
            "Duplicate names (target): " + (", ".join(duplicate_target) or "(none)"),
            "Duplicate names (donor): " + (", ".join(duplicate_donor) or "(none)"),
            "",
            "Interpretation limits:",
            "- Export names and parser-printed kinds describe metadata, not implementations.",
            "- Addresses are cache-local and are not compared as compatibility evidence.",
            "- A missing section or malformed log is an evidence/parser error, not an empty export set.",
            "- This report does not establish ABI, dependency resolution, runtime loading,",
            "  IOKit attachment, hardware behavior, kernel boot, or SpringBoard.",
            "- No binary, cache, device, firmware, partition, or boot state was modified.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare export names and parser-printed kinds from two saved "
            "ipsw dyld macho --symbols -V logs."
        )
    )
    parser.add_argument("--target", required=True, type=Path, help="target parser log")
    parser.add_argument("--donor", required=True, type=Path, help="donor parser log")
    args = parser.parse_args(argv)

    try:
        target_rows = read_export_log(args.target)
        donor_rows = read_export_log(args.donor)
    except ExportLogError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(compare_exports(target_rows, donor_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
