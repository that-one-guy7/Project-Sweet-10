"""Host-side tests for the pinned PongoOS source lock and verifier."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_pongo_source import EXPECTED_REPOSITORY, load_lock, verify_checkout


class PongoSourceLockTests(unittest.TestCase):
    def test_lock_contains_repository_and_full_commit_sha(self):
        lock = load_lock()
        self.assertEqual(lock["repository"], EXPECTED_REPOSITORY)
        self.assertRegex(lock["commit_sha"], r"^[0-9a-f]{40}$")
        self.assertTrue(lock.get("not_a_device_support_claim"))

    def test_workflow_reads_pongo_commit_from_lock(self):
        workflow = (ROOT / ".github/workflows/xnu-source-check.yml").read_text(encoding="utf-8")
        self.assertIn("id: pongo-source-lock", workflow)
        self.assertIn('json.load(open("pongo/BASELINE.lock.json"', workflow)
        self.assertIn("ref: ${{ steps.pongo-source-lock.outputs.commit_sha }}", workflow)

    def test_workflow_checks_out_the_pinned_repository_and_runs_verifier(self):
        workflow = (ROOT / ".github/workflows/xnu-source-check.yml").read_text(encoding="utf-8")
        self.assertIn("repository: checkra1n/PongoOS", workflow)
        self.assertIn("path: pongo/upstream", workflow)
        self.assertIn("tools/verify_pongo_source.py pongo/upstream", workflow)

    def test_workflow_triggers_on_pongo_lock_or_verifier_changes(self):
        workflow = (ROOT / ".github/workflows/xnu-source-check.yml").read_text(encoding="utf-8")
        workflow_lines = [line.strip() for line in workflow.splitlines()]
        self.assertEqual(workflow_lines.count('- "pongo/BASELINE.lock.json"'), 2)
        self.assertEqual(workflow_lines.count('- "tools/verify_pongo_source.py"'), 2)
        self.assertEqual(workflow.count('"pongo/BASELINE.lock.json"'), 2)
        self.assertEqual(workflow.count('"tools/verify_pongo_source.py"'), 2)

    def test_workflow_keeps_repository_permissions_read_only(self):
        workflow = (ROOT / ".github/workflows/xnu-source-check.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:", workflow)
        self.assertIn("  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)

    def test_verifier_accepts_exact_checkout_and_rejects_different_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            checkout = Path(temp) / "pongo"
            checkout.mkdir()
            subprocess.run(["git", "init", "--quiet", str(checkout)], check=True)
            subprocess.run(["git", "-C", str(checkout), "config", "user.name", "Sweet-10 test"], check=True)
            subprocess.run(["git", "-C", str(checkout), "config", "user.email", "sweet10-test@example.invalid"], check=True)
            (checkout / "fixture.txt").write_text("source-lock test\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(checkout), "add", "fixture.txt"], check=True)
            subprocess.run(["git", "-C", str(checkout), "commit", "--quiet", "-m", "fixture"], check=True)
            actual = subprocess.check_output(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
            ).strip()

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(verify_checkout(checkout, actual))
                self.assertFalse(verify_checkout(checkout, "0" * 40))

    def test_verifier_usage_is_documented(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/verify_pongo_source.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
