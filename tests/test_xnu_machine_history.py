"""Synthetic host-side tests for the historical XNU T8010 profile audit."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_xnu_machine_history import audit_history


MACHINE_GUARD = """ifeq ($(filter $(CURRENT_MACHINE_CONFIG),$(SUPPORTED_$(CURRENT_ARCH_CONFIG)_MACHINE_CONFIGS)),)
$(error Unsupported CURRENT_MACHINE_CONFIG $(CURRENT_MACHINE_CONFIG))
endif
"""


def make_checkout(
    root,
    t8010,
    with_guard=True,
    with_h9=True,
    with_machine_flag=True,
):
    (root / "makedefs").mkdir(parents=True)
    (root / "pexpert/pexpert/arm64").mkdir(parents=True)

    machine_list = "BCM2837 T6000 T8101 VMAPPLE"
    board_block = ""
    h9_file = False
    if t8010:
        machine_list = "T7000 T7001 T8010 T8011 BCM2837"
        board_block = (
            "#ifdef ARM64_BOARD_CONFIG_T8010\n"
            "#include <pexpert/arm64/H9.h>\n"
            "#endif\n"
        )
        h9_file = with_h9

    makeinc_def = (
        "SUPPORTED_ARM64_MACHINE_CONFIGS = NONE\n"
        "SUPPORTED_ARM64_MACHINE_CONFIGS = {}\n".format(machine_list)
    )
    if t8010 and with_machine_flag:
        makeinc_def += (
            "MACHINE_FLAGS_ARM64_T8010 = "
            "-DARM64_BOARD_CONFIG_T8010 -mcpu=hurricane\n"
        )

    (root / "makedefs/MakeInc.def").write_text(makeinc_def, encoding="utf-8")
    (root / "makedefs/MakeInc.kernel").write_text(
        MACHINE_GUARD if with_guard else "# machine config validation removed\n",
        encoding="utf-8",
    )
    (root / "pexpert/pexpert/arm64/board_config.h").write_text(
        board_block, encoding="utf-8"
    )
    if h9_file:
        (root / "pexpert/pexpert/arm64/H9.h").write_text(
            "#define APPLEHURRICANE\n", encoding="utf-8"
        )
    return root


class XnuMachineHistoryTests(unittest.TestCase):
    def _fixtures(self, temp, **overrides):
        base = Path(temp)
        historical = make_checkout(
            base / "7195",
            t8010=overrides.get("historical_t8010", True),
            with_h9=overrides.get("historical_h9", True),
            with_machine_flag=overrides.get("historical_machine_flag", True),
        )
        transition = make_checkout(
            base / "8019",
            t8010=overrides.get("transition_t8010", False),
            with_guard=overrides.get("transition_guard", True),
        )
        baseline = make_checkout(
            base / "8796",
            t8010=overrides.get("baseline_t8010", False),
            with_guard=overrides.get("baseline_guard", True),
        )
        return historical, transition, baseline

    def test_expected_historical_to_modern_transition_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(audit_history(*self._fixtures(temp)), [])

    def test_fails_when_historical_allowlist_loses_t8010(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_history(*self._fixtures(temp, historical_t8010=False))
            self.assertTrue(
                any("xnu-7195.121.3" in error and "allowlist" in error for error in errors)
            )

    def test_fails_when_modern_baseline_reintroduces_t8010(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_history(*self._fixtures(temp, baseline_t8010=True))
            self.assertTrue(
                any("xnu-8796.141.3" in error and "allowlist" in error for error in errors)
            )

    def test_fails_when_intermediate_snapshot_reintroduces_t8010(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_history(*self._fixtures(temp, transition_t8010=True))
            self.assertTrue(
                any("xnu-8019.80.24" in error and "allowlist" in error for error in errors)
            )

    def test_fails_when_historical_h9_header_is_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_history(*self._fixtures(temp, historical_h9=False))
            self.assertTrue(any("historical H9.h is missing" in error for error in errors))

    def test_fails_when_historical_machine_flag_is_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_history(*self._fixtures(temp, historical_machine_flag=False))
            self.assertTrue(
                any("missing MACHINE_FLAGS_ARM64_T8010" in error for error in errors)
            )

    def test_fails_when_transition_drops_machine_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            errors = audit_history(*self._fixtures(temp, transition_guard=False))
            self.assertTrue(
                any("xnu-8019.80.24" in error and "rejection guard" in error for error in errors)
            )


if __name__ == "__main__":
    unittest.main()
