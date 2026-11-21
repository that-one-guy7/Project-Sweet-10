#!/usr/bin/env python3
"""Search parsed ipsw KEXT JSON inventories for possible renamed equivalents.

This is a read-only metadata search. It never opens kernel binaries, extracts
or executes KEXTs, loads drivers, accesses a device, or changes input files.
A text match is only a lead for manual review, not proof of equivalent code or
functionality.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator

DEFAULT_TERMS = (
    "hurricane",
    "errorhandler",
    "platformerror",
    "t8010",
    "t8015",
    "h9",
)

IDENTITY_FIELDS = {"id", "name", "executable", "bundle_path"}
CATEGORY_ORDER = ("identity", "personality", "dependency", "other metadata")
MAX_VALUE_CHARS = 400


class InventoryError(ValueError):
    """Raised when a parsed KEXT JSON inventory cannot be searched."""


def normalize(value: str) -> str:
    """Case-fold and remove punctuation so hyphen/underscore variants match."""
    return "".join(character for character in value.casefold() if character.isalnum())


def iter_string_values(value: Any, path: str = "$[root]") -> Iterator[tuple[str, str]]:
    """Yield every string key and value in a JSON object with an unambiguous path."""
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}[{json.dumps(key_text, ensure_ascii=False)}]"
            # Bundle IDs and personality names are often JSON object keys,
            # not values, so search keys as well as their nested values.
            yield f"{child_path}::<key>", key_text
            yield from iter_string_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_string_values(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def classify_path(path: str) -> str:
    """Separate bundle identity from personality/dependency references."""
    if path.startswith('$[root]["io_kit_personalities"]'):
        return "personality"
    if path.startswith('$[root]["os_bundle_libraries"]'):
        return "dependency"
    if path in {f'$[root]["{field}"]' for field in IDENTITY_FIELDS}:
        return "identity"
    return "other metadata"


def load_inventory(path: Path) -> list[dict[str, Any]]:
    """Load a top-level array of parsed KEXT records without modifying it."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InventoryError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InventoryError(
            f"invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    if not isinstance(data, list):
        raise InventoryError(
            f"{path}: expected a top-level JSON array of KEXT records, "
            f"got {type(data).__name__}"
        )
    return [record for record in data if isinstance(record, dict)]


def find_record_matches(
    record: dict[str, Any], terms: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Return each string field/key whose normalized text contains a search term."""
    matches: list[dict[str, Any]] = []
    for path, value in iter_string_values(record):
        normalized_value = normalize(value)
        matched_terms = [term for term in terms if term in normalized_value]
        if matched_terms:
            matches.append(
                {
                    "path": path,
                    "value": value,
                    "terms": matched_terms,
                    "category": classify_path(path),
                }
            )
    return matches


def display_value(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(rendered) > MAX_VALUE_CHARS:
        return rendered[: MAX_VALUE_CHARS - 3] + "..."
    return rendered


def scan_inventory(
    path: Path,
    label: str,
    raw_terms: tuple[str, ...] = DEFAULT_TERMS,
) -> str:
    """Return a text report of keyword matches in every top-level KEXT record."""
    terms = tuple(dict.fromkeys(normalize(term) for term in raw_terms if normalize(term)))
    if not terms:
        raise InventoryError("at least one non-empty search term is required")

    records = load_inventory(path)
    results: list[tuple[int, dict[str, Any], list[dict[str, Any]]]] = []
    category_record_counts = {category: 0 for category in CATEGORY_ORDER}

    for index, record in enumerate(records):
        matches = find_record_matches(record, terms)
        if not matches:
            continue
        results.append((index, record, matches))
        categories = {match["category"] for match in matches}
        for category in categories:
            category_record_counts[category] += 1

    lines = [
        f"Project Sweet-10: KEXT metadata keyword search — {label}",
        f"Input: {path}",
        f"Terms (normalized): {', '.join(terms)}",
        f"Top-level KEXT records scanned: {len(records)}",
        f"Records with one or more keyword matches: {len(results)}",
        "",
    ]

    if not results:
        lines.append("(no matching string values found)")
    else:
        for index, record, matches in results:
            lines.append(f"=== top-level record index {index} ===")
            for key in ("id", "name", "executable", "bundle_path"):
                if key in record:
                    lines.append(f"  {key}: {display_value(record[key])}")
            for category in CATEGORY_ORDER:
                category_matches = [
                    match for match in matches if match["category"] == category
                ]
                if not category_matches:
                    continue
                lines.append(f"  {category} matches:")
                for match in category_matches:
                    terms_text = ",".join(match["terms"])
                    lines.append(
                        f"    {match['path']} [terms={terms_text}] = "
                        f"{display_value(match['value'])}"
                    )
            lines.append("")

    lines.extend(
        [
            "=== MATCH COUNTS ===",
            f"Records with identity-field matches: {category_record_counts['identity']}",
            f"Records with personality matches: {category_record_counts['personality']}",
            f"Records with dependency-reference matches: {category_record_counts['dependency']}",
            f"Records with other-metadata matches: {category_record_counts['other metadata']}",
            "",
            "Interpretation: a keyword hit is a metadata search lead only. It does not",
            "prove that a bundle is equivalent, ABI-compatible, loadable, or functional.",
            "No binary, device, firmware, partition, or boot state was accessed or changed.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Search target 19H422 and donor 20H392 parsed KEXT JSON inventories "
            "for possible renamed platform/error-handler records."
        )
    )
    parser.add_argument("--target", required=True, type=Path, help="19H422 kexts.json")
    parser.add_argument("--donor", required=True, type=Path, help="20H392 kexts.json")
    parser.add_argument(
        "--terms",
        nargs="+",
        default=list(DEFAULT_TERMS),
        help=(
            "case-insensitive substring terms; punctuation is ignored "
            f"(default: {' '.join(DEFAULT_TERMS)})"
        ),
    )
    args = parser.parse_args()

    try:
        target_report = scan_inventory(args.target, "TARGET 19H422", tuple(args.terms))
        donor_report = scan_inventory(args.donor, "DONOR 20H392", tuple(args.terms))
    except InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(target_report)
    sys.stdout.write("\n" + "=" * 78 + "\n\n")
    sys.stdout.write(donor_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
