"""Synthetic tests for the expanded public XNU T8010 source matrix."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_xnu_public_source_matrix import audit_public_matrix


MACHINE_GUARD = """ifeq ($(filter $(CURRENT_MACHINE_CONFIG),$(SUPPORTED_$(CURRENT_ARCH_CONFIG)_MACHINE_CONFIGS)),)
$(error Unsupported CURRENT_MACHINE_CONFIG $(CURRENT_MACHINE_CONFIG))
endif
"""


def make_checkout(root, t8010, with_guard=True):
    (root / "makedefs").mkdir(parents=True)
    (root / "pexpert/pexpert/arm64").mkdir(parents=True)

    machine_list = "BCM2837 T6000 T8101 T8103 VMAPPLE"
    board_block = ""
    if t8010:
        machine_list = "T7000 T7001 T8010 T8011 BCM2837"
        board_block = (
            "#ifdef ARM64_BOARD_CONFIG_T8010\n"
            "#include <pexpert/arm64/H9.h>\n"
            "#endif\n"
        )

    makeinc_def = (
        "SUPPORTED_ARM64_MACHINE_CONFIGS = NONE\n"
        "SUPPORTED_ARM64_MACHINE_CONFIGS = {}\n".format(machine_list)
    )
    if t8010:
        makeinc_def += (
            "MACHINE_FLAGS_ARM64_T8010 = "
            "-DARM64_BOARD_CONFIG_T8010 -mcpu=hurricane\n"
        )

    (root / "makedefs/MakeInc.def").write_text(makeinc_def, encoding="utf-8")
    (root / "makedefs/MakeInc.kernel").write_text(
        MACHINE_GUARD if with_guard else "# guard missing\n", encoding="utf-8"
    )
    (root / "pexpert/pexpert/arm64/board_config.h").write_text(
        board_block, encoding="utf-8"
    )
    if t8010:
        (root / "pexpert/pexpert/arm64/H9.h").write_text(
            "#define APPLEHURRICANE\n", encoding="utf-8"
        )
    return root


class XnuPublicSourceMatrixTests(unittest.TestCase):
    def _fixtures(self, temp, overrides=None):
        overrides = overrides or {}
        base = Path(temp)
        roots = []
        for index in range(10):
            roots.append(
                make_checkout(
                    base / str(index),
                    t8010=overrides.get(index, index == 0),
                    with_guard=overrides.get("guard_" + str(index), True),
                )
            )
        return roots

    def test_expected_ten_release_matrix_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(audit_public_matrix(self._fixtures(temp)), [])

    def test_fails_if_a_later_release_reintroduces_t8010(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_public_matrix(self._fixtures(temp, {9: True}))
            self.assertTrue(any("xnu-10002.81.5" in error and "allowlist" in error for error in errors))

    def test_fails_if_first_public_10002_tag_reintroduces_t8010(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_public_matrix(self._fixtures(temp, {6: True}))
            self.assertTrue(any("xnu-10002.1.13" in error and "allowlist" in error for error in errors))

    def test_fails_if_target_era_public_source_has_t8010(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_public_matrix(self._fixtures(temp, {1: True}))
            self.assertTrue(any("xnu-8020.101.4" in error and "allowlist" in error for error in errors))

    def test_fails_if_any_snapshot_loses_machine_config_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_public_matrix(self._fixtures(temp, {"guard_9": False}))
            self.assertTrue(any("xnu-10002.81.5" in error and "rejection guard" in error for error in errors))

    def test_requires_exactly_ten_snapshots(self):
        with tempfile.TemporaryDirectory() as temp:
            roots = self._fixtures(temp)[:-1]
            errors = audit_public_matrix(roots)
            self.assertTrue(any("expected 10 source directories" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
