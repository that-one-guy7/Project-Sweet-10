#!/usr/bin/env python3
"""Compare selected target/donor KEXT metadata exported by ipsw.

This tool reads JSON files only. It does not open KernelCache binaries,
load KEXTs, inspect devices, or modify either input file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SELECTED_BUNDLES = (
    "com.apple.driver.AppleInterruptController",
    "com.apple.driver.AppleARMPlatform",
    "com.apple.driver.AppleT8010",
    "com.apple.driver.AppleT8010CLPC",
    "com.apple.driver.AppleT8010PCIe",
    "com.apple.driver.AppleT8010PMPFirmware",
    "com.apple.driver.AppleT8010PMGR",
    "com.apple.driver.AppleT8010SmartIO",
    "com.apple.driver.AppleT8010SOCTuner",
)

BUNDLE_FIELDS = (
    "name",
    "executable",
    "version",
    "short_version_string",
    "compatible_version",
    "minimum_os_version",
    "sdk",
    "sdk_build",
    "platform_name",
    "platform_version",
    "platform_build",
    "package_type",
    "os_bundle_required",
    "bundle_path",
)

PERSONALITY_FIELDS = (
    "CFBundleIdentifier",
    "IOClass",
    "IONameMatch",
    "IOProviderClass",
    "IOMatchCategory",
    "IOResourceMatch",
    "IOPropertyMatch",
    "IOProbeScore",
    "IOInterruptControllers",
    "IOInterruptSpecifiers",
    "IOInterruptTypes",
    "IOInterruptController",
    "IOUserClientClass",
)


class InventoryError(ValueError):
    """Raised when an ipsw KEXT JSON inventory is malformed."""


def load_inventory(path: Path) -> dict[str, dict[str, Any]]:
    """Load a top-level array of KEXT records, retaining exact selected IDs."""
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

    selected = set(SELECTED_BUNDLES)
    result: dict[str, dict[str, Any]] = {}

    for index, record in enumerate(data):
        if not isinstance(record, dict):
            continue
        bundle_id = record.get("id")
        if bundle_id not in selected:
            # In particular, dependency references to AppleARMPlatform in
            # os_bundle_libraries are not treated as top-level KEXT records.
            continue
        if bundle_id in result:
            raise InventoryError(
                f"{path}: duplicate top-level bundle ID {bundle_id!r} "
                f"at array index {index}"
            )
        result[bundle_id] = record

    return result


def metadata(record: dict[str, Any] | None) -> dict[str, Any]:
    if record is None:
        return {}
    return {key: record[key] for key in BUNDLE_FIELDS if key in record}


def personalities(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = record.get("io_kit_personalities", {})
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for name, value in raw.items():
        if isinstance(name, str) and isinstance(value, dict):
            result[name] = {
                key: value[key]
                for key in PERSONALITY_FIELDS
                if key in value
            }
    return result


def libraries(record: dict[str, Any]) -> dict[str, Any]:
    raw = record.get("os_bundle_libraries", {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(name): version
        for name, version in raw.items()
        if isinstance(name, str)
    }


def shown(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def print_record(label: str, record: dict[str, Any] | None) -> None:
    if record is None:
        print(f"  {label}: ABSENT from this JSON inventory")
        return
    print(f"  {label}: PRESENT")
    for key, value in metadata(record).items():
        print(f"    {key}: {shown(value)}")


def print_map_difference(
    title: str,
    left_label: str,
    left: dict[str, Any],
    right_label: str,
    right: dict[str, Any],
) -> None:
    left_keys = set(left)
    right_keys = set(right)
    left_only = sorted(left_keys - right_keys)
    right_only = sorted(right_keys - left_keys)
    common = sorted(left_keys & right_keys)

    print(f"  {title}:")
    print(f"    {left_label}-only: {', '.join(left_only) if left_only else '(none)'}")
    print(f"    {right_label}-only: {', '.join(right_only) if right_only else '(none)'}")

    changed = [
        key for key in common
        if shown(left[key]) != shown(right[key])
    ]
    if changed:
        print("    shared names with differing values:")
        for key in changed:
            print(
                f"      {key}: {left_label}={shown(left[key])}; "
                f"{right_label}={shown(right[key])}"
            )
    else:
        print("    shared names with differing values: (none)")



def print_single_side_details(label: str, record: dict[str, Any]) -> None:
    """Print available personality and dependency data when only one side exists."""
    personality_map = personalities(record)
    print(f"  {label} IOKit personalities:")
    if not personality_map:
        print("    (no selected personality fields found)")
    for name in sorted(personality_map):
        fields = personality_map[name]
        print(f"    {name}:")
        if not fields:
            print("      (no fields in the comparator's selected field set)")
        for key in sorted(fields):
            print(f"      {key}: {shown(fields[key])}")

    dependency_map = libraries(record)
    print(f"  {label} os_bundle_libraries ({len(dependency_map)} entries):")
    if not dependency_map:
        print("    (none in this JSON record)")
    for name in sorted(dependency_map):
        print(f"    {name}: {shown(dependency_map[name])}")


def compare(
    target: dict[str, dict[str, Any]],
    donor: dict[str, dict[str, Any]],
) -> str:
    from io import StringIO

    original_stdout = sys.stdout
    buffer = StringIO()
    sys.stdout = buffer
    try:
        print("Project Sweet-10: selected KEXT metadata comparison")
        print("Target: iPhone9,1 / D10AP / iOS 15.8.8 / 19H422")
        print("Donor:  iPhone10,3 / D22AP / iOS 16.7.16 / 20H392")
        print("Scope: exact top-level bundle IDs; personality and dependency metadata")
        print()

        target_present = 0
        donor_present = 0

        for bundle_id in SELECTED_BUNDLES:
            t_record = target.get(bundle_id)
            d_record = donor.get(bundle_id)
            target_present += t_record is not None
            donor_present += d_record is not None

            print(f"=== {bundle_id} ===")
            print_record("TARGET 19H422", t_record)
            print_record("DONOR 20H392", d_record)

            if t_record is not None and d_record is not None:
                t_meta = metadata(t_record)
                d_meta = metadata(d_record)
                changed_fields = [
                    key for key in sorted(set(t_meta) | set(d_meta))
                    if shown(t_meta.get(key, "<missing>"))
                    != shown(d_meta.get(key, "<missing>"))
                ]
                if changed_fields:
                    print("  Bundle metadata differences:")
                    for key in changed_fields:
                        print(
                            f"    {key}: target={shown(t_meta.get(key, '<missing>'))}; "
                            f"donor={shown(d_meta.get(key, '<missing>'))}"
                        )
                else:
                    print("  Bundle metadata differences: (none)")

                t_personalities = personalities(t_record)
                d_personalities = personalities(d_record)
                print_map_difference(
                    "Personality names",
                    "target",
                    t_personalities,
                    "donor",
                    d_personalities,
                )
                for name in sorted(set(t_personalities) & set(d_personalities)):
                    t_personality = t_personalities[name]
                    d_personality = d_personalities[name]
                    changed = [
                        key for key in sorted(
                            set(t_personality) | set(d_personality)
                        )
                        if shown(t_personality.get(key, "<missing>"))
                        != shown(d_personality.get(key, "<missing>"))
                    ]
                    if changed:
                        print(f"    Personality field differences: {name}")
                        for key in changed:
                            print(
                                f"      {key}: target="
                                f"{shown(t_personality.get(key, '<missing>'))}; "
                                f"donor={shown(d_personality.get(key, '<missing>'))}"
                            )

                print_map_difference(
                    "os_bundle_libraries names/versions",
                    "target",
                    libraries(t_record),
                    "donor",
                    libraries(d_record),
                )
            else:
                print("  Side-specific details:")
                if t_record is not None:
                    print_single_side_details("TARGET 19H422", t_record)
                else:
                    print("  TARGET 19H422: unavailable (no selected top-level record)")
                if d_record is not None:
                    print_single_side_details("DONOR 20H392", d_record)
                else:
                    print("  DONOR 20H392: unavailable (no selected top-level record)")
            print()

        print("=== SUMMARY ===")
        print(f"Selected bundle IDs: {len(SELECTED_BUNDLES)}")
        print(f"Present in target: {target_present}")
        print(f"Present in donor: {donor_present}")
        print(
            "Important: ABSENT means absent from this parsed KEXT JSON inventory "
            "only; it does not prove absence from every filesystem or runtime source."
        )
        print(
            "Static metadata differences do not establish binary ABI compatibility, "
            "runtime loading, IOKit attachment, hardware behavior, or bootability."
        )
    finally:
        sys.stdout = original_stdout

    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare selected KEXT metadata in 19H422 and 20H392 JSON inventories."
    )
    parser.add_argument("--target", required=True, type=Path, help="19H422 kexts.json")
    parser.add_argument("--donor", required=True, type=Path, help="20H392 kexts.json")
    args = parser.parse_args()

    try:
        target = load_inventory(args.target)
        donor = load_inventory(args.donor)
    except InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = compare(target, donor)
    sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
