"""Synthetic tests for the read-only dyld loader-record collector."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import capture_dyld_loader_records as collector


class DyldLoaderCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / "dyld_shared_cache_arm64"
        self.cache.write_bytes(b"synthetic cache placeholder")
        self.output = self.root / "records"

    def completed(self, args, stdout="", stderr="", returncode=0):
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)

    def test_captures_raw_output_and_records_version_and_hashes(self):
        image = "/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices"
        responses = [
            self.completed(["ipsw", "version"], "Version 3.1.749\n"),
            self.completed(["ipsw", "dyld", "image"], "PrebuiltLoaderSet: example\n"),
        ]
        with mock.patch.object(collector.shutil, "which", return_value="/usr/bin/ipsw"), \
             mock.patch.object(collector.subprocess, "run", side_effect=responses) as run:
            report = collector.capture_records(
                self.cache, self.output, images=(image,)
            )

        self.assertEqual(report["tool_version_output"], "Version 3.1.749")
        self.assertEqual(report["successful_count"], 1)
        self.assertEqual(report["failed_count"], 0)
        record = report["records"][0]
        self.assertEqual(record["image"], image)
        self.assertEqual(record["status"], "captured")
        self.assertEqual(
            (self.output / record["stdout_file"]).read_text(encoding="utf-8"),
            "PrebuiltLoaderSet: example\n",
        )
        self.assertEqual(len(record["stdout_sha256"]), 64)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(
            run.call_args_list[1].args[0],
            ["/usr/bin/ipsw", "dyld", "image", str(self.cache.resolve()), image],
        )
        saved_manifest = json.loads((self.output / "capture-manifest.json").read_text())
        self.assertEqual(saved_manifest["schema"], collector.SCHEMA)

    def test_failed_lookup_is_recorded_and_does_not_abort_collection(self):
        images = (
            "/System/Library/PrivateFrameworks/ExampleA.framework/ExampleA",
            "/System/Library/PrivateFrameworks/ExampleB.framework/ExampleB",
        )
        responses = [
            self.completed(["ipsw", "version"], "Version test\n"),
            self.completed(["ipsw", "dyld", "image"], "partial", "not found", 1),
            self.completed(["ipsw", "dyld", "image"], "loader data", "", 0),
        ]
        with mock.patch.object(collector.shutil, "which", return_value="/usr/bin/ipsw"), \
             mock.patch.object(collector.subprocess, "run", side_effect=responses):
            report = collector.capture_records(
                self.cache, self.output, images=images
            )

        self.assertEqual(report["failed_count"], 1)
        self.assertEqual(report["successful_count"], 1)
        self.assertEqual(report["records"][0]["exit_code"], 1)
        self.assertEqual(
            (self.output / report["records"][0]["stderr_file"]).read_text(),
            "not found",
        )
        self.assertEqual(report["records"][1]["status"], "captured")

    def test_refuses_to_overwrite_existing_capture_without_explicit_flag(self):
        self.output.mkdir()
        (self.output / "capture-manifest.json").write_text("{}")
        with mock.patch.object(collector.shutil, "which", return_value="/usr/bin/ipsw"), \
             mock.patch.object(collector.subprocess, "run") as run:
            with self.assertRaises(collector.CaptureError):
                collector.capture_records(
                    self.cache,
                    self.output,
                    images=("/System/Library/Frameworks/Foundation.framework/Foundation",),
                )
        run.assert_not_called()

    def test_missing_cache_is_rejected_before_running_ipsw(self):
        with mock.patch.object(collector.shutil, "which", return_value="/usr/bin/ipsw"), \
             mock.patch.object(collector.subprocess, "run") as run:
            with self.assertRaises(collector.CaptureError):
                collector.capture_records(
                    self.root / "missing-cache",
                    self.output,
                    images=("/System/Library/Frameworks/Foundation.framework/Foundation",),
                )
        run.assert_not_called()

    def test_non_absolute_and_duplicate_image_paths_are_rejected(self):
        with mock.patch.object(collector.shutil, "which", return_value="/usr/bin/ipsw"):
            with self.assertRaises(collector.CaptureError):
                collector.capture_records(
                    self.cache, self.output, images=("Foundation",)
                )
            with self.assertRaises(collector.CaptureError):
                collector.capture_records(
                    self.cache,
                    self.output,
                    images=(
                        "/System/Library/Frameworks/Foundation.framework/Foundation",
                        "/System/Library/Frameworks/Foundation.framework/Foundation",
                    ),
                )

    def test_missing_ipsw_is_reported(self):
        with mock.patch.object(collector.shutil, "which", return_value=None):
            with self.assertRaises(collector.CaptureError):
                collector.capture_records(
                    self.cache,
                    self.output,
                    ipsw_bin="ipsw-not-installed",
                    images=("/System/Library/Frameworks/Foundation.framework/Foundation",),
                )


if __name__ == "__main__":
    unittest.main()
