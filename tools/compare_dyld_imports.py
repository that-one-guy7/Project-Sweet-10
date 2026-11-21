#!/usr/bin/env python3
"""Check saved undefined imports against exports of named provider logs.

This host-side tool reads only saved ipsw text output. It compares exact
symbol names within the provider label printed beside each undefined import.
A name found in a saved provider export list is static metadata only; it does
not prove dyld fixups, ABI compatibility, runtime resolution, or loading.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:  # Works both as "python3 tools/..." and as a package import in tests.
    from tools.compare_dyld_exports import ExportLogError, read_export_log
except ModuleNotFoundError:  # Direct script execution: sibling module is on sys.path.
    from compare_dyld_exports import ExportLogError, read_export_log


IMPORT_ROW_RE = re.compile(
    r"^\s*\(undefined\)\s+"
    r"(external|weak external(?: automatically hidden)?)\s+"
    r"(\S+)\s+\(from\s+(.+?)\)\s*$"
)


class ImportLogError(ValueError):
    """Raised when a saved ipsw log lacks a parseable Symtab section."""


@dataclass(frozen=True)
class ImportRow:
    """One parser-printed undefined import and its provider label."""

    name: str
    provider: str
    kind: str


def parse_import_log_text(text: str, source: str = "<text>") -> list[ImportRow]:
    """Parse undefined import rows from the Symtab section of an ipsw log."""
    lines = text.splitlines()
    headings = [i for i, line in enumerate(lines) if line.strip() == "Symtab"]
    if not headings:
        raise ImportLogError(f"{source}: no 'Symtab' section was printed")

    start = headings[0] + 1
    end = next(
        (i for i in range(start, len(lines)) if lines[i].strip() == "Dyld Exports"),
        len(lines),
    )
    rows: list[ImportRow] = []
    for line_number, line in enumerate(lines[start:end], start=start + 1):
        if "(undefined)" not in line:
            continue
        match = IMPORT_ROW_RE.match(line)
        if not match:
            raise ImportLogError(
                f"{source}:{line_number}: malformed undefined-import row"
            )
        kind, name, provider = match.groups()
        rows.append(ImportRow(name=name, provider=provider, kind=kind))
    return rows


def read_import_log(path: Path) -> list[ImportRow]:
    """Read and parse one UTF-8 ipsw text log."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ImportLogError(f"cannot read {path}: {exc}") from exc
    return parse_import_log_text(content, str(path))


def parse_provider_specs(specs: Iterable[str], option: str) -> dict[str, Path]:
    """Parse repeated PROVIDER=PATH command-line values, rejecting duplicates."""
    providers: dict[str, Path] = {}
    for spec in specs:
        provider, separator, filename = spec.partition("=")
        if not separator or not provider.strip() or not filename.strip():
            raise ImportLogError(f"{option}: expected PROVIDER=PATH, got {spec!r}")
        provider = provider.strip()
        if provider in providers:
            raise ImportLogError(f"{option}: duplicate provider {provider!r}")
        providers[provider] = Path(filename.strip())
    return providers


def _provider_imports(rows: list[ImportRow]) -> dict[str, list[ImportRow]]:
    grouped: dict[str, list[ImportRow]] = defaultdict(list)
    for row in rows:
        grouped[row.provider].append(row)
    return dict(grouped)


def compare_build(
    label: str,
    consumer_path: Path,
    provider_paths: dict[str, Path],
) -> str:
    """Build a deterministic provider-by-provider static name-match report."""
    imports = read_import_log(consumer_path)
    imports_by_provider = _provider_imports(imports)

    normal_count = sum(row.kind == "external" for row in imports)
    weak_count = len(imports) - normal_count
    assessed_rows = 0
    matched_unique = 0
    checked_unique = 0
    lines = [
        label,
        f"Consumer log: {consumer_path}",
        f"Undefined import rows: {len(imports)} ({normal_count} normal, {weak_count} weak)",
    ]

    all_providers = sorted(set(imports_by_provider) | set(provider_paths))
    for provider in all_providers:
        rows = imports_by_provider.get(provider, [])
        import_names = {row.name for row in rows}
        if provider not in provider_paths:
            if rows:
                names_preview = ", ".join(sorted(import_names)[:8])
                suffix = " ..." if len(import_names) > 8 else ""
                lines.append(
                    f"{provider}: NOT ASSESSED (no provider export log; "
                    f"{len(rows)} import rows / {len(import_names)} unique names; "
                    f"sample: {names_preview}{suffix})"
                )
            continue

        try:
            export_rows = read_export_log(provider_paths[provider])
        except ExportLogError as exc:
            raise ImportLogError(str(exc)) from exc
        export_names = {row.name for row in export_rows}
        matched = import_names & export_names
        missing = sorted(import_names - export_names)
        assessed_rows += len(rows)
        checked_unique += len(import_names)
        matched_unique += len(matched)
        lines.append(
            f"{provider}: import_rows={len(rows)}, "
            f"unique_imports={len(import_names)}, export_rows={len(export_rows)}, "
            f"unique_exports={len(export_names)}, "
            f"exact_name_matches={len(matched)}, "
            f"not_in_saved_exports={len(missing)}"
        )
        if missing:
            lines.append("  Not found in saved provider export list:")
            lines.extend(f"    {name}" for name in missing)

    lines.extend(
        [
            f"Provider-assessed import rows: {assessed_rows}/{len(imports)}",
            f"Provider-assessed unique import names: {checked_unique}",
            f"Exact matches among assessed unique imports: {matched_unique}/{checked_unique}",
            f"Unassessed import rows: {len(imports) - assessed_rows}",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check undefined imports in saved ipsw Symtab logs against "
            "provider-specific Dyld Exports logs."
        )
    )
    parser.add_argument("--target-consumer", required=True, type=Path)
    parser.add_argument("--donor-consumer", required=True, type=Path)
    parser.add_argument(
        "--target-provider", action="append", default=[], metavar="PROVIDER=PATH",
        help="target-build provider export log (repeat for each provider)",
    )
    parser.add_argument(
        "--donor-provider", action="append", default=[], metavar="PROVIDER=PATH",
        help="donor-build provider export log (repeat for each provider)",
    )
    args = parser.parse_args(argv)

    try:
        target_providers = parse_provider_specs(args.target_provider, "--target-provider")
        donor_providers = parse_provider_specs(args.donor_provider, "--donor-provider")
        if not target_providers and not donor_providers:
            raise ImportLogError("at least one target or donor provider log is required")
        target_report = compare_build("TARGET", args.target_consumer, target_providers)
        donor_report = compare_build("DONOR", args.donor_consumer, donor_providers)
    except (ImportLogError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(target_report)
    print(donor_report)
    print("Interpretation limits:")
    print("- A symbol-name match is membership in a saved provider export list, not a resolved dyld bind.")
    print("- Provider rows without a supplied export log are unassessed, not missing.")
    print("- This does not establish symbol versions, ABI compatibility, fixup locations, runtime loading, hardware operation, boot, or SpringBoard.")
    print("- Only saved text logs are read; no cache, binary, device, firmware, or boot state is modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
