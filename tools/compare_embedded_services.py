#!/usr/bin/env python3
"""Compare sanitized embedded XPC/app-extension inventory JSON files.

This utility compares plist-derived metadata only. It does not inspect,
execute, or validate bundle binaries or infer runtime service availability.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA = "project-sweet-10.embedded-service-inventory.v1"
METADATA_FIELDS = (
    "bundle_type",
    "bundle_executable",
    "executable_state",
    "package_type",
    "minimum_os_version",
    "supported_platforms",
    "extension",
    "xpc_service",
    "mach_services",
)


def load_inventory(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    if document.get("schema") != EXPECTED_SCHEMA:
        raise ValueError(
            f"{path}: expected schema {EXPECTED_SCHEMA!r}, "
            f"got {document.get('schema')!r}"
        )
    bundles = document.get("bundles")
    if not isinstance(bundles, list) or not all(
        isinstance(item, dict) for item in bundles
    ):
        raise ValueError(f"{path}: 'bundles' must be an array of objects")
    return document


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def group_by_identifier(document: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bundle in document["bundles"]:
        identifier = bundle.get("bundle_identifier")
        if isinstance(identifier, str) and identifier:
            grouped[identifier].append(bundle)
    return dict(grouped)


def distinct_values(records: list[dict[str, Any]], field: str) -> set[str]:
    return {canonical(record.get(field)) for record in records}


def render_values(records: list[dict[str, Any]], field: str) -> str:
    values = sorted(distinct_values(records, field))
    return json.dumps([json.loads(value) for value in values], sort_keys=True)


def compare(
    target: dict[str, Any], donor: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    target_groups = group_by_identifier(target)
    donor_groups = group_by_identifier(donor)
    target_ids = set(target_groups)
    donor_ids = set(donor_groups)

    rows: list[dict[str, str]] = []
    field_diff_counts: Counter[str] = Counter()
    presence_counts = Counter()

    for identifier in sorted(target_ids | donor_ids):
        left = target_groups.get(identifier, [])
        right = donor_groups.get(identifier, [])
        if left and right:
            presence = "common"
        elif left:
            presence = "target-only"
        else:
            presence = "donor-only"
        presence_counts[presence] += 1

        changed_fields = []
        if left and right:
            for field in METADATA_FIELDS:
                if distinct_values(left, field) != distinct_values(right, field):
                    changed_fields.append(field)
                    field_diff_counts[field] += 1

        def paths(records: list[dict[str, Any]]) -> str:
            values = sorted(
                {
                    canonical(
                        {
                            "source_root": item.get("source_root"),
                            "bundle_path": item.get("bundle_path"),
                        }
                    )
                    for item in records
                }
            )
            return json.dumps([json.loads(value) for value in values], sort_keys=True)

        rows.append(
            {
                "bundle_identifier": identifier,
                "presence": presence,
                "target_occurrences": str(len(left)),
                "donor_occurrences": str(len(right)),
                "target_bundle_types": render_values(left, "bundle_type"),
                "donor_bundle_types": render_values(right, "bundle_type"),
                "target_minimum_os_versions": render_values(left, "minimum_os_version"),
                "donor_minimum_os_versions": render_values(right, "minimum_os_version"),
                "target_paths": paths(left),
                "donor_paths": paths(right),
                "changed_metadata_fields": ";".join(changed_fields),
            }
        )

    def inventory_stats(document: dict[str, Any]) -> dict[str, Any]:
        bundles = document["bundles"]
        status_counts = Counter(str(item.get("status", "unspecified")) for item in bundles)
        type_counts = Counter(str(item.get("bundle_type", "unspecified")) for item in bundles)
        identifiers = [
            item.get("bundle_identifier")
            for item in bundles
            if isinstance(item.get("bundle_identifier"), str)
            and item.get("bundle_identifier")
        ]
        declared_mach_names = sum(
            len(item.get("mach_services") or [])
            for item in bundles
            if isinstance(item.get("mach_services") or [], list)
        )
        return {
            "candidate_bundle_count": len(bundles),
            "identifier_record_count": len(identifiers),
            "unique_bundle_identifier_count": len(group_by_identifier(document)),
            "duplicate_identifier_count": sum(
                count > 1 for count in Counter(identifiers).values()
            ),
            "status_counts": dict(sorted(status_counts.items())),
            "bundle_type_counts": dict(sorted(type_counts.items())),
            "source_root_counts": dict(
                sorted(
                    Counter(
                        str(item.get("source_root", "unspecified"))
                        for item in bundles
                    ).items()
                )
            ),
            "declared_mach_service_name_count": declared_mach_names,
            "mach_service_provider_index_entry_count": len(
                document.get("mach_service_providers") or []
            ),
            "scan_error_count": len(document.get("scan_errors") or []),
        }

    target_stats = inventory_stats(target)
    donor_stats = inventory_stats(donor)
    summary = {
        "schema": "project-sweet-10.embedded-service-comparison.v1",
        "target": target_stats,
        "donor": donor_stats,
        "identifier_comparison": {
            "common_identifier_count": presence_counts["common"],
            "target_only_identifier_count": presence_counts["target-only"],
            "donor_only_identifier_count": presence_counts["donor-only"],
            "identifier_count": len(rows),
            "metadata_difference_identifier_counts": dict(
                sorted(field_diff_counts.items())
            ),
        },
        "interpretation_limits": [
            "Comparison is limited to the input inventories and their selected .xpc/.appex roots.",
            "Identifier presence is not a one-to-one executable or service identity guarantee; duplicate identifiers are retained as occurrence counts.",
            "Path and source-root placement may differ because the filesystem roots and staged-app locations differ.",
            "MinimumOSVersion differences are expected to reflect the two distinct OS builds and are not ABI evidence.",
            "Plist declarations and executable filename-presence checks do not prove launch, registration, clients, signature validity, ABI compatibility, or runtime availability.",
            "This tool reads only the sanitized JSON inventory files; it does not inspect or execute bundle binaries or access a device.",
        ],
    }
    return summary, rows


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    columns = [
        "bundle_identifier",
        "presence",
        "target_occurrences",
        "donor_occurrences",
        "target_bundle_types",
        "donor_bundle_types",
        "target_minimum_os_versions",
        "donor_minimum_os_versions",
        "target_paths",
        "donor_paths",
        "changed_metadata_fields",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_json", help="19H422 target-reference inventory JSON")
    parser.add_argument("donor_json", help="20H392 donor-reference inventory JSON")
    parser.add_argument("--csv-out", help="write one row per unique bundle identifier")
    args = parser.parse_args(argv)

    try:
        target = load_inventory(args.target_json)
        donor = load_inventory(args.donor_json)
        summary, rows = compare(target, donor)
        if args.csv_out:
            write_csv(args.csv_out, rows)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
