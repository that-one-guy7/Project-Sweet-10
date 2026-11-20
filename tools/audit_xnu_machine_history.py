#!/usr/bin/env python3
"""Audit the public XNU T8010 machine-profile transition using local checkouts.

This is a read-only structural audit. It does not build XNU or establish device support.
"""
from pathlib import Path
import re
import sys


ASSIGNMENT_RE = re.compile(
    r"^\s*SUPPORTED_ARM64_MACHINE_CONFIGS\s*(?::=|=)\s*(.*?)\s*$",
    re.MULTILINE,
)
MACHINE_FLAG_RE = re.compile(
    r"^\s*MACHINE_FLAGS_ARM64_T8010\s*(?::=|=)\s*(.*?)\s*$",
    re.MULTILINE,
)
CONFIG_GUARD = (
    "ifeq ($(filter $(CURRENT_MACHINE_CONFIG),"
    "$(SUPPORTED_$(CURRENT_ARCH_CONFIG)_MACHINE_CONFIGS)),)"
)
CONFIG_ERROR = (
    "$(error Unsupported CURRENT_MACHINE_CONFIG "
    "$(CURRENT_MACHINE_CONFIG))"
)
BOARD_CONFIG = Path("pexpert/pexpert/arm64/board_config.h")
H9_HEADER = Path("pexpert/pexpert/arm64/H9.h")
MAKEINC_DEF = Path("makedefs/MakeInc.def")
MAKEINC_KERNEL = Path("makedefs/MakeInc.kernel")


def _read(path, description, errors):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append("{}: cannot read {}: {}".format(description, path, exc))
        return None


def _normal_arm64_machine_list(makeinc_def):
    """Return the last non-NONE ARM64 machine list, ignoring sim/host assignments."""
    assignments = ASSIGNMENT_RE.findall(makeinc_def)
    normal = [
        value for value in assignments
        if value.strip() and value.strip() != "NONE"
    ]
    if not normal:
        return None
    return set(normal[-1].split())


def _audit_one_tree(label, root, expect_t8010, errors):
    if not root.is_dir():
        errors.append("{}: checkout directory does not exist: {}".format(label, root))
        return

    makeinc_def = _read(root / MAKEINC_DEF, "{} MakeInc.def".format(label), errors)
    makeinc_kernel = _read(
        root / MAKEINC_KERNEL, "{} MakeInc.kernel".format(label), errors
    )
    board_config = _read(
        root / BOARD_CONFIG, "{} board_config.h".format(label), errors
    )
    if makeinc_def is None or makeinc_kernel is None or board_config is None:
        return

    machine_list = _normal_arm64_machine_list(makeinc_def)
    if machine_list is None:
        errors.append(
            "{}: no normal (non-NONE) SUPPORTED_ARM64_MACHINE_CONFIGS "
            "assignment found".format(label)
        )
    elif ("T8010" in machine_list) != expect_t8010:
        expectation = "contains" if expect_t8010 else "does not contain"
        errors.append(
            "{}: normal ARM64 machine allowlist {} T8010; got {}".format(
                label, expectation, sorted(machine_list)
            )
        )

    flag_match = MACHINE_FLAG_RE.search(makeinc_def)
    if expect_t8010:
        if not flag_match:
            errors.append("{}: missing MACHINE_FLAGS_ARM64_T8010 assignment".format(label))
        else:
            flag_value = flag_match.group(1)
            if (
                "ARM64_BOARD_CONFIG_T8010" not in flag_value
                or "-mcpu=hurricane" not in flag_value
            ):
                errors.append(
                    "{}: T8010 machine flags do not include the historical "
                    "board define and Hurricane compiler target".format(label)
                )
    elif flag_match:
        errors.append(
            "{}: unexpected MACHINE_FLAGS_ARM64_T8010 assignment remains".format(label)
        )

    board_has_t8010 = "#ifdef ARM64_BOARD_CONFIG_T8010" in board_config
    board_includes_h9 = "#include <pexpert/arm64/H9.h>" in board_config
    h9_path = root / H9_HEADER
    h9_exists = h9_path.is_file()
    if expect_t8010:
        if not board_has_t8010:
            errors.append(
                "{}: board_config.h lacks the ARM64_BOARD_CONFIG_T8010 block".format(label)
            )
        if not board_includes_h9:
            errors.append(
                "{}: T8010 board configuration does not include H9.h".format(label)
            )
        if not h9_exists:
            errors.append("{}: historical H9.h is missing".format(label))
        else:
            h9_text = _read(h9_path, "{} H9.h".format(label), errors)
            if h9_text is not None and "#define APPLEHURRICANE" not in h9_text:
                errors.append("{}: H9.h does not declare APPLEHURRICANE".format(label))
    else:
        if board_has_t8010:
            errors.append(
                "{}: unexpected T8010 board-configuration block remains".format(label)
            )
        if board_includes_h9:
            errors.append(
                "{}: unexpected H9.h include remains in board_config.h".format(label)
            )
        if h9_exists:
            errors.append(
                "{}: H9.h unexpectedly exists at the historical path".format(label)
            )

    if CONFIG_GUARD not in makeinc_kernel or CONFIG_ERROR not in makeinc_kernel:
        errors.append(
            "{}: MakeInc.kernel does not contain the expected "
            "machine-configuration rejection guard".format(label)
        )


def audit_history(historical, transition, baseline):
    """Return all structural discrepancies across the three pinned XNU snapshots."""
    errors = []
    _audit_one_tree("xnu-7195.121.3", Path(historical), True, errors)
    _audit_one_tree("xnu-8019.80.24", Path(transition), False, errors)
    _audit_one_tree("xnu-8796.141.3", Path(baseline), False, errors)
    return errors


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 3:
        print(
            "Usage: python3 tools/audit_xnu_machine_history.py "
            "PATH_TO_XNU_7195 PATH_TO_XNU_8019 PATH_TO_XNU_8796"
        )
        return 2

    historical, transition, baseline = (Path(value).resolve() for value in args)
    errors = audit_history(historical, transition, baseline)
    if errors:
        for error in errors:
            print("FAIL: {}".format(error))
        return 1

    print("PASS: xnu-7195.121.3 contains the historical T8010/H9 machine profile.")
    print(
        "PASS: xnu-8019.80.24 and xnu-8796.141.3 omit the T8010/H9 profile "
        "at the audited paths."
    )
    print("PASS: all three snapshots retain the MakeInc.kernel machine-selection guard.")
    print(
        "NOTE: this describes public source snapshots only; it does not explain "
        "Apple's rationale,"
    )
    print(
        "      establish private/downstream source state, prove build viability, "
        "or claim iPhone9,1 support."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
