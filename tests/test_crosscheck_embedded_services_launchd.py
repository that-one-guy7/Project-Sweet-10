"""Synthetic tests for the embedded-bundle / launchd service cross-check."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from crosscheck_embedded_services_launchd import (
    BUNDLE_SCHEMA,
    LAUNCHD_SCHEMA,
    crosscheck,
    load_bundle_inventory,
    load_launchd_inventory,
)


def bundle(service_names, **overrides):
    row = {
        "status": "parsed",
        "bundle_identifier": "com.example.worker",
        "bundle_type": ".xpc",
        "bundle_executable": "Worker",
        "executable_state": "regular-file",
        "source_root": "root_0",
        "bundle_path": "System/Library/XPCServices/Worker.xpc",
        "mach_services": service_names,
    }
    row.update(overrides)
    return row


def bundle_inventory(bundles):
    return {"schema": BUNDLE_SCHEMA, "bundles": bundles}


def launchd_inventory(rows):
    return {"schema": LAUNCHD_SCHEMA, "mach_service_providers": rows}


class CrosscheckEmbeddedServicesLaunchdTests(unittest.TestCase):
    def test_matches_exact_service_name_and_preserves_provider_labels(self):
        result = crosscheck(
            bundle_inventory([bundle(["svc.alpha"])]),
            launchd_inventory([{"service": "svc.alpha", "provider_labels": ["job.alpha"]}]),
            "a" * 64,
            "b" * 64,
        )
        self.assertEqual(result["summary"]["launchd_index_match_occurrence_count"], 1)
        self.assertTrue(result["entries"][0]["launchd_index_match"])
        self.assertEqual(result["entries"][0]["launchd_provider_labels"], ["job.alpha"])

    def test_unmatched_name_is_not_dropped_or_called_globally_missing(self):
        result = crosscheck(
            bundle_inventory([bundle(["svc.not-indexed"])]),
            launchd_inventory([]),
            "a" * 64,
            "b" * 64,
        )
        self.assertEqual(result["summary"]["launchd_index_unmatched_occurrence_count"], 1)
        self.assertFalse(result["entries"][0]["launchd_index_match"])
        self.assertEqual(result["entries"][0]["launchd_provider_labels"], [])

    def test_duplicate_bundle_records_remain_separate_occurrences(self):
        first = bundle(["svc.shared"], bundle_path="System/A.xpc")
        second = bundle(["svc.shared"], bundle_path="private/staged/A.xpc", source_root="root_1")
        result = crosscheck(
            bundle_inventory([first, second]),
            launchd_inventory([{"service": "svc.shared", "provider_labels": ["job.shared"]}]),
            "a" * 64,
            "b" * 64,
        )
        self.assertEqual(result["summary"]["service_declaration_occurrence_count"], 2)
        self.assertEqual(result["summary"]["unique_declared_service_count"], 1)
        self.assertEqual(len(result["entries"]), 2)
        self.assertNotEqual(result["entries"][0]["bundle_path"], result["entries"][1]["bundle_path"])

    def test_ignores_unparsed_bundles(self):
        row = bundle(["svc.ignored"], status="missing-info-plist")
        result = crosscheck(
            bundle_inventory([row]),
            launchd_inventory([]),
            "a" * 64,
            "b" * 64,
        )
        self.assertEqual(result["summary"]["candidate_bundle_count"], 1)
        self.assertEqual(result["summary"]["parsed_bundle_count"], 0)
        self.assertEqual(result["entries"], [])

    def test_no_declarations_produces_empty_result(self):
        result = crosscheck(
            bundle_inventory([bundle([])]),
            launchd_inventory([{"service": "svc.other", "provider_labels": ["job.other"]}]),
            "a" * 64,
            "b" * 64,
        )
        self.assertEqual(result["summary"]["service_declaration_occurrence_count"], 0)
        self.assertEqual(result["entries"], [])

    def test_rejects_wrong_bundle_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bundle.json"
            path.write_text(json.dumps({"schema": "wrong", "bundles": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_bundle_inventory(path)

    def test_rejects_invalid_service_names(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bundle.json"
            path.write_text(json.dumps(bundle_inventory([bundle("not-a-list")])), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_bundle_inventory(path)

    def test_rejects_duplicate_launchd_service_index_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "launchd.json"
            path.write_text(json.dumps(launchd_inventory([
                {"service": "svc.dup", "provider_labels": ["job.a"]},
                {"service": "svc.dup", "provider_labels": ["job.b"]},
            ])), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_launchd_inventory(path)

    def test_rejects_non_string_provider_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "launchd.json"
            path.write_text(json.dumps(launchd_inventory([
                {"service": "svc.alpha", "provider_labels": [7]},
            ])), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_launchd_inventory(path)


if __name__ == "__main__":
    unittest.main()
