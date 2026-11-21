#!/usr/bin/env python3
"""Inventory embedded iOS XPC services and app extensions from mounted roots.

Reads only Info.plist files in .xpc and .appex directories. It does not read or
execute bundle binaries, follow symlinks, or modify the source filesystem.
Only explicitly allowlisted plist fields are emitted; arbitrary plist content,
environment values, arguments, and privacy-sensitive payloads are omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import sys
from pathlib import Path
from typing import Any

SCHEMA = "project-sweet-10.embedded-service-inventory.v1"
DEFAULT_SUFFIXES = (".xpc", ".appex")
INFO_PLIST_CANDIDATES = (Path("Info.plist"), Path("Contents/Info.plist"))


class InventoryError(ValueError):
    """Raised when an input root cannot be scanned."""


def _string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return sorted({item for item in value if isinstance(item, str)})


def _string_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return sorted(key for key in value if isinstance(key, str))
    if isinstance(value, (list, tuple)):
        return _string_list(value)
    return []


def _safe_relative_executable(bundle: Path, executable: str | None) -> tuple[str | None, str | None]:
    """Report only a bundle-relative executable name and presence state."""
    if executable is None:
        return None, "not-declared"
    candidate = Path(executable)
    if (
        candidate.name != executable
        or executable in ("", ".", "..")
        or "/" in executable
        or "\\" in executable
        or "\x00" in executable
    ):
        return None, "unsafe-executable-name"
    path = bundle / executable
    try:
        if path.is_symlink():
            return executable, "symlink"
        if path.is_file():
            return executable, "regular-file"
        if path.exists():
            return executable, "other-file-type"
        return executable, "not-found"
    except (OSError, ValueError):
        return executable, "stat-error"


def _parse_xpc_service(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    service_limit = value.get("ServiceInstanceLimit")
    if not isinstance(service_limit, int) or isinstance(service_limit, bool):
        service_limit = None
    join_session = value.get("JoinExistingSession")
    if not isinstance(join_session, bool):
        join_session = None
    return {
        "service_type": _string(value.get("ServiceType")),
        "run_loop_type": _string(value.get("RunLoopType")),
        "join_existing_session": join_session,
        "service_instance_limit": service_limit,
        "declared_mach_services": _string_keys(value.get("MachServices")),
        "declared_keys": _string_keys(value),
    }


def _parse_extension(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    attributes = value.get("NSExtensionAttributes")
    return {
        "extension_point_identifier": _string(value.get("NSExtensionPointIdentifier")),
        "principal_class": _string(value.get("NSExtensionPrincipalClass")),
        "attribute_keys": _string_keys(attributes),
        "declared_keys": _string_keys(value),
    }


def _bundle_record(root: Path, root_label: str, bundle: Path, suffix: str) -> dict[str, Any]:
    relative_bundle = bundle.relative_to(root).as_posix()
    record: dict[str, Any] = {
        "source_root": root_label,
        "bundle_path": relative_bundle,
        "bundle_type": suffix,
        "info_plist_path": None,
        "status": "unreadable",
        "info_plist_sha256": None,
        "bundle_identifier": None,
        "bundle_executable": None,
        "executable_state": None,
        "package_type": None,
        "minimum_os_version": None,
        "supported_platforms": [],
        "mach_services": [],
        "xpc_service": None,
        "extension": None,
    }

    if bundle.is_symlink():
        record["status"] = "symlink-bundle-skipped"
        return record

    plist_path = None
    for relative_info_path in INFO_PLIST_CANDIDATES:
        candidate_plist = bundle / relative_info_path
        if candidate_plist.is_symlink():
            record["status"] = "symlink-info-plist-skipped"
            record["info_plist_path"] = candidate_plist.relative_to(root).as_posix()
            return record
        if candidate_plist.is_file():
            plist_path = candidate_plist
            break
    if plist_path is None:
        record["status"] = "missing-info-plist"
        return record

    try:
        raw = plist_path.read_bytes()
    except OSError:
        record["status"] = "unreadable-info-plist"
        record["info_plist_path"] = plist_path.relative_to(root).as_posix()
        return record

    record["info_plist_path"] = plist_path.relative_to(root).as_posix()
    record["info_plist_sha256"] = hashlib.sha256(raw).hexdigest()
    try:
        info = plistlib.loads(raw)
    except (plistlib.InvalidFileException, ValueError, TypeError, OverflowError):
        record["status"] = "invalid-info-plist"
        return record
    if not isinstance(info, dict):
        record["status"] = "non-dictionary-info-plist"
        return record

    executable = _string(info.get("CFBundleExecutable"))
    executable_name, executable_state = _safe_relative_executable(bundle, executable)
    xpc_service = _parse_xpc_service(info.get("XPCService"))
    extension = _parse_extension(info.get("NSExtension"))
    mach_services = set(_string_keys(info.get("MachServices")))
    if xpc_service:
        mach_services.update(xpc_service["declared_mach_services"])

    record.update({
        "status": "parsed",
        "bundle_identifier": _string(info.get("CFBundleIdentifier")),
        "bundle_executable": executable_name,
        "executable_state": executable_state,
        "package_type": _string(info.get("CFBundlePackageType")),
        "minimum_os_version": _string(info.get("MinimumOSVersion")),
        "supported_platforms": _string_list(info.get("CFBundleSupportedPlatforms")),
        "mach_services": sorted(mach_services),
        "xpc_service": xpc_service,
        "extension": extension,
    })
    return record


def inspect_roots(roots: list[Path], suffixes: tuple[str, ...] = DEFAULT_SUFFIXES) -> dict[str, Any]:
    """Scan one or more extracted/mounted roots without following symlinks."""
    if not roots:
        raise InventoryError("at least one root directory is required")
    normalized_suffixes = tuple(
        sorted({s.lower() if s.startswith(".") else "." + s.lower() for s in suffixes})
    )
    if not normalized_suffixes:
        raise InventoryError("at least one bundle suffix is required")

    records: list[dict[str, Any]] = []
    scan_errors: list[dict[str, str]] = []
    total_walked_roots = 0

    for root_index, input_root in enumerate(roots):
        root = Path(input_root).expanduser().resolve()
        if not root.is_dir():
            raise InventoryError("root path is not a directory: {}".format(input_root))
        root_label = "root_{}".format(root_index)
        total_walked_roots += 1
        candidates: set[tuple[str, str]] = set()

        def on_walk_error(error: OSError) -> None:
            try:
                rel = Path(error.filename).relative_to(root).as_posix() if error.filename else "."
            except (ValueError, TypeError):
                rel = "."
            scan_errors.append({
                "source_root": root_label,
                "path": rel,
                "error": error.__class__.__name__,
            })

        for directory, dirnames, _filenames in os.walk(
            root, topdown=True, followlinks=False, onerror=on_walk_error
        ):
            dirnames.sort(key=str.lower)
            current = Path(directory)
            for dirname in list(dirnames):
                suffix = Path(dirname).suffix.lower()
                if suffix in normalized_suffixes:
                    candidates.add(((current / dirname).relative_to(root).as_posix(), suffix))

        for relative_path, suffix in sorted(candidates, key=lambda item: item[0].lower()):
            bundle = root / relative_path
            records.append(_bundle_record(root, root_label, bundle, suffix))

    records.sort(key=lambda row: (
        row["source_root"], row["bundle_path"].lower(), row["bundle_path"]
    ))
    providers: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if record["status"] != "parsed":
            continue
        for service in record["mach_services"]:
            providers.setdefault(service, []).append({
                "source_root": record["source_root"],
                "bundle_identifier": record["bundle_identifier"],
                "bundle_path": record["bundle_path"],
            })

    provider_rows = [
        {
            "service": service,
            "providers": sorted(
                rows, key=lambda row: (row["source_root"], row["bundle_path"])
            ),
        }
        for service, rows in sorted(providers.items())
    ]
    status_counts: dict[str, int] = {}
    for record in records:
        status_counts[record["status"]] = status_counts.get(record["status"], 0) + 1

    return {
        "schema": SCHEMA,
        "source_root_count": total_walked_roots,
        "bundle_suffixes": list(normalized_suffixes),
        "candidate_bundle_count": len(records),
        "status_counts": dict(sorted(status_counts.items())),
        "bundles": records,
        "mach_service_providers": provider_rows,
        "scan_errors": scan_errors,
        "scope_notes": [
            "Scans directories ending in the selected bundle suffixes, defaulting to .xpc and .appex.",
            "Reads only each candidate bundle's Info.plist or Contents/Info.plist.",
            "Does not read or execute bundle binaries, follow symlinks, or modify source files.",
            "Only allowlisted plist metadata is emitted; arbitrary keys and values are omitted.",
            "MachServices entries are declarations in bundle metadata, not proof of launch, registration, or clients.",
            "Executable state is a filename-presence check only, not a signature or loadability check.",
            "Multiple roots are kept separate as root_0, root_1, and so on; root paths are not emitted.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only inventory of embedded XPC-service and app-extension bundles."
    )
    parser.add_argument(
        "roots",
        nargs="+",
        help="one or more extracted or mounted iOS roots (e.g. OS root and SystemOS Cryptex root)",
    )
    parser.add_argument(
        "--suffix",
        action="append",
        default=None,
        help="bundle directory suffix to include (repeatable; default: .xpc and .appex)",
    )
    args = parser.parse_args(argv)
    try:
        report = inspect_roots(
            [Path(root) for root in args.roots],
            tuple(args.suffix or DEFAULT_SUFFIXES),
        )
    except InventoryError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
