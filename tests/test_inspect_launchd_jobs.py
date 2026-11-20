"""Synthetic tests for the read-only launchd job inventory."""
import json
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_launchd_jobs import InventoryError, inspect_root


def make_root(root, launch_daemons=None):
    plist_path = root / "System/Library/xpc/launchd.plist"
    plist_path.parent.mkdir(parents=True)
    document = {
        "LaunchDaemons": launch_daemons
        if launch_daemons is not None
        else {
            "com.apple.backboardd": {
                "Label": "com.apple.backboardd",
                "ProgramArguments": [
                    "/System/Library/CoreServices/backboardd.app/backboardd",
                    "--example",
                    "private-value-that-must-not-be-exported",
                ],
                "MachServices": {
                    "com.apple.backboard.services": True,
                    "com.apple.frontboard.systemappservices": True,
                },
                "KeepAlive": {"SuccessfulExit": False, "AfterInitialDemand": True},
                "RunAtLoad": True,
                "UserName": "mobile",
                "EnvironmentVariables": {
                    "OS_ACTIVITY_DT_MODE": "YES",
                    "PRIVATE_TOKEN": "do-not-export-this-value",
                },
            },
            "com.apple.SpringBoard": {
                "Label": "com.apple.SpringBoard",
                "Program": "/System/Library/CoreServices/SpringBoard.app/SpringBoard",
                "MachServices": {"com.apple.springboard.services": True},
                "KeepAlive": True,
            },
            "com.apple.mediaserverd": {
                "Label": "com.apple.mediaserverd",
                "ProgramArguments": ["/usr/sbin/mediaserverd"],
                "Disabled": False,
                "KeepAlive": False,
            },
        },
    }
    plist_path.write_bytes(plistlib.dumps(document, fmt=plistlib.FMT_BINARY))
    return plist_path


class LaunchdInventoryTests(unittest.TestCase):
    def test_inventory_summarizes_jobs_and_focus_services(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = make_root(root)
            report = inspect_root(root)

            self.assertEqual(report["launch_daemon_count"], 3)
            self.assertEqual(report["source_plist"], "System/Library/xpc/launchd.plist")
            self.assertEqual(len(report["source_sha256"]), 64)
            labels = {job["label"] for job in report["jobs"]}
            self.assertEqual(
                labels,
                {"com.apple.backboardd", "com.apple.SpringBoard", "com.apple.mediaserverd"},
            )
            self.assertEqual(source.read_bytes(), (root / report["source_plist"]).read_bytes())
            self.assertEqual(
                {tag for item in report["focus_service_matches"] for tag in item["matched_tags"]},
                {"backboardd", "springboard", "mediaserverd"},
            )

    def test_environment_values_and_full_arguments_are_not_exported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_root(root)
            report = inspect_root(root)
            encoded = json.dumps(report)

            self.assertNotIn("PRIVATE_TOKEN", encoded)
            self.assertNotIn("do-not-export-this-value", encoded)
            self.assertNotIn("private-value-that-must-not-be-exported", encoded)
            backboard = next(
                job for job in report["jobs"] if job["label"] == "com.apple.backboardd"
            )
            self.assertEqual(backboard["program_arguments_count"], 3)
            self.assertEqual(
                backboard["environment_variable_names"],
                ["OS_ACTIVITY_DT_MODE", "PRIVATE_TOKEN"],
            )

    def test_mach_service_provider_index_is_sorted_and_does_not_claim_clients(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_root(root)
            report = inspect_root(root)
            service = next(
                row for row in report["mach_service_providers"]
                if row["service"] == "com.apple.backboard.services"
            )
            self.assertEqual(service["provider_labels"], ["com.apple.backboardd"])
            self.assertIn(
                "it does not reveal every client dependency.",
                report["scope_notes"][1],
            )

    def test_keep_alive_is_reduced_to_mode_and_condition_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_root(root)
            report = inspect_root(root)
            jobs = {job["label"]: job for job in report["jobs"]}

            self.assertEqual(
                jobs["com.apple.backboardd"]["keep_alive"],
                {"mode": "conditions", "condition_keys": ["AfterInitialDemand", "SuccessfulExit"]},
            )
            self.assertEqual(
                jobs["com.apple.SpringBoard"]["keep_alive"],
                {"mode": "always", "condition_keys": []},
            )
            self.assertEqual(
                jobs["com.apple.mediaserverd"]["keep_alive"],
                {"mode": "never", "condition_keys": []},
            )

    def test_missing_launchd_plist_reports_a_clear_error(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(InventoryError):
                inspect_root(temp)

    def test_invalid_launch_daemon_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_root(root, {"bad-job": "not-a-dictionary"})
            with self.assertRaises(InventoryError):
                inspect_root(root)

    def test_workflow_triggers_when_launchd_inspector_changes(self):
        workflow = (
            ROOT / ".github/workflows/xnu-source-check.yml"
        ).read_text(encoding="utf-8")
        self.assertEqual(workflow.count('- "tools/inspect_launchd_jobs.py"'), 2)

    def test_command_line_emits_json_and_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plist_path = make_root(root)
            original = plist_path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/inspect_launchd_jobs.py"), str(root)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            parsed = json.loads(result.stdout)
            self.assertEqual(parsed["schema"], "project-sweet-10.launchd-inventory.v1")
            self.assertEqual(plist_path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
