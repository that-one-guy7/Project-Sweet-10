#!/usr/bin/env python3
"""Read-only audit of T8010/H9 presence across ten pinned public XNU releases.

This checks source structure only. It does not edit, build, or configure XNU,
and it does not establish that any release supports iPhone9,1 hardware.
"""
from pathlib import Path
import sys

from audit_xnu_machine_history import _audit_one_tree


SNAPSHOTS = (
    ("xnu-7195.121.3", True),
    ("xnu-8020.101.4", False),
    ("xnu-8019.80.24", False),
    ("xnu-8796.101.5", False),
    ("xnu-8796.141.3", False),
    ("xnu-12377.1.9", False),
    ("xnu-10002.1.13", False),
    ("xnu-10002.41.9", False),
    ("xnu-10002.61.3", False),
    ("xnu-10002.81.5", False),
)


def audit_public_matrix(roots):
    """Return source-structure errors for the ten pinned XNU source trees."""
    roots = tuple(Path(root).resolve() for root in roots)
    if len(roots) != len(SNAPSHOTS):
        return [
            "expected {} source directories, received {}".format(
                len(SNAPSHOTS), len(roots)
            )
        ]

    errors = []
    for (label, expect_t8010), root in zip(SNAPSHOTS, roots):
        _audit_one_tree(label, root, expect_t8010, errors)
    return errors


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != len(SNAPSHOTS):
        print(
            "Usage: python3 tools/audit_xnu_public_source_matrix.py "
            "PATH_7195 PATH_8020 PATH_8019 PATH_8796_101 "
            "PATH_8796_141 PATH_12377 PATH_10002_1_13 "
            "PATH_10002_41_9 PATH_10002_61_3 PATH_10002_81_5"
        )
        return 2

    errors = audit_public_matrix(args)
    if errors:
        for error in errors:
            print("FAIL: {}".format(error))
        return 1

    print("PASS: xnu-7195.121.3 contains the historical T8010/H9 profile.")
    print(
        "PASS: xnu-8020.101.4, xnu-8019.80.24, xnu-8796.101.5, "
        "xnu-8796.141.3, xnu-12377.1.9, and all four audited "
        "xnu-10002 tags omit T8010/H9 at the audited paths."
    )
    print(
        "PASS: all ten snapshots retain the MakeInc.kernel "
        "machine-configuration rejection guard."
    )
    print(
        "NOTE: these public snapshots do not identify the exact source or "
        "product-specific build inputs for either supplied shipped KernelCache."
    )
    print(
        "NOTE: this audit does not build XNU, create a kernel configuration, "
        "or establish device support."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
