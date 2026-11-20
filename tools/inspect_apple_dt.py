#!/usr/bin/env python3
"""Safely inspect selected, non-identifying fields in an Apple flattened DeviceTree.

The input is a decompressed Apple DeviceTree component. This parser follows the
node/property layout used by the pinned public Ios-emul survey parser:
little-endian u32 property/node counts, 32-byte property names, a u32 property
length/flags word, four-byte value alignment, then recursive child nodes.

It intentionally emits only an allowlist of platform-relevant fields. It does
not dump serial numbers, MAC addresses, chip identifiers, NVRAM, boot nonces,
random seeds, or arbitrary property values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

MAX_NODES = 10_000
MAX_PROPERTIES_PER_NODE = 2_000
MAX_DEPTH = 64
MAX_INPUT_BYTES = 64 * 1024 * 1024

SELECTED_PATHS = (
    "/",
    "/cpus",
    "/cpus/cpu0",
    "/cpus/cpu1",
    "/memory",
    "/pram",
    "/vram",
    "/chosen",
    "/chosen/memory-map",
    "/arm-io",
    "/arm-io/aic",
    "/arm-io/aic-timebase",
    "/arm-io/gpio",
    "/arm-io/aop-gpio",
    "/arm-io/spi2",
    "/arm-io/spi2/multi-touch",
    "/arm-io/mipi-dsim",
    "/arm-io/mipi-dsim/lcd",
    "/arm-io/disp0",
    "/arm-io/i2c0",
    "/arm-io/i2c0/display-pmu",
    "/arm-io/i2c0/lm3539",
)

STRING_PROPERTIES = {
    "name",
    "compatible",
    "device_type",
    "state",
    "interrupt-controller",
    "target-type",
    "model",
}
INTEGER_PROPERTIES = {
    "#address-cells",
    "#size-cells",
    "#interrupt-cells",
    "#main-cpus",
    "#shared-timestamps",
    "aic-version",
    "cpu-id",
    "cpu-version",
    "interrupt-parent",
    "clock-frequency",
    "timebase-frequency",
    "bus-frequency",
    "memory-frequency",
    "peripheral-frequency",
    "fixed-frequency",
    "usbphy-frequency",
}
RAW_PROPERTIES = {"reg", "ranges", "interrupts"}
SELECTED_PROPERTIES = STRING_PROPERTIES | INTEGER_PROPERTIES | RAW_PROPERTIES


class DeviceTreeFormatError(ValueError):
    """Raised when the flattened DeviceTree is truncated or malformed."""


def _decode_strings(value: bytes) -> list[str]:
    return [
        item.decode("utf-8", errors="replace")
        for item in value.split(b"\x00")
        if item
    ]


def _numeric_views(value: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {"length_bytes": len(value), "hex": value.hex()}
    if len(value) % 4 == 0:
        result["u32_le_cells"] = [
            struct.unpack_from("<I", value, offset)[0]
            for offset in range(0, len(value), 4)
        ]
    if len(value) % 8 == 0:
        result["u64_le_words"] = [
            struct.unpack_from("<Q", value, offset)[0]
            for offset in range(0, len(value), 8)
        ]
    return result


def parse_tree(data: bytes) -> dict[str, Any]:
    """Parse the complete Apple flattened tree with strict bounds checks."""
    if not data:
        raise DeviceTreeFormatError("Input is empty.")
    if len(data) > MAX_INPUT_BYTES:
        raise DeviceTreeFormatError(
            f"Input exceeds the {MAX_INPUT_BYTES}-byte safety limit."
        )

    cursor = 0
    node_count = 0

    def parse_node(depth: int) -> dict[str, Any]:
        nonlocal cursor, node_count

        if depth > MAX_DEPTH:
            raise DeviceTreeFormatError(
                f"Tree depth exceeds the {MAX_DEPTH}-level safety limit."
            )
        if cursor + 8 > len(data):
            raise DeviceTreeFormatError(
                f"Truncated node header at byte offset {cursor}."
            )

        node_start = cursor
        property_count, child_count = struct.unpack_from("<II", data, cursor)
        cursor += 8
        node_count += 1

        if node_count > MAX_NODES:
            raise DeviceTreeFormatError(
                f"Node count exceeds the {MAX_NODES}-node safety limit."
            )
        if property_count > MAX_PROPERTIES_PER_NODE:
            raise DeviceTreeFormatError(
                f"Node at {node_start} has an unreasonable property count."
            )
        if child_count > MAX_NODES:
            raise DeviceTreeFormatError(
                f"Node at {node_start} has an unreasonable child count."
            )

        properties: dict[str, bytes] = {}
        for _ in range(property_count):
            if cursor + 36 > len(data):
                raise DeviceTreeFormatError(
                    f"Truncated property header at byte offset {cursor}."
                )

            raw_name = data[cursor:cursor + 32]
            cursor += 32
            name_bytes = raw_name.split(b"\x00", 1)[0]
            if not name_bytes:
                raise DeviceTreeFormatError(
                    f"Empty property name in node at {node_start}."
                )
            name = name_bytes.decode("ascii", errors="strict")

            raw_length = struct.unpack_from("<I", data, cursor)[0]
            cursor += 4
            value_length = raw_length & 0x7FFFFFFF
            padded_length = (value_length + 3) & ~3

            if cursor + padded_length > len(data):
                raise DeviceTreeFormatError(
                    f"Property {name!r} at node {node_start} extends beyond input."
                )
            if name in properties:
                raise DeviceTreeFormatError(
                    f"Duplicate property {name!r} in node at {node_start}."
                )

            properties[name] = data[cursor:cursor + value_length]
            cursor += padded_length

        node = {
            "properties": properties,
            "children": [],
            "start_offset": node_start,
        }

        for _ in range(child_count):
            node["children"].append(parse_node(depth + 1))

        node["end_offset"] = cursor
        return node

    root = parse_node(0)
    if cursor != len(data):
        raise DeviceTreeFormatError(
            f"Parser consumed {cursor} of {len(data)} bytes; "
            f"{len(data) - cursor} trailing bytes remain."
        )

    root["_node_count"] = node_count
    root["_parsed_bytes"] = cursor
    return root


def index_tree(root: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build a path index without materializing arbitrary property values."""
    result: dict[str, dict[str, Any]] = {}

    def visit(node: dict[str, Any], path: str, root_node: bool = False) -> None:
        name_value = node["properties"].get("name", b"")
        node_name = _decode_strings(name_value)
        name = node_name[0] if node_name else ("?" if not root_node else "/")

        if root_node:
            current_path = "/"
        else:
            current_path = (path.rstrip("/") + "/" + name) if path != "/" else "/" + name

        result[current_path] = node
        for child in node["children"]:
            visit(child, current_path)

    visit(root, "/", root_node=True)
    return result


