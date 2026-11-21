"""Synthetic tests for the recursive read-only framework location inventory."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_framework_paths import EXPECTED_SCHEMA, InspectionError
from inventory_framework_locations import OUTPUT_SCHEMA, build_inventory


def write_candidates(path, entries):
    path.write_text(json.dumps({
        "schema": EXPECTED_SCHEMA,
        "target_reference": {"device": "iPhone9,1", "build": "19H422"},
        "donor_reference": {"device": "iPhone10,3", "build": "20H392"},
        "candidates": [
            {
                "id": entry[0],
                "path": entry[1],
                "group": "Synthetic",
                "reason": "test fixture",
            }
            for entry in entries
        ],
    }), encoding="utf-8")


class FrameworkLocationInventoryTests(unittest.TestCase):
    def test_finds_binary_and_framework_bundle_in_unexpected_subtree(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "target-root"
            bundle = root / "private/alternate/Example.framework"
            binary = bundle / "Example"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"not-read-by-the-inspector")
            candidates = base / "candidates.json"
            write_candidates(candidates, [
                ("example", "/System/Library/Frameworks/Example.framework/Example")
            ])

            report = build_inventory(candidates, root)
            row = report["candidates"][0]
            self.assertEqual(report["schema"], OUTPUT_SCHEMA)
            self.assertEqual(report["scan_status"], "complete")
            self.assertEqual(row["status"], "match-found")
            self.assertEqual(
                {item["match_kind"] for item in row["matches"]},
                {"binary-name", "framework-bundle-name"},
            )
            self.assertEqual(
                {item["path"] for item in row["matches"]},
                {"private/alternate/Example.framework", "private/alternate/Example.framework/Example"},
            )

    def test_bundle_directory_only_is_not_reported_as_binary_file_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "target-root"
            bundle = root / "System/Library/PrivateFrameworks/Example.framework"
            bundle.mkdir(parents=True)
            candidates = base / "candidates.json"
            write_candidates(candidates, [
                ("example", "/System/Library/Frameworks/Example.framework/Example")
            ])

            report = build_inventory(candidates, root)
            row = report["candidates"][0]
            self.assertEqual(row["status"], "bundle-directory-only")
            self.assertEqual(row["binary_matches"], [])
            self.assertEqual(len(row["bundle_directory_matches"]), 1)
            self.assertEqual(row["bundle_directory_matches"][0]["entry_kind"], "directory")

    def test_regular_binary_file_has_binary_file_found_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "target-root"
            binary = root / "alternate/Example.framework/Example"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"not-opened")
            candidates = base / "candidates.json"
            write_candidates(candidates, [
                ("example", "/System/Library/Frameworks/Example.framework/Example")
            ])

            report = build_inventory(candidates, root)
            row = report["candidates"][0]
            self.assertEqual(row["status"], "binary-file-found")
            self.assertEqual(len(row["binary_matches"]), 1)
            self.assertEqual(row["binary_matches"][0]["entry_kind"], "regular-file")

    def test_no_match_is_reported_only_for_complete_scans(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            root.mkdir()
            candidates = base / "candidates.json"
            write_candidates(candidates, [("example", "/System/Library/Example.framework/Example")])

            report = build_inventory(candidates, root)
            self.assertEqual(report["scan_status"], "complete")
            self.assertEqual(report["candidates"][0]["status"], "no-match-in-complete-scan")

    def test_directory_symlink_is_recorded_but_never_traversed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            outside = base / "outside" / "Example.framework"
            root.mkdir()
            outside.mkdir(parents=True)
            (outside / "Example").touch()
            (root / "linked").mkdir()
            (root / "linked" / "Example.framework").symlink_to(outside, target_is_directory=True)
            candidates = base / "candidates.json"
            write_candidates(candidates, [("example", "/System/Library/Example.framework/Example")])

            report = build_inventory(candidates, root)
            row = report["candidates"][0]
            self.assertEqual(row["status"], "match-found")
            self.assertEqual(len(row["matches"]), 1)
            self.assertEqual(row["matches"][0]["entry_kind"], "symlink")
            self.assertEqual(row["matches"][0]["match_kind"], "framework-bundle-name")
            self.assertNotIn("Example.framework/Example", [item["path"] for item in report["matches"]])

    def test_symlink_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            actual = base / "actual"
            actual.mkdir()
            link = base / "link"
            link.symlink_to(actual, target_is_directory=True)
            candidates = base / "candidates.json"
            write_candidates(candidates, [("example", "/System/Example.framework/Example")])
            with self.assertRaises(InspectionError):
                build_inventory(candidates, link)

    def test_non_directory_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root_file = base / "not-a-directory"
            root_file.write_text("x", encoding="utf-8")
            candidates = base / "candidates.json"
            write_candidates(candidates, [("example", "/System/Example.framework/Example")])
            with self.assertRaises(InspectionError):
                build_inventory(candidates, root_file)

    def test_walk_errors_mark_unmatched_candidates_as_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            root.mkdir()
            candidates = base / "candidates.json"
            write_candidates(candidates, [("example", "/System/Example.framework/Example")])

            def fake_walk(path, topdown=True, onerror=None, followlinks=False):
                if onerror:
                    onerror(PermissionError(13, "permission denied", str(Path(path) / "locked")))
                yield str(path), [], []

            with patch("inventory_framework_locations.os.walk", side_effect=fake_walk):
                report = build_inventory(candidates, root)
            self.assertEqual(report["scan_status"], "incomplete")
            self.assertEqual(
                report["candidates"][0]["status"],
                "no-match-scan-incomplete",
            )
            self.assertEqual(report["summary"]["walk_error_count"], 1)


if __name__ == "__main__":
    unittest.main()
