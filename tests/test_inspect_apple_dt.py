"""Tests for the privacy-filtered Apple DeviceTree inspector."""
import hashlib
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_apple_dt import DeviceTreeFormatError, inspect_tree, parse_tree


def prop(name: str, value: bytes) -> bytes:
    encoded = name.encode("ascii")
    if len(encoded) > 31:
        raise ValueError("property name too long for fixture")
    name_field = encoded + b"\x00" * (32 - len(encoded))
    value_header = struct.pack("<I", len(value))
    padding = b"\x00" * ((-len(value)) % 4)
    return name_field + value_header + value + padding


def node(properties: dict[str, bytes], children: list[bytes] | None = None) -> bytes:
    children = children or []
    header = struct.pack("<II", len(properties), len(children))
    body = b"".join(prop(name, value) for name, value in properties.items())
    return header + body + b"".join(children)


class AppleDeviceTreeInspectorTests(unittest.TestCase):
    def fixture(self):
        cpu0 = node({
            "name": b"cpu0\x00",
            "device_type": b"cpu\x00",
            "state": b"running\x00",
            "compatible": b"apple,hurricane-zephyr\x00ARM,v8\x00",
            "reg": struct.pack("<I", 0),
            "timebase-frequency": struct.pack("<Q", 0),
        })
        mipi_lcd = node({
            "name": b"lcd\x00",
            "compatible": b"lcd,pinot\x00",
            "device_type": b"lcd\x00",
        })
        mipi_dsim = node({
            "name": b"mipi-dsim\x00",
            "compatible": b"mipi-dsim-1,synopsys\x00",
        }, [mipi_lcd])
        display = node({
            "name": b"disp0\x00",
            "compatible": b"disp0,t8010\x00",
            "backlight-control": b"",
            "serial-number": b"PRIVATE-DISPLAY-ID\x00",
        })
        aic = node({
            "name": b"aic\x00",
            "compatible": b"aic,1\x00",
            "device_type": b"interrupt-controller\x00",
            "interrupt-controller": b"master\x00",
            "#interrupt-cells": struct.pack("<I", 1),
            "#main-cpus": struct.pack("<I", 2),
            "aic-version": struct.pack("<I", 2),
            "reg": struct.pack("<QQ", 0x0E100000, 0x8000),
        })
        arm_io = node({
            "name": b"arm-io\x00",
            "compatible": b"arm-io,t8010\x00",
            "device_type": b"t8010-io\x00",
            "#address-cells": struct.pack("<I", 2),
            "#size-cells": struct.pack("<I", 2),
            "ranges": struct.pack("<QQQ", 0, 0x200000000, 0x100000000),
        }, [aic, mipi_dsim, display])
        chosen = node({
            "name": b"chosen\x00",
            "embedded-panic-log-size": struct.pack("<I", 0x80000),
            "serial-number": b"PRIVATE-TEST-ID\x00",
        })
        cpus = node({
            "name": b"cpus\x00",
            "#address-cells": struct.pack("<I", 1),
            "#size-cells": struct.pack("<I", 0),
        }, [cpu0])
        root = node({
            "name": b"device-tree\x00",
            "compatible": b"D10AP\x00iPhone9,1\x00AppleARM\x00",
            "serial-number": b"PRIVATE-ROOT-ID\x00",
            "#address-cells": struct.pack("<I", 2),
            "#size-cells": struct.pack("<I", 2),
        }, [chosen, cpus, arm_io])
        return root

    def test_parses_entire_tree_and_indexes_nodes(self):
        raw = self.fixture()
        parsed = parse_tree(raw)
        self.assertEqual(parsed["_node_count"], 9)
        report = inspect_tree(raw)
        self.assertEqual(report["parsed_bytes"], len(raw))
        self.assertEqual(report["node_count_including_root"], 9)
        nodes = {item["path"]: item for item in report["nodes"]}
        self.assertTrue(nodes["/arm-io/aic"]["present"])
        self.assertEqual(
            nodes["/arm-io/aic"]["properties"]["#main-cpus"]["u32_le_cells"],
            [2],
        )
        self.assertEqual(
            nodes["/arm-io/mipi-dsim"]["properties"]["compatible"]["strings"],
            ["mipi-dsim-1,synopsys"],
        )
        self.assertEqual(
            nodes["/arm-io/disp0"]["properties"]["backlight-control"],
            {
                "present": True,
                "length_bytes": 0,
                "hex": "",
                "zero_length_marker": True,
            },
        )

    def test_report_does_not_emit_unique_identifiers(self):
        report = inspect_tree(self.fixture())
        rendered = str(report)
        self.assertNotIn("PRIVATE-TEST-ID", rendered)
        self.assertNotIn("PRIVATE-ROOT-ID", rendered)
        self.assertNotIn("serial-number", rendered)
        self.assertNotIn("PRIVATE-DISPLAY-ID", rendered)
        self.assertFalse(report["privacy"]["arbitrary_properties_emitted"])

    def test_rejects_truncated_node_header(self):
        with self.assertRaisesRegex(DeviceTreeFormatError, "Truncated node header"):
            parse_tree(bytes([1, 2, 3]))

    def test_rejects_property_that_runs_past_file(self):
        malformed = struct.pack("<II", 1, 0) + b"test" + b"\x00" * 28 + struct.pack("<I", 100)
        with self.assertRaisesRegex(DeviceTreeFormatError, "extends beyond input"):
            parse_tree(malformed)

    def test_rejects_trailing_bytes(self):
        with self.assertRaisesRegex(DeviceTreeFormatError, "trailing bytes remain"):
            parse_tree(self.fixture() + b"\x00")

    def test_rejects_duplicate_property_names(self):
        encoded = (
            struct.pack("<II", 2, 0)
            + prop("name", b"device-tree\x00")
            + prop("name", b"duplicate\x00")
        )
        with self.assertRaisesRegex(DeviceTreeFormatError, "Duplicate property"):
            parse_tree(encoded)

    def test_sha256_is_recorded(self):
        raw = self.fixture()
        report = inspect_tree(raw)
        self.assertEqual(report["input_sha256"], hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    unittest.main()
