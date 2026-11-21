#!/usr/bin/env python3
"""Check selected launchd Program paths under already-mounted iOS filesystem roots.

Only filesystem metadata is queried. Symlinks are reported but never followed;
program contents are never read or executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any

EXPECTED_SCHEMA = "project-sweet-10.launchd-inventory.v1"
OUTPUT_SCHEMA = "project-sweet-10.launchd-program-path-presence.v1"
DEFAULT_LABELS = (
    "com.apple.backboardd",
    "com.apple.runningboardd",
    "com.apple.SpringBoard",
    "com.apple.configd",
    "com.apple.notifyd",
    "com.apple.mediaserverd",
    "com.apple.wifid",
    "com.apple.bluetoothd",
    "com.apple.mobileactivationd",
)


class InspectionError(ValueError):
    """Raised for invalid inventory inputs or filesystem roots."""


def load_inventory(path: str | Path) -> tuple[dict[str, Any], str]:
    source = Path(path).expanduser()
    try:
        raw = source.read_bytes()
        document = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise InspectionError(f"cannot read launchd inventory {source}: {exc}") from exc
    if not isinstance(document, dict):
        raise InspectionError(f"{source}: top-level JSON value must be an object")
    if document.get("schema") != EXPECTED_SCHEMA:
        raise InspectionError(
            f"{source}: expected schema {EXPECTED_SCHEMA!r}, got {document.get('schema')!r}"
        )
    jobs = document.get("jobs")
    if not isinstance(jobs, list) or not all(isinstance(job, dict) for job in jobs):
        raise InspectionError(f"{source}: 'jobs' must be an array of objects")
    return document, hashlib.sha256(raw).hexdigest()


def _program_components(program: Any) -> tuple[str, ...] | None:
    if not isinstance(program, str) or not program.startswith("/") or "\x00" in program:
        return None
    parsed = PurePosixPath(program)
    parts = parsed.parts[1:]
    if not parts or any(part in ("", ".", "..") for part in parts):
        return None
    return tuple(parts)


def inspect_relative_path(root: Path, relative_parts: tuple[str, ...]) -> str:
    """Inspect each path component with lstat; do not traverse symlinks."""
    current = root
    for index, component in enumerate(relative_parts):
        current = current / component
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            return "missing"
        except NotADirectoryError:
            return "not-directory"
        except PermissionError:
            return "permission-denied"
        except OSError:
            return "stat-error"

        is_final = index == len(relative_parts) - 1
        if stat.S_ISLNK(metadata.st_mode):
            return "final-symlink" if is_final else "symlink-component"
        if not is_final and not stat.S_ISDIR(metadata.st_mode):
            return "not-directory"
        if is_final:
            if stat.S_ISREG(metadata.st_mode):
                return "regular-file"
            if stat.S_ISDIR(metadata.st_mode):
                return "directory"
            return "other-file-type"
    return "missing"


def _aggregate_status(checks: list[dict[str, Any]]) -> str:
    states = {item["state"] for item in checks}
    if "regular-file" in states:
        return "regular-file-found"
    if "final-symlink" in states or "symlink-component" in states:
        return "symlink-present-unresolved"
    if "directory" in states:
        return "directory-at-program-path"
    if "other-file-type" in states:
        return "other-file-type-found"
    if states & {"permission-denied", "stat-error", "not-directory"}:
        return "inspection-incomplete"
    return "not-found-under-scanned-roots"


def _inspect_build(
    document: dict[str, Any],
    inventory_sha256: str,
    roots: list[tuple[str, Path]],
    labels: tuple[str, ...],
    wrapper_depth: int,
) -> dict[str, Any]:
    if not roots:
        raise InspectionError("at least one filesystem root is required per build")

    normalized_roots: list[tuple[str, Path]] = []
    for label, root_value in roots:
        try:
            root = Path(root_value).expanduser().resolve()
            is_directory = root.is_dir()
        except (OSError, RuntimeError) as exc:
            raise InspectionError(f"cannot inspect filesystem root {root_value}: {exc}") from exc
        if not is_directory:
            raise InspectionError(f"filesystem root is not a directory: {root_value}")
        normalized_roots.append((label, root))

    selected = set(labels)
    selected_jobs = [job for job in document["jobs"] if job.get("label") in selected]
    jobs_out: list[dict[str, Any]] = []
    for job in sorted(
        selected_jobs,
        key=lambda item: (str(item.get("label", "")), str(item.get("launchd_key", ""))),
    ):
        program = job.get("program")
        parts = _program_components(program)
        if parts is None:
            jobs_out.append({
                "label": job.get("label"),
                "launchd_key": job.get("launchd_key"),
                "program": program,
                "status": "invalid-or-missing-absolute-program-path",
                "checks": [],
            })
            continue

        checks: list[dict[str, Any]] = []
        for root_label, root in normalized_roots:
            for depth in range(wrapper_depth + 1):
                prefix = ("root",) * depth
                candidate_parts = prefix + parts
                state = inspect_relative_path(root, candidate_parts)
                checks.append({
                    "filesystem_root": root_label,
                    "root_wrapper_depth": depth,
                    "relative_candidate_path": "/".join(candidate_parts),
                    "state": state,
                })
        jobs_out.append({
            "label": job.get("label"),
            "launchd_key": job.get("launchd_key"),
            "program": program,
            "status": _aggregate_status(checks),
            "checks": checks,
        })

    status_counts: dict[str, int] = {}
    for job in jobs_out:
        status_counts[job["status"]] = status_counts.get(job["status"], 0) + 1
    return {
        "launchd_inventory_sha256": inventory_sha256,
        "launchd_source_plist_sha256": document.get("source_sha256"),
        "filesystem_root_count": len(normalized_roots),
        "filesystem_roots": [label for label, _ in normalized_roots],
        "root_wrapper_depths_checked": list(range(wrapper_depth + 1)),
        "selected_job_count": len(jobs_out),
        "status_counts": dict(sorted(status_counts.items())),
        "jobs": jobs_out,
    }


def build_report(
    target_inventory_path: str | Path,
    donor_inventory_path: str | Path,
    target_roots: list[tuple[str, Path]],
    donor_roots: list[tuple[str, Path]],
    labels: tuple[str, ...] = DEFAULT_LABELS,
    wrapper_depth: int = 2,
) -> dict[str, Any]:
    if not 0 <= wrapper_depth <= 4:
        raise InspectionError("wrapper depth must be between 0 and 4")
    target_doc, target_hash = load_inventory(target_inventory_path)
    donor_doc, donor_hash = load_inventory(donor_inventory_path)
    return {
        "schema": OUTPUT_SCHEMA,
        "target_19H422": _inspect_build(
            target_doc, target_hash, target_roots, labels, wrapper_depth
        ),
        "donor_20H392": _inspect_build(
            donor_doc, donor_hash, donor_roots, labels, wrapper_depth
        ),
        "scope_notes": [
            "Checks only the selected LaunchDaemons job Program path strings against the explicitly supplied filesystem roots.",
            "Checks the root itself and bounded repeated root/ wrapper prefixes; it does not recursively search the filesystem.",
            "Uses lstat on each path component and stops at symlinks; symlink targets are not followed.",
            "Does not open, hash, execute, or inspect program file contents.",
            "A regular-file result proves only that a regular filesystem object was present at that path during this scan; it does not validate Mach-O format, signature, entitlements, ABI, or loadability.",
            "not-found-under-scanned-roots means only that the path was not found at the checked prefixes in the supplied roots; split volumes or other locations may contain it.",
            "This is static host-side metadata and does not establish launchd registration, process launch, runtime behavior, kernel compatibility, or SpringBoard readiness.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-launchd", required=True, help="19H422 launchd inventory JSON")
    parser.add_argument("--donor-launchd", required=True, help="20H392 launchd inventory JSON")
    parser.add_argument("--target-root", action="append", required=True, help="19H422 filesystem root; repeat for split roots")
    parser.add_argument("--donor-root", action="append", required=True, help="20H392 filesystem root; repeat for OS/SystemOS volumes")
    parser.add_argument("--label", action="append", default=None, help="job label to inspect; repeatable (default: selected GUI/platform jobs)")
    parser.add_argument("--wrapper-depth", type=int, default=2, help="also check this many nested root/ wrapper levels (default: 2; max: 4)")
    args = parser.parse_args(argv)

    try:
        labels = tuple(args.label or DEFAULT_LABELS)
        target_roots = [(f"target_root_{i}", Path(value)) for i, value in enumerate(args.target_root)]
        donor_roots = [(f"donor_root_{i}", Path(value)) for i, value in enumerate(args.donor_root)]
        report = build_report(
            args.target_launchd,
            args.donor_launchd,
            target_roots,
            donor_roots,
            labels,
            args.wrapper_depth,
        )
    except InspectionError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
