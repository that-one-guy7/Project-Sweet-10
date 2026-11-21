#!/usr/bin/env python3
"""Extract selected graphics KEXT metadata from parsed ipsw JSON inventories.

This tool reads JSON arrays only. It does not open KernelCache or KEXT
executables, inspect devices, or modify any input file. Its output is static
metadata and is not a driver, ABI, runtime, or hardware compatibility test.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_PAIRS = (
    ("com.apple.AGXG9P", "com.apple.AGXG10P"),
    ("com.apple.iokit.IOGPUFamily", "com.apple.iokit.IOGPUFamily"),
    ("com.apple.driver.AppleA7IOP", "com.apple.driver.AppleA7IOP"),
)

# Keep the report focused on identity, loader dependencies, and IOKit
# personality properties relevant to the graphics stack. Preserve the
# original JSON values (including empty strings, nulls, arrays, and maps).
SELECTED_FIELDS = (
    "id",
    "name",
    "path",
    "bundle_path",
    "executable",
    "version",
    "short_version",
    "compatible_version",
    "minimum_os_version",
    "sdk",
    "iosource_version",
    "os_bundle_libraries",
    "io_kit_personalities",
)

SCHEMA = "project-sweet-10.graphics-kext-metadata.v1"


class InventoryError(ValueError):
    """Raised when a parsed KEXT JSON inventory cannot be read safely."""


def load_selected_records(
    path: Path, selected_ids: Iterable[str]
) -> dict[str, dict[str, Any]]:
    """Load exact top-level bundle IDs from a JSON array."""
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
    records: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            continue
        bundle_id = record.get("id")
        if not isinstance(bundle_id, str) or bundle_id not in wanted:
            continue
        if bundle_id in records:
            raise InventoryError(
                f"{path}: duplicate selected top-level bundle ID "
                f"{bundle_id!r} at array index {index}"
            )
        records[bundle_id] = record
    return records


def parse_pairs(
    raw_pairs: list[list[str]] | None,
) -> tuple[tuple[str, str], ...]:
    """Return default exact-ID pairs or validate caller-supplied pairs."""
    if not raw_pairs:
        return DEFAULT_PAIRS

    pairs: list[tuple[str, str]] = []
    for pair in raw_pairs:
        if len(pair) != 2:
            raise InventoryError("--pair requires one target ID and one donor ID")
        target_id, donor_id = pair
        if not target_id.strip() or not donor_id.strip():
            raise InventoryError("--pair values must be non-empty exact bundle IDs")
        pairs.append((target_id, donor_id))
    return tuple(pairs)


def project_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return only the selected graphics-relevant fields that were present."""
    return {
        field: record[field]
        for field in SELECTED_FIELDS
        if field in record
    }


def build_report(
    target_records: dict[str, dict[str, Any]],
    donor_records: dict[str, dict[str, Any]],
    pairs: Iterable[tuple[str, str]],
    target_inventory: str,
    donor_inventory: str,
) -> dict[str, Any]:
    """Build a deterministic, JSON-serializable target/donor metadata report."""
    rows = []
    for target_id, donor_id in pairs:
        target = target_records.get(target_id)
        donor = donor_records.get(donor_id)
        rows.append(
            {
                "target_id": target_id,
                "donor_id": donor_id,
                "target": {
                    "status": "PRESENT" if target is not None else "ABSENT_FROM_INVENTORY",
                    "metadata": project_record(target) if target is not None else None,
                },
                "donor": {
                    "status": "PRESENT" if donor is not None else "ABSENT_FROM_INVENTORY",
                    "metadata": project_record(donor) if donor is not None else None,
                },
            }
        )

    return {
        "schema": SCHEMA,
        "target_inventory": Path(target_inventory).name,
        "donor_inventory": Path(donor_inventory).name,
        "pairs": rows,
        "scope_notes": [
            "Selection is by exact top-level KEXT record ID; dependency-map mentions do not count as top-level records.",
            "Only identity fields, os_bundle_libraries, and io_kit_personalities are included.",
            "Missing fields are omitted; explicit null and empty-string values are preserved.",
            "A missing record means only that the exact ID was not found in the parsed JSON inventory.",
            "This report does not inspect executable bytes or establish ABI, runtime loading, IOKit attachment, hardware behavior, or bootability.",
            "No binary, device, firmware, partition, or boot state is accessed or changed.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Extract selected AGX/IOGPU graphics KEXT metadata from the "
            "19H422 target and 20H392 donor JSON inventories."
        )
    )
    parser.add_argument("--target", required=True, type=Path, help="19H422 kexts.json")
    parser.add_argument("--donor", required=True, type=Path, help="20H392 kexts.json")
    parser.add_argument(
        "--pair",
        action="append",
        nargs=2,
        metavar=("TARGET_ID", "DONOR_ID"),
        help="exact target/donor top-level ID pair; repeat to override defaults",
    )
    args = parser.parse_args(argv)

    try:
        pairs = parse_pairs(args.pair)
        target_ids = [target_id for target_id, _ in pairs]
        donor_ids = [donor_id for _, donor_id in pairs]
        target_records = load_selected_records(args.target, target_ids)
        donor_records = load_selected_records(args.donor, donor_ids)
        report = build_report(
            target_records,
            donor_records,
            pairs,
            args.target.name,
            args.donor.name,
        )
    except InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
