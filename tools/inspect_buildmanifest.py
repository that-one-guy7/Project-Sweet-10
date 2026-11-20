#!/usr/bin/env python3
"""Read BuildManifest.plist metadata directly from an IPSW ZIP archive.

This utility does not extract files, execute archive contents, modify the IPSW,
or select a "correct" BuildIdentity. It reports every identity for review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import sys
import zipfile
from datetime import date, datetime
from pathlib import Path
from typing import Any


def json_safe(value: Any) -> Any:
    """Convert plist values to JSON-safe values without losing byte identity."""
    if isinstance(value, bytes):
        return {"hex": value.hex()}
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def archive_sha256(path: Path) -> str:
    """Hash an archive in bounded-size chunks instead of loading it into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def component_record(identity: dict[str, Any], name: str) -> dict[str, Any] | None:
    components = identity.get("Manifest", {})
    if not isinstance(components, dict):
        return None
    component = components.get(name)
    if not isinstance(component, dict):
        return None
    info = component.get("Info", {})
    if not isinstance(info, dict):
        info = {}
    return {
        "path": info.get("Path"),
        "digest": json_safe(component.get("Digest")),
        "partial_digest": json_safe(component.get("PartialDigest")),
        "size": component.get("Size"),
        "metadata": json_safe(component),
    }


def inspect_archive(path: Path, include_sha256: bool = False) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"IPSW file does not exist: {path}")

    with zipfile.ZipFile(path, "r") as archive:
        try:
            manifest_bytes = archive.read("BuildManifest.plist")
        except KeyError as exc:
            raise ValueError("BuildManifest.plist was not found at the IPSW archive root") from exc

    try:
        manifest = plistlib.loads(manifest_bytes)
    except Exception as exc:
        raise ValueError(f"BuildManifest.plist could not be parsed: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ValueError("BuildManifest.plist root is not a dictionary")

    identities = manifest.get("BuildIdentities", [])
    if not isinstance(identities, list):
        raise ValueError("BuildIdentities is not an array")

    records = []
    for index, identity in enumerate(identities):
        if not isinstance(identity, dict):
            records.append({"index": index, "error": "BuildIdentity entry is not a dictionary"})
            continue
        info = identity.get("Info", {})
        if not isinstance(info, dict):
            info = {}
        records.append({
            "index": index,
            "identity_info": json_safe(info),
            "device_class": info.get("DeviceClass"),
            "supported_product_types": json_safe(info.get("SupportedProductTypes")),
            "ap_board_id": json_safe(info.get("ApBoardID")),
            "ap_chip_id": json_safe(info.get("ApChipID")),
            "kernel_cache": component_record(identity, "KernelCache"),
            "device_tree": component_record(identity, "DeviceTree"),
        })

    result = {
        "schema_version": 1,
        "archive": {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": archive_sha256(path) if include_sha256 else None,
        },
        "product_version": manifest.get("ProductVersion"),
        "product_build_version": manifest.get("ProductBuildVersion"),
        "build_identity_count": len(identities),
        "build_identities": records,
        "selection_policy": "No BuildIdentity is selected automatically; review each entry against the archive's intended device.",
        "limitations": [
            "This is a metadata report, not a compatibility assessment.",
            "A matching build number does not establish device compatibility.",
            "The report does not prove which XNU source revision produced a KernelCache.",
            "No archive contents are extracted or executed.",
        ],
    }
    return json_safe(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ipsw", type=Path, help="path to a local IPSW ZIP archive")
    parser.add_argument("--sha256", action="store_true", help="also calculate the IPSW archive SHA-256")
    args = parser.parse_args()

    try:
        report = inspect_archive(args.ipsw, include_sha256=args.sha256)
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
