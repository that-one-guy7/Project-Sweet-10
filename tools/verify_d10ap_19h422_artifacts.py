#!/usr/bin/env python3
"""Verify the supplied iPhone9,1 / D10AP / iOS 15.8.8 (19H422) artifacts.

This is a read-only evidence checker. It validates hashes and BuildManifest
identity metadata, then inspects the IM4P wrapper and compression marker.
It does not decompress or parse the Apple DeviceTree payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import sys
from pathlib import Path
from typing import Any

EXPECTED_MANIFEST_SHA256 = (
    "1eb426fd4da23fc8d133a06c15f697924537d09b9dc192e49e23accf8dd9d015"
)
EXPECTED_DEVICE_TREE_SHA256 = (
    "906a2708d3d15828c447ee1d7211f628dfeec7653a343384f3845153178c5906"
)
EXPECTED_PRODUCT_VERSION = "15.8.8"
EXPECTED_BUILD = "19H422"
EXPECTED_DEVICE_CLASS = "d10ap"
EXPECTED_DEVICE_TREE_PATH = "Firmware/all_flash/DeviceTree.d10ap.im4p"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_der_tlv(data: bytes, offset: int = 0) -> tuple[int, bytes, int]:
    """Read one definite-length DER TLV and return (tag, value, next_offset)."""
    if offset < 0 or offset + 2 > len(data):
        raise ValueError("Truncated DER tag/length.")

    tag = data[offset]
    first_length = data[offset + 1]
    cursor = offset + 2

    if tag & 0x1F == 0x1F:
        raise ValueError("High-tag-number DER form is not supported by this inspector.")

    if first_length & 0x80:
        length_octets = first_length & 0x7F
        if length_octets == 0:
            raise ValueError("Indefinite-length encoding is not valid DER.")
        if length_octets > 8 or cursor + length_octets > len(data):
            raise ValueError("Invalid or truncated DER length.")
        length = int.from_bytes(data[cursor:cursor + length_octets], "big")
        cursor += length_octets
        if length < 128:
            raise ValueError("Non-minimal DER long-form length.")
    else:
        length = first_length

    end = cursor + length
    if end > len(data):
        raise ValueError("DER element extends beyond the input buffer.")
    return tag, data[cursor:end], end


def parse_im4p_header(component: bytes) -> tuple[dict[str, Any], bytes]:
    """Validate the outer IM4P envelope without decompressing its payload."""
    outer_tag, outer_body, outer_end = read_der_tlv(component, 0)
    if outer_tag != 0x30 or outer_end != len(component):
        raise ValueError("DeviceTree component is not one complete DER SEQUENCE.")

    fields: list[tuple[int, bytes]] = []
    offset = 0
    while offset < len(outer_body):
        tag, value, offset = read_der_tlv(outer_body, offset)
        fields.append((tag, value))

    if len(fields) < 4:
        raise ValueError("IM4P envelope has fewer than four required fields.")
    if fields[0] != (0x16, b"IM4P"):
        raise ValueError("IM4P envelope marker is missing.")
    if fields[1] != (0x16, b"dtre"):
        raise ValueError("IM4P component type is not dtre.")
    if fields[2][0] != 0x16:
        raise ValueError("IM4P description field is not an IA5String.")
    if fields[3][0] != 0x04:
        raise ValueError("IM4P payload field is not an OCTET STRING.")

    trailing_octet_strings = sum(1 for tag, _ in fields[4:] if tag == 0x04)
    if trailing_octet_strings:
        raise ValueError(
            "IM4P contains an additional OCTET STRING after its payload; "
            "the payload form is not accepted by this read-only verifier."
        )

    payload = fields[3][1]
    compression_magic = payload[:4]
    if compression_magic not in (b"bvx1", b"bvx2", b"bvxn", b"bvx-"):
        raise ValueError(
            "DeviceTree payload does not begin with a recognized LZFSE-family marker."
        )

    metadata = {
        "im4p_type": "IM4P",
        "component_type": "dtre",
        "description": fields[2][1].decode("ascii", errors="replace"),
        "payload_length_bytes": len(payload),
        "compression_marker": compression_magic.decode("ascii"),
        "compression_family": "LZFSE",
        "decompressed": False,
        "trailing_octet_string_count": trailing_octet_strings,
    }
    return metadata, payload


def inspect_artifacts(
    manifest_path: Path,
    device_tree_path: Path,
    expected_manifest_sha256: str = EXPECTED_MANIFEST_SHA256,
    expected_device_tree_sha256: str = EXPECTED_DEVICE_TREE_SHA256,
) -> dict[str, Any]:
    if not manifest_path.is_file():
        raise FileNotFoundError(f"BuildManifest file not found: {manifest_path}")
    if not device_tree_path.is_file():
        raise FileNotFoundError(f"DeviceTree component file not found: {device_tree_path}")

    manifest_bytes = manifest_path.read_bytes()
    component_bytes = device_tree_path.read_bytes()
    manifest_hash = sha256_bytes(manifest_bytes)
    component_hash = sha256_bytes(component_bytes)

    if manifest_hash != expected_manifest_sha256.lower():
        raise ValueError(
            "BuildManifest SHA-256 mismatch: "
            f"expected {expected_manifest_sha256.lower()}, got {manifest_hash}"
        )
    if component_hash != expected_device_tree_sha256.lower():
        raise ValueError(
            "DeviceTree component SHA-256 mismatch: "
            f"expected {expected_device_tree_sha256.lower()}, got {component_hash}"
        )

    try:
        manifest = plistlib.loads(manifest_bytes)
    except Exception as exc:
        raise ValueError(f"BuildManifest plist could not be parsed: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("BuildManifest root is not a dictionary.")

    product_version = manifest.get("ProductVersion")
    product_build = manifest.get("ProductBuildVersion")
    supported_products = manifest.get("SupportedProductTypes", [])
    if product_version != EXPECTED_PRODUCT_VERSION:
        raise ValueError(
            f"Unexpected ProductVersion: expected {EXPECTED_PRODUCT_VERSION}, got {product_version!r}"
        )
    if product_build != EXPECTED_BUILD:
        raise ValueError(
            f"Unexpected ProductBuildVersion: expected {EXPECTED_BUILD}, got {product_build!r}"
        )
    if not isinstance(supported_products, list) or "iPhone9,1" not in supported_products:
        raise ValueError("BuildManifest does not list iPhone9,1 in SupportedProductTypes.")

    identities = manifest.get("BuildIdentities")
    if not isinstance(identities, list):
        raise ValueError("BuildManifest BuildIdentities is missing or not an array.")

    d10_identities: list[dict[str, Any]] = []
    for index, identity in enumerate(identities):
        if not isinstance(identity, dict):
            continue
        info = identity.get("Info", {})
        if not isinstance(info, dict) or str(info.get("DeviceClass", "")).lower() != EXPECTED_DEVICE_CLASS:
            continue

        identity_manifest = identity.get("Manifest", {})
        if not isinstance(identity_manifest, dict):
            raise ValueError(f"D10AP BuildIdentity {index} has invalid Manifest.")
        device_tree = identity_manifest.get("DeviceTree", {})
        if not isinstance(device_tree, dict):
            raise ValueError(f"D10AP BuildIdentity {index} has no DeviceTree component record.")
        component_info = device_tree.get("Info", {})
        if not isinstance(component_info, dict):
            raise ValueError(f"D10AP BuildIdentity {index} has invalid DeviceTree Info.")
        component_path = component_info.get("Path")
        if component_path != EXPECTED_DEVICE_TREE_PATH:
            raise ValueError(
                f"D10AP BuildIdentity {index} points to unexpected DeviceTree path: {component_path!r}"
            )

        manifest_digest = device_tree.get("Digest")
        if not isinstance(manifest_digest, bytes) or len(manifest_digest) != 48:
            raise ValueError(
                f"D10AP BuildIdentity {index} DeviceTree Digest is not a 48-byte value."
            )
        kernel_cache = identity_manifest.get("KernelCache", {})
        if not isinstance(kernel_cache, dict):
            kernel_cache = {}
        kernel_info = kernel_cache.get("Info", {})
        if not isinstance(kernel_info, dict):
            kernel_info = {}

        d10_identities.append({
            "index": index,
            "restore_behavior": info.get("RestoreBehavior"),
            "variant": info.get("Variant"),
            "device_tree_path": component_path,
            "device_tree_manifest_digest": manifest_digest.hex(),
            "kernel_cache_path": kernel_info.get("Path"),
            "device_tree_personalize": component_info.get("Personalize"),
            "device_tree_is_firmware_payload": component_info.get("IsFirmwarePayload"),
        })

    behaviors = {entry["restore_behavior"] for entry in d10_identities}
    if behaviors != {"Erase", "Update"} or len(d10_identities) != 2:
        raise ValueError(
            "Expected exactly one D10AP Erase and one D10AP Update BuildIdentity; "
            f"found {d10_identities!r}"
        )

    manifest_digests = {entry["device_tree_manifest_digest"] for entry in d10_identities}
    if len(manifest_digests) != 1:
        raise ValueError("D10AP Erase and Update identities disagree on DeviceTree Digest.")

    component_sha384 = hashlib.sha384(component_bytes).hexdigest()
    expected_sha384 = next(iter(manifest_digests))
    if component_sha384 != expected_sha384:
        raise ValueError(
            "DeviceTree SHA-384 does not match the BuildManifest Digest field: "
            f"expected {expected_sha384}, got {component_sha384}"
        )

    im4p, _payload = parse_im4p_header(component_bytes)

    return {
        "verification": "PASS",
        "scope": "artifact identity and hash verification only; DeviceTree properties not parsed",
        "product_version": product_version,
        "product_build_version": product_build,
        "supported_product_types": supported_products,
        "build_identity_count": len(identities),
        "d10ap_build_identities": d10_identities,
        "buildmanifest": {
            "filename": manifest_path.name,
            "size_bytes": len(manifest_bytes),
            "sha256": manifest_hash,
        },
        "device_tree_component": {
            "filename": device_tree_path.name,
            "size_bytes": len(component_bytes),
            "sha256": component_hash,
            "sha384": component_sha384,
            "im4p": im4p,
        },
        "limitations": [
            "The full IPSW archive was not supplied or verified by this tool run.",
            "The LZFSE payload has not been decompressed by this tool.",
            "No DeviceTree node, property, address, interrupt, clock, or memory value is asserted.",
            "The iOS 15.8.8 DeviceTree is a target-hardware reference, not an iOS 16 kernel or userland image.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="path to BuildManifest-19H422.plist")
    parser.add_argument("--device-tree", required=True, type=Path, help="path to DeviceTree.d10ap.im4p")
    parser.add_argument("--output", type=Path, help="optional path to write the JSON report")
    parser.add_argument(
        "--extract-payload",
        type=Path,
        help="optional output path for the verified IM4P LZFSE payload (does not decompress it)",
    )
    args = parser.parse_args()

    try:
        report = inspect_artifacts(args.manifest, args.device_tree)
        if args.extract_payload:
            component_bytes = args.device_tree.read_bytes()
            _metadata, payload = parse_im4p_header(component_bytes)
            args.extract_payload.write_bytes(payload)
            report["extracted_lzfse_payload"] = {
                "path": str(args.extract_payload),
                "size_bytes": len(payload),
                "sha256": sha256_bytes(payload),
                "decompressed": False,
            }
    except (OSError, ValueError) as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
