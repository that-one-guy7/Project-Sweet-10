import json
import tempfile
import unittest
from pathlib import Path

from tools.compare_kext_metadata import (
    InventoryError,
    compare,
    load_inventory,
    libraries,
    personalities,
)


AIC = "com.apple.driver.AppleInterruptController"
ARM_PLATFORM = "com.apple.driver.AppleARMPlatform"
T8010_PMGR = "com.apple.driver.AppleT8010PMGR"


def write_json(data):
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".json", delete=False
    )
    with handle:
        json.dump(data, handle)
    return Path(handle.name)


class CompareKextMetadataTests(unittest.TestCase):
    def setUp(self):
        self.paths = []

    def tearDown(self):
        for path in self.paths:
            path.unlink(missing_ok=True)

    def make_file(self, data):
        path = write_json(data)
        self.paths.append(path)
        return path

    def test_exact_top_level_bundle_ids_ignore_dependency_mentions(self):
        path = self.make_file([
            {"id": AIC, "version": "1.0.0d1"},
            {
                "id": "com.example.Unrelated",
                "os_bundle_libraries": {ARM_PLATFORM: "1.0.0"},
            },
        ])
        inventory = load_inventory(path)
        self.assertEqual(set(inventory), {AIC})
        self.assertNotIn(ARM_PLATFORM, inventory)

    def test_personality_and_library_fields_are_preserved(self):
        record = {
            "id": AIC,
            "io_kit_personalities": {
                "AppleInterruptController": {
                    "IOClass": "AppleInterruptController",
                    "IONameMatch": "aic,1",
                    "IOProviderClass": "AppleARMIODevice",
                    "IgnoredPrivateKey": "not emitted",
                }
            },
            "os_bundle_libraries": {
                ARM_PLATFORM: "1.0.0",
                "com.apple.kpi.iokit": "8.0",
            },
        }
        self.assertEqual(
            personalities(record)["AppleInterruptController"],
            {
                "IOClass": "AppleInterruptController",
                "IONameMatch": "aic,1",
                "IOProviderClass": "AppleARMIODevice",
            },
        )
        self.assertEqual(
            libraries(record),
            {
                ARM_PLATFORM: "1.0.0",
                "com.apple.kpi.iokit": "8.0",
            },
        )

    def test_comparison_reports_personality_and_dependency_differences(self):
        target = {
            AIC: {
                "id": AIC,
                "version": "1.0.0d1",
                "io_kit_personalities": {
                    "AppleInterruptController": {
                        "IONameMatch": "aic,1",
                        "IOProviderClass": "AppleARMIODevice",
                    }
                },
                "os_bundle_libraries": {
                    ARM_PLATFORM: "1.0.0",
                    "com.apple.kpi.iokit": "8.0",
                },
            }
        }
        donor = {
            AIC: {
                "id": AIC,
                "version": "1.0.0",
                "io_kit_personalities": {
                    "AppleInterruptController": {
                        "IONameMatch": "aic,1",
                        "IOProviderClass": "IOPlatformDevice",
                    }
                },
                "os_bundle_libraries": {
                    ARM_PLATFORM: "1.1.0",
                    "com.apple.kpi.iokit": "18.0",
                    "com.apple.kpi.mach": "18.0",
                },
            }
        }
        report = compare(target, donor)
        self.assertIn("AppleInterruptController", report)
        self.assertIn("IOProviderClass", report)
        self.assertIn("com.apple.kpi.mach", report)
        self.assertIn("1.0.0d1", report)
        self.assertIn("1.0.0", report)

    def test_duplicate_selected_bundle_id_is_rejected(self):
        path = self.make_file([
            {"id": T8010_PMGR, "version": "1"},
            {"id": T8010_PMGR, "version": "2"},
        ])
        with self.assertRaises(InventoryError):
            load_inventory(path)

    def test_non_array_root_is_rejected(self):
        path = self.make_file({"records": []})
        with self.assertRaises(InventoryError):
            load_inventory(path)

    def test_malformed_json_is_rejected(self):
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        )
        path = Path(handle.name)
        self.paths.append(path)
        with handle:
            handle.write("{not-json")
        with self.assertRaises(InventoryError):
            load_inventory(path)


if __name__ == "__main__":
    unittest.main()
