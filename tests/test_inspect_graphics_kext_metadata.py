import json
import tempfile
import unittest
from pathlib import Path

from tools.inspect_graphics_kext_metadata import (
    DEFAULT_PAIRS,
    InventoryError,
    build_report,
    load_selected_records,
    parse_pairs,
    project_record,
)


AGX_TARGET = "com.apple.AGXG9P"
AGX_DONOR = "com.apple.AGXG10P"
IOGPU = "com.apple.iokit.IOGPUFamily"


def write_json(data):
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".json", delete=False
    )
    with handle:
        json.dump(data, handle)
    return Path(handle.name)


class InspectGraphicsKextMetadataTests(unittest.TestCase):
    def setUp(self):
        self.paths = []

    def tearDown(self):
        for path in self.paths:
            path.unlink(missing_ok=True)

    def make_file(self, data):
        path = write_json(data)
        self.paths.append(path)
        return path

    def test_defaults_include_agx_iogpu_and_a7iop_pairs(self):
        self.assertEqual(
            DEFAULT_PAIRS,
            (
                (AGX_TARGET, AGX_DONOR),
                (IOGPU, IOGPU),
                ("com.apple.driver.AppleA7IOP", "com.apple.driver.AppleA7IOP"),
            ),
        )

    def test_loads_only_exact_top_level_ids(self):
        path = self.make_file([
            {"id": AGX_TARGET, "version": "190.23"},
            {"id": "com.example.Other", "os_bundle_libraries": {AGX_TARGET: "1"}},
        ])
        records = load_selected_records(path, [AGX_TARGET])
        self.assertEqual(set(records), {AGX_TARGET})
        self.assertEqual(records[AGX_TARGET]["version"], "190.23")

    def test_duplicate_selected_id_is_rejected(self):
        path = self.make_file([{"id": AGX_TARGET}, {"id": AGX_TARGET}])
        with self.assertRaises(InventoryError):
            load_selected_records(path, [AGX_TARGET])

    def test_duplicate_unselected_id_is_ignored(self):
        path = self.make_file([
            {"id": "unselected"},
            {"id": "unselected"},
            {"id": AGX_TARGET},
        ])
        self.assertEqual(set(load_selected_records(path, [AGX_TARGET])), {AGX_TARGET})

    def test_non_array_root_is_rejected(self):
        path = self.make_file({"records": []})
        with self.assertRaises(InventoryError):
            load_selected_records(path, [AGX_TARGET])

    def test_malformed_json_is_rejected(self):
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        )
        path = Path(handle.name)
        self.paths.append(path)
        with handle:
            handle.write("{bad-json")
        with self.assertRaises(InventoryError):
            load_selected_records(path, [AGX_TARGET])

    def test_project_record_preserves_dependency_and_personality_values(self):
        record = {
            "id": AGX_TARGET,
            "version": "190.23",
            "os_bundle_libraries": {"com.apple.iokit.IOGPUFamily": ""},
            "io_kit_personalities": {
                "AGXG9P_A0": {
                    "IONameMatch": "gpu,t8010",
                    "MetalPluginName": "AGXMetalA10",
                    "IOProbeScore": None,
                }
            },
            "unselected_large_field": "must not be copied",
        }
        projected = project_record(record)
        self.assertEqual(
            projected["os_bundle_libraries"]["com.apple.iokit.IOGPUFamily"], ""
        )
        personality = projected["io_kit_personalities"]["AGXG9P_A0"]
        self.assertEqual(personality["IONameMatch"], "gpu,t8010")
        self.assertEqual(personality["MetalPluginName"], "AGXMetalA10")
        self.assertIsNone(personality["IOProbeScore"])
        self.assertNotIn("unselected_large_field", projected)

    def test_missing_fields_are_not_synthesized(self):
        projected = project_record({"id": AGX_TARGET})
        self.assertEqual(projected, {"id": AGX_TARGET})

    def test_build_report_marks_absent_records_without_guessing(self):
        report = build_report(
            {AGX_TARGET: {"id": AGX_TARGET}},
            {},
            [(AGX_TARGET, AGX_DONOR)],
            "/tmp/19H422-kexts.json",
            "/tmp/20H392-kexts.json",
        )
        pair = report["pairs"][0]
        self.assertEqual(pair["target"]["status"], "PRESENT")
        self.assertEqual(pair["donor"]["status"], "ABSENT_FROM_INVENTORY")
        self.assertIsNone(pair["donor"]["metadata"])
        self.assertEqual(report["target_inventory"], "19H422-kexts.json")
        self.assertEqual(report["donor_inventory"], "20H392-kexts.json")

    def test_build_report_preserves_same_id_target_donor_pair(self):
        record = {"id": IOGPU, "version": "35.29"}
        report = build_report(
            {IOGPU: record},
            {IOGPU: record},
            [(IOGPU, IOGPU)],
            "target.json",
            "donor.json",
        )
        self.assertEqual(report["pairs"][0]["target_id"], IOGPU)
        self.assertEqual(report["pairs"][0]["donor_id"], IOGPU)
        self.assertEqual(report["pairs"][0]["target"]["metadata"]["version"], "35.29")

    def test_default_and_custom_pair_parsing(self):
        self.assertEqual(parse_pairs(None), DEFAULT_PAIRS)
        self.assertEqual(parse_pairs([[AGX_TARGET, AGX_DONOR]]), ((AGX_TARGET, AGX_DONOR),))

    def test_empty_custom_pair_is_rejected(self):
        with self.assertRaises(InventoryError):
            parse_pairs([["", AGX_DONOR]])


if __name__ == "__main__":
    unittest.main()
