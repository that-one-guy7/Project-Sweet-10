"""Host-side tests for the XNU source locks and read-only CI workflow."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SourceLockTests(unittest.TestCase):
    def test_locked_commit_is_a_full_git_sha(self):
        lock = json.loads(
            (ROOT / "xnu/BASELINE.lock.json").read_text(encoding="utf-8")
        )
        self.assertRegex(lock["commit_sha"], r"^[0-9a-f]{40}$")

    def test_historical_source_locks_have_full_shas_and_no_support_claim(self):
        for name in ("xnu-7195.121.3", "xnu-8019.80.24"):
            path = ROOT / "xnu" / "history" / (name + ".lock.json")
            lock = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(lock["tag"], name)
            self.assertRegex(lock["tag_object_sha"], r"^[0-9a-f]{40}$")
            self.assertRegex(lock["commit_sha"], r"^[0-9a-f]{40}$")
            self.assertEqual(lock["tag_signature"], "unsigned")
            self.assertTrue(lock["not_a_device_support_claim"])

    def test_workflow_checks_out_the_commit_from_the_current_lock(self):
        workflow = (
            ROOT / ".github/workflows/xnu-source-check.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("id: source-lock", workflow)
        self.assertIn("ref: ${{ steps.source-lock.outputs.commit_sha }}", workflow)
        self.assertNotIn("ref: 1b191cb58250d0705d8a51287127505aa4bc0789", workflow)

    def test_workflow_checks_out_historical_refs_from_their_locks(self):
        workflow = (
            ROOT / ".github/workflows/xnu-source-check.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("id: historical-xnu-lock", workflow)
        self.assertIn("id: transition-xnu-lock", workflow)
        self.assertIn(
            "ref: ${{ steps.historical-xnu-lock.outputs.commit_sha }}", workflow
        )
        self.assertIn(
            "ref: ${{ steps.transition-xnu-lock.outputs.commit_sha }}", workflow
        )
        self.assertIn(
            "xnu/history/xnu-7195.121.3.lock.json", workflow
        )
        self.assertIn(
            "xnu/history/xnu-8019.80.24.lock.json", workflow
        )
        self.assertIn("tools/audit_xnu_machine_history.py", workflow)
        self.assertEqual(workflow.count('- "xnu/history/**"'), 2)
        self.assertEqual(workflow.count('- "tools/audit_xnu_machine_history.py"'), 2)

    def test_workflow_uses_sparse_source_checkouts(self):
        workflow = (
            ROOT / ".github/workflows/xnu-source-check.yml"
        ).read_text(encoding="utf-8")
        self.assertEqual(workflow.count("sparse-checkout-cone-mode: false"), 3)
        self.assertIn("/pexpert/pexpert/arm64/H9.h", workflow)
        self.assertIn("/makedefs/MakeInc.kernel", workflow)

    def test_workflow_has_read_only_repository_permissions(self):
        workflow = (
            ROOT / ".github/workflows/xnu-source-check.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("permissions:", workflow)
        self.assertIn("  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)

    def test_verifier_usage_allows_an_explicit_historical_lock(self):
        verifier = (ROOT / "tools/verify_xnu_source.py").read_text(encoding="utf-8")
        self.assertIn("[PATH_TO_LOCK_JSON]", verifier)

    def test_scaffold_checker_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/check_project.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
