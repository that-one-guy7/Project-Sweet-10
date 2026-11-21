#!/usr/bin/env python3
"""Compare complete selected KEXT records from parsed ipsw JSON inventories.

This tool reads JSON files only. It does not open KernelCache or KEXT
executables, inspect devices, or modify input files. A metadata diff is not
an ABI, runtime, or hardware compatibility test.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator


DEFAULT_PAIRS = (
    ("com.apple.driver.AppleA7IOP", "com.apple.driver.AppleA7IOP"),
    (
        "com.apple.driver.AppleEmbeddedTempSensor",
        "com.apple.driver.AppleEmbeddedTempSensor",
    ),
    ("com.apple.driver.AppleT8010", "com.apple.driver.AppleT8015"),
    (
        "com.apple.driver.AppleHurricaneErrorHandler",
        "com.apple.driver.AppleMonsoonErrorHandler",
    ),
    ("com.apple.driver.AppleMobileDispH9P", "com.apple.driver.AppleMobileDispH10P"),
    ("com.apple.AGXG9P", "com.apple.AGXG10P"),
    (
        "com.apple.driver.AppleH9CameraInterface",
        "com.apple.driver.AppleH10CameraInterface",
    ),
)


class InventoryError(ValueError):
    """Raised when a parsed KEXT JSON inventory cannot be read safely."""


class _Missing:
    """Sentinel that distinguishes an omitted key from JSON null."""


MISSING = _Missing()


def load_selected_records(
    path: Path, selected_ids: Iterable[str]
) -> dict[str, dict[str, Any]]:
    """Load only requested exact top-level bundle IDs from a JSON array."""
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

    wanted = set(selected_ids)
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            continue
        bundle_id = record.get("id")
        if not isinstance(bundle_id, str) or bundle_id not in wanted:
            continue
        if bundle_id in result:
            raise InventoryError(
                f"{path}: duplicate selected top-level bundle ID "
                f"{bundle_id!r} at array index {index}"
            )
        result[bundle_id] = record
    return result


def escape_pointer_token(token: str) -> str:
    """Escape a token using JSON Pointer's RFC 6901 rules."""
    return token.replace("~", "~0").replace("/", "~1")


def pointer(path: tuple[str, ...]) -> str:
    """Render a stable JSON Pointer-like location for a differing value."""
    if not path:
        return "$"
    return "$/" + "/".join(escape_pointer_token(token) for token in path)


def iter_differences(
    target: Any, donor: Any, path: tuple[str, ...] = ()
) -> Iterator[tuple[str, Any, Any]]:
    """Yield changed JSON paths, preserving missing/null and JSON type."""
    location = pointer(path)
    if target is MISSING or donor is MISSING:
        yield location, target, donor
        return

    if type(target) is not type(donor):
        yield location, target, donor
        return

    if isinstance(target, dict):
        keys = sorted(set(target) | set(donor), key=str)
        for key in keys:
            left = target.get(key, MISSING)
            right = donor.get(key, MISSING)
            yield from iter_differences(left, right, path + (str(key),))
        return

    if isinstance(target, list):
        if len(target) != len(donor):
            yield pointer(path + ("#length",)), len(target), len(donor)
        for index in range(max(len(target), len(donor))):
            left = target[index] if index < len(target) else MISSING
            right = donor[index] if index < len(donor) else MISSING
            yield from iter_differences(left, right, path + (str(index),))
        return

    if target != donor:
        yield location, target, donor


def format_value(value: Any) -> str:
    if value is MISSING:
        return "<missing>"
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compare_records(
    target_records: dict[str, dict[str, Any]],
    donor_records: dict[str, dict[str, Any]],
    pairs: Iterable[tuple[str, str]],
) -> str:
    """Build a deterministic report for caller-selected target/donor ID pairs."""
    pairs = tuple(pairs)
    lines = [
        "Project Sweet-10: complete selected KEXT JSON record comparison",
        "Scope: exact top-level record IDs; recursive JSON metadata only",
        "",
    ]
    total_diffs = 0

    for target_id, donor_id in pairs:
        target = target_records.get(target_id)
        donor = donor_records.get(donor_id)
        lines.append(f"=== TARGET {target_id} <=> DONOR {donor_id} ===")
        lines.append(
            "  TARGET: PRESENT" if target is not None
            else "  TARGET: ABSENT from this JSON inventory"
        )
        lines.append(
            "  DONOR: PRESENT" if donor is not None
            else "  DONOR: ABSENT from this JSON inventory"
        )

        if target is None or donor is None:
            lines.append("  Recursive comparison: skipped (one or both records unavailable)")
            lines.append("")
            continue

        differences = list(iter_differences(target, donor))
        total_diffs += len(differences)
        if not differences:
            lines.append("  JSON field differences: (none)")
        else:
            lines.append(f"  JSON field differences: {len(differences)}")
            for location, left, right in differences:
                lines.append(
                    f"    {location}: target={format_value(left)}; "
                    f"donor={format_value(right)}"
                )
        lines.append("")

    lines.extend(
        [
            "=== SUMMARY ===",
            f"Record pairs requested: {len(pairs)}",
            f"Total differing JSON paths: {total_diffs}",
            "Missing top-level records refer only to the parsed JSON inventory.",
            "Array values are compared by index; ordering is not normalized.",
            "This report does not establish binary identity, ABI compatibility,",
            "runtime loading, IOKit attachment, hardware behavior, or bootability.",
            "No binary, device, firmware, partition, or boot state was accessed or changed.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_pairs(raw_pairs: list[list[str]] | None) -> tuple[tuple[str, str], ...]:
    """Validate CLI pairs or return the documented default cross-generation set."""
    if not raw_pairs:
        return DEFAULT_PAIRS
    pairs: list[tuple[str, str]] = []
    for target_id, donor_id in raw_pairs:
        if not target_id.strip() or not donor_id.strip():
            raise InventoryError("--pair values must be non-empty exact bundle IDs")
        pairs.append((target_id, donor_id))
    return tuple(pairs)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare complete selected top-level KEXT JSON records from "
            "the 19H422 target and 20H392 donor inventories."
        )
    )
    parser.add_argument("--target", required=True, type=Path, help="19H422 kexts.json")
    parser.add_argument("--donor", required=True, type=Path, help="20H392 kexts.json")
    parser.add_argument(
        "--pair",
        action="append",
        nargs=2,
        metavar=("TARGET_ID", "DONOR_ID"),
        help="exact top-level target/donor ID pair; repeat to override the default set",
    )
    args = parser.parse_args()

    try:
        pairs = parse_pairs(args.pair)
        target_ids = [target_id for target_id, _ in pairs]
        donor_ids = [donor_id for _, donor_id in pairs]
        target_records = load_selected_records(args.target, target_ids)
        donor_records = load_selected_records(args.donor, donor_ids)
    except InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(compare_records(target_records, donor_records, pairs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
