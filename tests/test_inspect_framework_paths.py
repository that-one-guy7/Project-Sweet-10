"""Synthetic tests for the read-only framework path inspector."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_framework_paths import (
    EXPECTED_SCHEMA,
    InspectionError,
    aggregate_status,
    build_report,
    inspect_relative_path,
    load_candidates,
)


def write_candidates(path, candidates, schema=EXPECTED_SCHEMA):
    path.write_text(json.dumps({
        "schema": schema,
        "target_reference": {"build": "19H422"},
        "donor_reference": {"build": "20H392"},
        "candidates": candidates,
    }), encoding="utf-8")


def candidate(identifier, path, group="SpringBoard.framework"):
    return {"id": identifier, "path": path, "group": group, "reason": "synthetic test"}


class FrameworkPathTests(unittest.TestCase):
    def test_exact_regular_file_is_found_without_opening_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "System/Library/Frameworks/Example.framework/Example"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"do-not-read")
            self.assertEqual(
                inspect_relative_path(root, ("System", "Library", "Frameworks", "Example.framework", "Example")),
                "regular-file",
            )

    def test_root_wrapper_depth_one_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "root/System/Library/Frameworks/Example.framework/Example"
            target.parent.mkdir(parents=True)
            target.touch()
            candidate_file = root / "candidates.json"
            write_candidates(candidate_file, [
                candidate("example", "/System/Library/Frameworks/Example.framework/Example")
            ])
            report = build_report(candidate_file, [("r0", root)], wrapper_depth=2)
            row = report["candidates"][0]
            self.assertEqual(row["status"], "regular-file-found")
            self.assertEqual(
                next(check for check in row["checks"] if check["state"] == "regular-file")["root_wrapper_depth"],
                1,
            )

    def test_extensionfoundation_exact_donor_path_and_target_alternate_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alternate = root / "root/System/Library/PrivateFrameworks/ExtensionFoundation.framework/ExtensionFoundation"
            alternate.parent.mkdir(parents=True)
            alternate.touch()
            candidate_file = root / "candidates.json"
            write_candidates(candidate_file, [
                candidate("donor-frameworks-path", "/System/Library/Frameworks/ExtensionFoundation.framework/ExtensionFoundation"),
                candidate("target-privateframeworks-path", "/System/Library/PrivateFrameworks/ExtensionFoundation.framework/ExtensionFoundation"),
            ])
            report = build_report(candidate_file, [("r0", root)], wrapper_depth=1)
            rows = {row["id"]: row for row in report["candidates"]}
            self.assertEqual(rows["donor-frameworks-path"]["status"], "not-found-under-scanned-roots")
            self.assertEqual(rows["target-privateframeworks-path"]["status"], "regular-file-found")

    def test_final_symlink_is_reported_without_following(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "System/Library/Frameworks/Example.framework/Example"
            target.parent.mkdir(parents=True)
            target.symlink_to("/etc/passwd")
            self.assertEqual(
                inspect_relative_path(root, ("System", "Library", "Frameworks", "Example.framework", "Example")),
                "final-symlink",
            )

    def test_intermediate_symlink_is_reported_without_following(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "System").symlink_to("/tmp", target_is_directory=True)
            self.assertEqual(inspect_relative_path(root, ("System", "file")), "symlink-component")

    def test_missing_path_is_limited_to_checked_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(inspect_relative_path(Path(tmp), ("System", "missing")), "missing")

    def test_non_directory_component_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "System").write_text("x", encoding="utf-8")
            self.assertEqual(inspect_relative_path(root, ("System", "child")), "not-directory")

    def test_candidate_schema_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate_file = Path(tmp) / "candidates.json"
            write_candidates(candidate_file, [candidate("x", "/System/x")], schema="wrong")
            with self.assertRaises(InspectionError):
                load_candidates(candidate_file)

    def test_candidate_ids_must_be_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate_file = Path(tmp) / "candidates.json"
            write_candidates(candidate_file, [
                candidate("duplicate", "/System/one"),
                candidate("duplicate", "/System/two"),
            ])
            with self.assertRaises(InspectionError):
                load_candidates(candidate_file)

    def test_rejects_relative_and_traversal_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate_file = Path(tmp) / "candidates.json"
            for bad_path in ("relative/path", "/System/../etc/passwd", "/System//Example"):
                write_candidates(candidate_file, [candidate("bad", bad_path)])
                with self.subTest(path=bad_path), self.assertRaises(InspectionError):
                    load_candidates(candidate_file)

    def test_wrapper_depth_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_file = root / "candidates.json"
            write_candidates(candidate_file, [candidate("x", "/System/x")])
            with self.assertRaises(InspectionError):
                build_report(candidate_file, [("r0", root)], wrapper_depth=5)

    def test_aggregate_status_keeps_symlink_distinct_from_missing(self):
        self.assertEqual(
            aggregate_status([{"state": "missing"}, {"state": "symlink-component"}]),
            "symlink-present-unresolved",
        )
        self.assertEqual(
            aggregate_status([{"state": "missing"}]),
            "not-found-under-scanned-roots",
        )

    def test_root_must_exist_and_be_a_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            candidate_file = base / "candidates.json"
            write_candidates(candidate_file, [candidate("x", "/System/x")])
            with self.assertRaises(InspectionError):
                build_report(candidate_file, [("missing", base / "no-such-root")])

    def test_all_candidate_records_are_retained_in_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            candidate_file = base / "candidates.json"
            write_candidates(candidate_file, [
                candidate("one", "/System/one"),
                candidate("two", "/System/two"),
            ])
            report = build_report(candidate_file, [("r0", base)], wrapper_depth=0)
            self.assertEqual([row["id"] for row in report["candidates"]], ["one", "two"])
            self.assertEqual(report["candidate_count"], 2)


if __name__ == "__main__":
    unittest.main()
