import json
import tempfile
import unittest
from pathlib import Path

from tools.search_kext_inventory import (
    InventoryError,
    classify_path,
    find_record_matches,
    load_inventory,
    normalize,
    scan_inventory,
)


class SearchKextInventoryTests(unittest.TestCase):
    def setUp(self):
        self.paths = []

    def tearDown(self):
        for path in self.paths:
            path.unlink(missing_ok=True)

    def make_file(self, data):
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        )
        with handle:
            json.dump(data, handle)
        path = Path(handle.name)
        self.paths.append(path)
        return path

    def test_normalize_ignores_case_and_punctuation(self):
        self.assertEqual(
            normalize("Apple-Hurricane_ErrorHandler"),
            "applehurricaneerrorhandler",
        )

    def test_search_finds_identity_personality_and_dependency_paths(self):
        record = {
            "id": "com.apple.driver.AppleHurricaneErrorHandler",
            "name": "AppleHurricaneErrorHandler.kext",
            "io_kit_personalities": {
                "AppleT8010PlatformErrorHandler": {
                    "IONameMatch": "error-handler,t8010",
                }
            },
            "os_bundle_libraries": {
                "com.apple.driver.AppleHurricaneErrorHandler": "1.0",
            },
        }
        matches = find_record_matches(
            record, ("hurricane", "errorhandler", "platformerror", "t8010")
        )
        categories = {match["category"] for match in matches}
        self.assertEqual(categories, {"identity", "personality", "dependency"})
        paths = {match["path"] for match in matches}
        self.assertIn('$[root]["id"]', paths)
        self.assertTrue(any("io_kit_personalities" in path for path in paths))
        self.assertTrue(any("os_bundle_libraries" in path for path in paths))

    def test_classification_distinguishes_top_level_identity(self):
        self.assertEqual(classify_path('$[root]["id"]'), "identity")
        self.assertEqual(
            classify_path(
                '$[root]["io_kit_personalities"]["Personality"]["IONameMatch"]'
            ),
            "personality",
        )
        self.assertEqual(
            classify_path(
                '$[root]["os_bundle_libraries"]["com.apple.driver.X"]'
            ),
            "dependency",
        )

    def test_scan_report_keeps_target_and_donor_labels(self):
        target = self.make_file(
            [
                {"id": "com.apple.driver.AppleT8010", "name": "AppleT8010.kext"},
                {"id": "com.apple.iokit.IOKit", "name": "IOKit.kext"},
            ]
        )
        report = scan_inventory(target, "TARGET 19H422", ("t8010",))
        self.assertIn("TARGET 19H422", report)
        self.assertIn("Top-level KEXT records scanned: 2", report)
        self.assertIn("Records with one or more keyword matches: 1", report)
        self.assertIn("com.apple.driver.AppleT8010", report)
        self.assertIn("keyword hit is a metadata search lead only", report)

    def test_non_array_inventory_is_rejected(self):
        path = self.make_file({"records": []})
        with self.assertRaises(InventoryError):
            load_inventory(path)

    def test_empty_terms_are_rejected(self):
        path = self.make_file([])
        with self.assertRaises(InventoryError):
            scan_inventory(path, "EMPTY", ("---",))


if __name__ == "__main__":
    unittest.main()
