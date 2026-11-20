"""Host-side tests for the XNU source lock and read-only CI workflow."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SourceLockTests(unittest.TestCase):
    def test_locked_commit_is_a_full_git_sha(self):
        lock = json.loads((ROOT / "xnu/BASELINE.lock.json").read_text(encoding="utf-8"))
        self.assertRegex(lock["commit_sha"], r"^[0-9a-f]{40}$")

    def test_workflow_checks_out_the_commit_from_the_lock(self):
        workflow = (ROOT / ".github/workflows/xnu-source-check.yml").read_text(encoding="utf-8")
        self.assertIn("id: source-lock", workflow)
        self.assertIn("ref: ${{ steps.source-lock.outputs.commit_sha }}", workflow)
        self.assertNotIn("ref: 1b191cb58250d0705d8a51287127505aa4bc0789", workflow)

    def test_workflow_has_read_only_repository_permissions(self):
        workflow = (ROOT / ".github/workflows/xnu-source-check.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:", workflow)
        self.assertIn("  contents: read", workflow)

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
