"""Synthetic tests for the read-only launchd Program-path inspector."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_launchd_program_paths import (
    EXPECTED_SCHEMA,
    InspectionError,
    _aggregate_status,
    build_report,
    inspect_relative_path,
    load_inventory,
)


def write_inventory(path, jobs, source_sha="a" * 64):
    path.write_text(json.dumps({
        "schema": EXPECTED_SCHEMA,
        "source_sha256": source_sha,
        "jobs": jobs,
    }), encoding="utf-8")


def job(label, program, key=None):
    return {
        "label": label,
        "launchd_key": key or f"/System/Library/LaunchDaemons/{label}.plist",
        "program": program,
    }


class LaunchdProgramPathTests(unittest.TestCase):
    def test_regular_file_at_exact_program_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "usr/libexec/backboardd"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"do-not-read")
            self.assertEqual(inspect_relative_path(root, ("usr", "libexec", "backboardd")), "regular-file")

    def test_bounded_root_wrapper_is_detected_in_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "mount"
            target = root / "root/System/Library/CoreServices/SpringBoard.app/SpringBoard"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"not-opened")
            inventory = base / "launchd.json"
            write_inventory(inventory, [job("com.apple.SpringBoard", "/System/Library/CoreServices/SpringBoard.app/SpringBoard")])
            report = build_report(
                inventory, inventory,
                [("r0", root)], [("r0", root)],
                ("com.apple.SpringBoard",), 2,
            )
            row = report["target_19H422"]["jobs"][0]
            self.assertEqual(row["status"], "regular-file-found")
            self.assertEqual(
                next(x for x in row["checks"] if x["state"] == "regular-file")["root_wrapper_depth"],
                1,
            )

    def test_symlink_is_reported_and_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "usr/libexec").mkdir(parents=True)
            (root / "usr/libexec/daemon").symlink_to("/etc/passwd")
            self.assertEqual(inspect_relative_path(root, ("usr", "libexec", "daemon")), "final-symlink")

    def test_intermediate_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "linked").symlink_to("/tmp", target_is_directory=True)
            self.assertEqual(inspect_relative_path(root, ("linked", "file")), "symlink-component")

    def test_missing_path_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(inspect_relative_path(Path(tmp), ("no", "such", "file")), "missing")

    def test_non_directory_component_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "regular").write_text("x", encoding="utf-8")
            self.assertEqual(inspect_relative_path(root, ("regular", "child")), "not-directory")

    def test_rejects_non_absolute_program_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = root / "launchd.json"
            write_inventory(inventory, [job("com.apple.SpringBoard", "relative/SpringBoard")])
            report = build_report(
                inventory, inventory,
                [("r", root)], [("r", root)],
                ("com.apple.SpringBoard",), 0,
            )
            self.assertEqual(
                report["target_19H422"]["jobs"][0]["status"],
                "invalid-or-missing-absolute-program-path",
            )

    def test_filters_selected_labels_and_keeps_duplicate_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = root / "launchd.json"
            write_inventory(inventory, [
                job("com.apple.SpringBoard", "/one"),
                job("com.apple.SpringBoard", "/two", key="second"),
                job("ignored", "/three"),
            ])
            report = build_report(
                inventory, inventory,
                [("r", root)], [("r", root)],
                ("com.apple.SpringBoard",), 0,
            )
            jobs = report["target_19H422"]["jobs"]
            self.assertEqual(len(jobs), 2)
            self.assertEqual({x["program"] for x in jobs}, {"/one", "/two"})

    def test_load_inventory_rejects_wrong_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory = Path(tmp) / "launchd.json"
            inventory.write_text(json.dumps({"schema": "wrong", "jobs": []}), encoding="utf-8")
            with self.assertRaises(InspectionError):
                load_inventory(inventory)

    def test_status_aggregation_keeps_unresolved_symlink_distinct_from_missing(self):
        checks = [{"state": "missing"}, {"state": "symlink-component"}]
        self.assertEqual(_aggregate_status(checks), "symlink-present-unresolved")
        self.assertEqual(
            _aggregate_status([{"state": "missing"}]),
            "not-found-under-scanned-roots",
        )

    def test_rejects_wrapper_depth_outside_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = root / "launchd.json"
            write_inventory(inventory, [])
            with self.assertRaises(InspectionError):
                build_report(inventory, inventory, [("r", root)], [("r", root)], (), 5)


if __name__ == "__main__":
    unittest.main()
