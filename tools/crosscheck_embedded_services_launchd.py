#!/usr/bin/env python3
"""Cross-reference embedded-bundle MachServices declarations with launchd's index.

This is a read-only comparison of two sanitized metadata formats. It does not
inspect bundle binaries or infer runtime registration, launch, or clients.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

BUNDLE_SCHEMA = "project-sweet-10.embedded-service-inventory.v1"
LAUNCHD_SCHEMA = "project-sweet-10.launchd-inventory.v1"
OUTPUT_SCHEMA = "project-sweet-10.embedded-launchd-crosscheck.v1"


def load_document(path: str | Path, expected_schema: str) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    if value.get("schema") != expected_schema:
        raise ValueError(
            f"{path}: expected schema {expected_schema!r}, "
            f"got {value.get('schema')!r}"
        )
    return value


def load_bundle_inventory(path: str | Path) -> dict[str, Any]:
    document = load_document(path, BUNDLE_SCHEMA)
    bundles = document.get("bundles")
    if not isinstance(bundles, list) or not all(
        isinstance(item, dict) for item in bundles
    ):
        raise ValueError(f"{path}: 'bundles' must be an array of objects")
    for index, bundle in enumerate(bundles):
        if bundle.get("status") != "parsed":
            continue
        names = bundle.get("mach_services", [])
        if not isinstance(names, list) or not all(
            isinstance(name, str) for name in names
        ):
            raise ValueError(
                f"{path}: bundles[{index}].mach_services must be an array of strings"
            )
    return document


def load_launchd_inventory(path: str | Path) -> dict[str, Any]:
    document = load_document(path, LAUNCHD_SCHEMA)
    rows = document.get("mach_service_providers")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(
            f"{path}: 'mach_service_providers' must be an array of objects"
        )
    seen: set[str] = set()
    for index, row in enumerate(rows):
        service = row.get("service")
        labels = row.get("provider_labels")
        if not isinstance(service, str) or not service:
            raise ValueError(
                f"{path}: mach_service_providers[{index}].service must be a non-empty string"
            )
        if service in seen:
            raise ValueError(f"{path}: duplicate launchd service index entry {service!r}")
        seen.add(service)
        if not isinstance(labels, list) or not all(
            isinstance(label, str) for label in labels
        ):
            raise ValueError(
                f"{path}: mach_service_providers[{index}].provider_labels must be an array of strings"
            )
    return document


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def crosscheck(
    bundle_inventory: dict[str, Any],
    launchd_inventory: dict[str, Any],
    bundle_json_sha256: str,
    launchd_json_sha256: str,
) -> dict[str, Any]:
    provider_index = {
        row["service"]: sorted(set(row["provider_labels"]))
        for row in launchd_inventory["mach_service_providers"]
    }

    entries: list[dict[str, Any]] = []
    for bundle in bundle_inventory["bundles"]:
        if bundle.get("status") != "parsed":
            continue
        for service in sorted(set(bundle.get("mach_services", []))):
            labels = provider_index.get(service, [])
            entries.append({
                "service": service,
                "bundle_identifier": bundle.get("bundle_identifier"),
                "bundle_type": bundle.get("bundle_type"),
                "bundle_executable": bundle.get("bundle_executable"),
                "executable_state": bundle.get("executable_state"),
                "source_root": bundle.get("source_root"),
                "bundle_path": bundle.get("bundle_path"),
                "launchd_index_match": service in provider_index,
                "launchd_provider_labels": labels,
            })

    entries.sort(key=lambda item: (
        item["service"],
        str(item["source_root"]),
        str(item["bundle_path"]),
    ))
    declared_names = {entry["service"] for entry in entries}
    matched_names = {
        entry["service"] for entry in entries if entry["launchd_index_match"]
    }
    unmatched_names = declared_names - matched_names

    return {
        "bundle_inventory_sha256": bundle_json_sha256,
        "launchd_inventory_json_sha256": launchd_json_sha256,
        "launchd_source_plist_sha256": launchd_inventory.get("source_sha256"),
        "summary": {
            "candidate_bundle_count": len(bundle_inventory["bundles"]),
            "parsed_bundle_count": sum(
                bundle.get("status") == "parsed"
                for bundle in bundle_inventory["bundles"]
            ),
            "service_declaration_occurrence_count": len(entries),
            "unique_declared_service_count": len(declared_names),
            "launchd_index_match_occurrence_count": sum(
                entry["launchd_index_match"] for entry in entries
            ),
            "launchd_index_unmatched_occurrence_count": sum(
                not entry["launchd_index_match"] for entry in entries
            ),
            "unique_declared_names_found_in_launchd_index": len(matched_names),
            "unique_declared_names_not_found_in_launchd_index": len(unmatched_names),
            "launchd_provider_index_name_count": len(provider_index),
        },
        "entries": entries,
    }


def build_report(
    target_bundle_path: str | Path,
    donor_bundle_path: str | Path,
    target_launchd_path: str | Path,
    donor_launchd_path: str | Path,
) -> dict[str, Any]:
    target_bundle = load_bundle_inventory(target_bundle_path)
    donor_bundle = load_bundle_inventory(donor_bundle_path)
    target_launchd = load_launchd_inventory(target_launchd_path)
    donor_launchd = load_launchd_inventory(donor_launchd_path)

    return {
        "schema": OUTPUT_SCHEMA,
        "target_19H422": crosscheck(
            target_bundle,
            target_launchd,
            sha256_file(target_bundle_path),
            sha256_file(target_launchd_path),
        ),
        "donor_20H392": crosscheck(
            donor_bundle,
            donor_launchd,
            sha256_file(donor_bundle_path),
            sha256_file(donor_launchd_path),
        ),
        "interpretation_limits": [
            "This joins bundle-plist MachServices declarations to the provider index from the central LaunchDaemons dictionary only.",
            "An index match is a shared static service-name string, not proof of registration, successful launch, or a client relationship.",
            "A name absent from this index may be declared by LaunchAgents, another plist, another volume, or runtime state not covered by this inventory.",
            "Bundle executable presence is filename metadata only; this tool does not inspect binaries, signatures, entitlements, or ABI.",
            "The target and donor are different products and different iOS releases; differences are not attributable to SoC generation alone.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_bundle_json", help="19H422 embedded-service inventory JSON")
    parser.add_argument("donor_bundle_json", help="20H392 embedded-service inventory JSON")
    parser.add_argument("target_launchd_json", help="19H422 central launchd inventory JSON")
    parser.add_argument("donor_launchd_json", help="20H392 central launchd inventory JSON")
    args = parser.parse_args(argv)

    try:
        report = build_report(
            args.target_bundle_json,
            args.donor_bundle_json,
            args.target_launchd_json,
            args.donor_launchd_json,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
