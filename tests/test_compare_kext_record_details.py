import json
import tempfile
import unittest
from pathlib import Path

from tools.compare_kext_record_details import (
    DEFAULT_PAIRS,
    InventoryError,
    MISSING,
    compare_records,
    escape_pointer_token,
    iter_differences,
    load_selected_records,
    parse_pairs,
)


SAME_ID = "com.apple.driver.AppleA7IOP"
OTHER_ID = "com.apple.driver.AppleMonsoonErrorHandler"


def write_json(data):
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".json", delete=False
    )
    with handle:
        json.dump(data, handle)
    return Path(handle.name)


class CompareKextRecordDetailsTests(unittest.TestCase):
    def setUp(self):
        self.paths = []

    def tearDown(self):
        for path in self.paths:
            path.unlink(missing_ok=True)

    def make_file(self, data):
        path = write_json(data)
        self.paths.append(path)
        return path

    def test_loads_only_requested_exact_top_level_ids(self):
        path = self.make_file([
            {"id": SAME_ID, "version": "1"},
            {"id": "com.example.Other", "os_bundle_libraries": {SAME_ID: "1"}},
        ])
        records = load_selected_records(path, [SAME_ID])
        self.assertEqual(set(records), {SAME_ID})
        self.assertEqual(records[SAME_ID]["version"], "1")

    def test_duplicate_selected_top_level_id_is_rejected(self):
        path = self.make_file([{"id": SAME_ID}, {"id": SAME_ID}])
        with self.assertRaises(InventoryError):
            load_selected_records(path, [SAME_ID])

    def test_duplicate_unselected_id_is_ignored(self):
        path = self.make_file([{"id": "x"}, {"id": "x"}, {"id": SAME_ID}])
        records = load_selected_records(path, [SAME_ID])
        self.assertEqual(set(records), {SAME_ID})

    def test_non_array_root_is_rejected(self):
        path = self.make_file({"records": []})
        with self.assertRaises(InventoryError):
            load_selected_records(path, [SAME_ID])

    def test_malformed_json_is_rejected(self):
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        )
        path = Path(handle.name)
        self.paths.append(path)
        with handle:
            handle.write("{bad-json")
        with self.assertRaises(InventoryError):
            load_selected_records(path, [SAME_ID])

    def test_missing_key_is_distinct_from_json_null(self):
        diffs = list(iter_differences({"key": None}, {}))
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0][0], "$/key")
        self.assertIsNone(diffs[0][1])
        self.assertIs(diffs[0][2], MISSING)

    def test_bool_and_integer_are_compared_as_different_json_types(self):
        diffs = list(iter_differences({"value": True}, {"value": 1}))
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0][0], "$/value")

    def test_nested_dict_changes_have_stable_paths(self):
        target = {"io_kit_personalities": {"Personality": {"IONameMatch": "x,t8010"}}}
        donor = {"io_kit_personalities": {"Personality": {"IONameMatch": "x,t8015"}}}
        diffs = list(iter_differences(target, donor))
        self.assertEqual(diffs, [(
            "$/io_kit_personalities/Personality/IONameMatch",
            "x,t8010",
            "x,t8015",
        )])

    def test_list_elements_and_length_are_compared_by_index(self):
        diffs = list(iter_differences({"items": ["a", "b"]}, {"items": ["a", "c", "d"]}))
        self.assertIn("$/items/#length", [item[0] for item in diffs])
        self.assertIn("$/items/1", [item[0] for item in diffs])
        self.assertIn("$/items/2", [item[0] for item in diffs])

    def test_json_pointer_tokens_are_escaped(self):
        self.assertEqual(escape_pointer_token("a/b~c"), "a~1b~0c")
        diffs = list(iter_differences({"a/b": 1}, {"a/b": 2}))
        self.assertEqual(diffs[0][0], "$/a~1b")

    def test_identical_records_have_no_difference(self):
        record = {"id": SAME_ID, "nested": {"v": [1, 2, None]}}
        report = compare_records({SAME_ID: record}, {SAME_ID: record}, [(SAME_ID, SAME_ID)])
        self.assertIn("JSON field differences: (none)", report)
        self.assertIn("Total differing JSON paths: 0", report)

    def test_report_compares_differently_named_counterparts(self):
        target = {SAME_ID: {"id": SAME_ID, "IONameMatch": "cpu-error-handler,hurricane"}}
        donor = {OTHER_ID: {"id": OTHER_ID, "IONameMatch": "cpu-error-handler,monsoon"}}
        report = compare_records(target, donor, [(SAME_ID, OTHER_ID)])
        self.assertIn("TARGET com.apple.driver.AppleA7IOP", report)
        self.assertIn("DONOR com.apple.driver.AppleMonsoonErrorHandler", report)
        self.assertIn("cpu-error-handler,hurricane", report)
        self.assertIn("cpu-error-handler,monsoon", report)

    def test_absent_record_is_reported_as_inventory_only(self):
        report = compare_records({}, {OTHER_ID: {"id": OTHER_ID}}, [(SAME_ID, OTHER_ID)])
        self.assertIn("TARGET: ABSENT from this JSON inventory", report)
        self.assertIn("Recursive comparison: skipped", report)

    def test_default_and_custom_pairs(self):
        self.assertEqual(parse_pairs(None), DEFAULT_PAIRS)
        self.assertEqual(parse_pairs([[SAME_ID, OTHER_ID]]), ((SAME_ID, OTHER_ID),))

    def test_pair_generator_is_counted_before_iteration(self):
        record = {"id": SAME_ID}
        report = compare_records(
            {SAME_ID: record},
            {SAME_ID: record},
            (pair for pair in [(SAME_ID, SAME_ID)]),
        )
        self.assertIn("Record pairs requested: 1", report)

    def test_empty_custom_pair_is_rejected(self):
        with self.assertRaises(InventoryError):
            parse_pairs([["", OTHER_ID]])


if __name__ == "__main__":
    unittest.main()