def _render_property(name: str, value: bytes) -> dict[str, Any]:
    if name in STRING_PROPERTIES:
        return {
            "length_bytes": len(value),
            "strings": _decode_strings(value),
        }
    if name in INTEGER_PROPERTIES or name in RAW_PROPERTIES:
        return _numeric_views(value)
    raise ValueError(f"Property {name!r} is not on the output allowlist.")


def inspect_tree(data: bytes) -> dict[str, Any]:
    """Return a privacy-filtered inventory of selected platform nodes."""
    parsed = parse_tree(data)
    indexed = index_tree(parsed)

    selected_nodes: list[dict[str, Any]] = []
    for path in SELECTED_PATHS:
        node = indexed.get(path)
        if node is None:
            selected_nodes.append({"path": path, "present": False})
            continue

        properties: dict[str, Any] = {}
        for name in sorted(SELECTED_PROPERTIES):
            value = node["properties"].get(name)
            if value is not None:
                properties[name] = _render_property(name, value)

        child_names = []
        if path in {"/", "/arm-io", "/chosen", "/cpus"}:
            for child in node["children"]:
                child_name = _decode_strings(child["properties"].get("name", b""))
                if child_name:
                    child_names.append(child_name[0])

        selected_nodes.append({
            "path": path,
            "present": True,
            "child_count": len(node["children"]),
            "children": child_names,
            "properties": properties,
        })

    return {
        "schema_version": 1,
        "format": "Apple flattened DeviceTree node/property stream",
        "input_size_bytes": len(data),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "parsed_bytes": parsed["_parsed_bytes"],
        "node_count_including_root": parsed["_node_count"],
        "node_count_excluding_root": parsed["_node_count"] - 1,
        "trailing_bytes": 0,
        "privacy": {
            "mode": "allowlist",
            "arbitrary_properties_emitted": False,
            "unique_identifiers_and_machine_specific_blobs_emitted": False,
        },
        "integer_interpretation": (
            "Raw hex is authoritative. Little-endian numeric views are supplied "
            "for comparison with the pinned XNU consumers, which read selected "
            "properties through native uintptr_t/uint32_t pointers on ARM64. "
            "Do not treat every reg/ranges property as a generic FDT tuple."
        ),
        "nodes": selected_nodes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("device_tree", type=Path, help="decompressed Apple DeviceTree file")
    parser.add_argument("--output", type=Path, help="optional path for the privacy-filtered JSON report")
    args = parser.parse_args()

    try:
        data = args.device_tree.read_bytes()
        report = inspect_tree(data)
    except (OSError, UnicodeError, DeviceTreeFormatError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
