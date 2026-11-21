"""Synthetic tests for the embedded-service inventory comparator."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compare_embedded_services import compare, load_inventory, write_csv


SCHEMA = "project-sweet-10.embedded-service-inventory.v1"


def inventory(bundles, **overrides):
    value = {
        "schema": SCHEMA,
        "bundles": bundles,
        "mach_service_providers": [],
        "scan_errors": [],
    }
    value.update(overrides)
    return value


def bundle(identifier, **values):
    record = {
        "bundle_identifier": identifier,
        "bundle_type": ".xpc",
        "bundle_executable": "Worker",
        "executable_state": "regular-file",
        "package_type": "XPC!",
        "minimum_os_version": "15.8",
        "supported_platforms": ["iPhoneOS"],
        "extension": None,
        "xpc_service": None,
        "mach_services": [],
        "source_root": "root_0",
        "bundle_path": "System/Library/XPCServices/Worker.xpc",
        "status": "parsed",
    }
    record.update(values)
    return record


class CompareEmbeddedServicesTests(unittest.TestCase):
    def test_common_and_unique_identifiers(self):
        target = inventory([bundle("common"), bundle("target-only")])
        donor = inventory(
            [bundle("common"), bundle("donor-only", minimum_os_version="16.7")]
        )
        summary, rows = compare(target, donor)
        comparison = summary["identifier_comparison"]
        self.assertEqual(comparison["common_identifier_count"], 1)
        self.assertEqual(comparison["target_only_identifier_count"], 1)
        self.assertEqual(comparison["donor_only_identifier_count"], 1)
        self.assertEqual(len(rows), 3)

    def test_duplicate_identifiers_are_counted_not_discarded(self):
        target = inventory([bundle("same")])
        donor = inventory(
            [
                bundle("same"),
                bundle(
                    "same",
                    source_root="root_1",
                    bundle_path="Staged/Worker.xpc",
                ),
            ]
        )
        summary, rows = compare(target, donor)
        self.assertEqual(summary["identifier_comparison"]["common_identifier_count"], 1)
        self.assertEqual(rows[0]["donor_occurrences"], "2")
        self.assertEqual(summary["donor"]["duplicate_identifier_count"], 1)

    def test_metadata_comparison_ignores_repeated_identical_rows(self):
        target = inventory([bundle("same"), bundle("same")])
        donor = inventory([bundle("same")])
        summary, _ = compare(target, donor)
        self.assertNotIn(
            "bundle_type",
            summary["identifier_comparison"]["metadata_difference_identifier_counts"],
        )

    def test_metadata_changes_are_reported(self):
        target = inventory([bundle("same", minimum_os_version="15.8")])
        donor = inventory([bundle("same", minimum_os_version="16.7")])
        summary, rows = compare(target, donor)
        self.assertEqual(
            summary["identifier_comparison"]["metadata_difference_identifier_counts"][
                "minimum_os_version"
            ],
            1,
        )
        self.assertIn("minimum_os_version", rows[0]["changed_metadata_fields"])

    def test_missing_identifier_records_stay_in_inventory_statistics(self):
        target = inventory([bundle(None), bundle("known")])
        donor = inventory([bundle("known")])
        summary, rows = compare(target, donor)
        self.assertEqual(summary["target"]["candidate_bundle_count"], 2)
        self.assertEqual(summary["target"]["identifier_record_count"], 1)
        self.assertEqual(len(rows), 1)

    def test_null_and_empty_metadata_values_compare_differently(self):
        target = inventory([bundle("same", extension=None)])
        donor = inventory([bundle("same", extension={})])
        summary, _ = compare(target, donor)
        self.assertEqual(
            summary["identifier_comparison"]["metadata_difference_identifier_counts"][
                "extension"
            ],
            1,
        )

    def test_csv_contains_all_identifiers(self):
        target = inventory([bundle("a")])
        donor = inventory([bundle("a"), bundle("b")])
        _, rows = compare(target, donor)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "out.csv"
            write_csv(path, rows)
            content = path.read_text(encoding="utf-8")
        self.assertIn("bundle_identifier,presence", content)
        self.assertIn("donor-only", content)
        self.assertEqual(content.count("\n"), 3)

    def test_rejects_wrong_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text(
                json.dumps({"schema": "wrong", "bundles": []}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_inventory(path)

    def test_rejects_non_object_bundle_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text(
                json.dumps(
                    {"schema": SCHEMA, "bundles": ["not-an-object"]}
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_inventory(path)

    def test_declared_mach_services_are_counted_as_metadata_only(self):
        target = inventory([bundle("same")])
        donor = inventory(
            [bundle("same", mach_services=["svc.alpha", "svc.beta"])],
            mach_service_providers=[{"service": "svc.alpha"}],
        )
        summary, _ = compare(target, donor)
        self.assertEqual(summary["donor"]["declared_mach_service_name_count"], 2)
        self.assertEqual(
            summary["donor"]["mach_service_provider_index_entry_count"], 1
        )
        self.assertTrue(
            any(
                "do not prove launch" in note
                for note in summary["interpretation_limits"]
            )
        )


if __name__ == "__main__":
    unittest.main()
