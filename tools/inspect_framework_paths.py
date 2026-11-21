#!/usr/bin/env python3
"""Inspect selected framework install paths in an already-mounted iOS filesystem.

The tool checks filesystem metadata only. It uses lstat on every component,
stops at symlinks, and never opens, hashes, or executes framework binaries.
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

EXPECTED_SCHEMA = "project-sweet-10.framework-path-candidates.v1"
OUTPUT_SCHEMA = "project-sweet-10.framework-path-presence.v1"


class InspectionError(ValueError):
    """Raised for invalid candidate input or filesystem roots."""


def load_candidates(path: str | Path) -> tuple[dict[str, Any], str]:
    source = Path(path).expanduser()
    try:
        raw = source.read_bytes()
        document = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise InspectionError(f"cannot read candidate JSON {source}: {exc}") from exc

    if not isinstance(document, dict):
        raise InspectionError("candidate JSON top-level value must be an object")
    if document.get("schema") != EXPECTED_SCHEMA:
        raise InspectionError(
            f"expected schema {EXPECTED_SCHEMA!r}, got {document.get('schema')!r}"
        )

    candidates = document.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise InspectionError("'candidates' must be a non-empty array")
    seen_ids: set[str] = set()
    for index, item in enumerate(candidates):
        if not isinstance(item, dict):
            raise InspectionError(f"candidate {index} must be an object")
        candidate_id = item.get("id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise InspectionError(f"candidate {index} has an invalid id")
        if candidate_id in seen_ids:
            raise InspectionError(f"duplicate candidate id: {candidate_id}")
        seen_ids.add(candidate_id)
        if _path_components(item.get("path")) is None:
            raise InspectionError(f"candidate {candidate_id}: path must be a safe absolute path")
    return document, hashlib.sha256(raw).hexdigest()


def _path_components(value: Any) -> tuple[str, ...] | None:
    if not isinstance(value, str) or not value.startswith("/") or "\x00" in value:
        return None
    raw_parts = value.split("/")[1:]
    if not raw_parts or any(part in ("", ".", "..") for part in raw_parts):
        return None
    parsed = PurePosixPath(value)
    parts = parsed.parts[1:]
    if not parts or any(part in (".", "..") for part in parts):
        return None
    return tuple(parts)


def inspect_relative_path(root: Path, relative_parts: tuple[str, ...]) -> str:
    """Inspect each path component with lstat and never traverse symlinks."""
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


def aggregate_status(checks: list[dict[str, Any]]) -> str:
    states = {check["state"] for check in checks}
    if "regular-file" in states:
        return "regular-file-found"
    if "final-symlink" in states or "symlink-component" in states:
        return "symlink-present-unresolved"
    if "directory" in states:
        return "directory-at-path"
    if "other-file-type" in states:
        return "other-file-type-found"
    if states & {"permission-denied", "stat-error", "not-directory"}:
        return "inspection-incomplete"
    return "not-found-under-scanned-roots"


def build_report(
    candidates_path: str | Path,
    target_roots: list[tuple[str, Path]],
    wrapper_depth: int = 2,
) -> dict[str, Any]:
    if not 0 <= wrapper_depth <= 4:
        raise InspectionError("wrapper depth must be between 0 and 4")
    if not target_roots:
        raise InspectionError("at least one target filesystem root is required")

    document, candidate_sha256 = load_candidates(candidates_path)
    normalized_roots: list[tuple[str, Path]] = []
    for label, root_value in target_roots:
        try:
            root = Path(root_value).expanduser().resolve()
            is_directory = root.is_dir()
        except (OSError, RuntimeError) as exc:
            raise InspectionError(f"cannot inspect filesystem root {root_value}: {exc}") from exc
        if not is_directory:
            raise InspectionError(f"filesystem root is not a directory: {root_value}")
        normalized_roots.append((label, root))

    rows: list[dict[str, Any]] = []
    for candidate in document["candidates"]:
        parts = _path_components(candidate["path"])
        # load_candidates already validated every path.
        assert parts is not None
        checks: list[dict[str, Any]] = []
        for root_label, root in normalized_roots:
            for depth in range(wrapper_depth + 1):
                relative_parts = ("root",) * depth + parts
                checks.append({
                    "filesystem_root": root_label,
                    "root_wrapper_depth": depth,
                    "relative_candidate_path": "/".join(relative_parts),
                    "state": inspect_relative_path(root, relative_parts),
                })
        rows.append({
            "id": candidate["id"],
            "path": candidate["path"],
            "group": candidate.get("group"),
            "reason": candidate.get("reason"),
            "status": aggregate_status(checks),
            "checks": checks,
        })

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    return {
        "schema": OUTPUT_SCHEMA,
        "target_reference": document.get("target_reference"),
        "donor_reference_context": document.get("donor_reference"),
        "candidate_file_sha256": candidate_sha256,
        "filesystem_root_count": len(normalized_roots),
        "filesystem_roots": [label for label, _ in normalized_roots],
        "root_wrapper_depths_checked": list(range(wrapper_depth + 1)),
        "candidate_count": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "candidates": rows,
        "scope_notes": [
            "Checks only the exact absolute candidate paths in the supplied JSON under the explicitly supplied target roots.",
            "Checks the root itself and bounded repeated root/ wrapper prefixes; it does not recursively search for basenames or other paths.",
            "Uses lstat on each path component and stops at symlinks; symlink targets are not followed.",
            "Does not open, hash, parse, or execute framework files.",
            "regular-file-found means only that a regular filesystem object was present at one checked path during this scan.",
            "not-found-under-scanned-roots is limited to the exact candidate paths, roots, and wrapper depths in this report; other paths, volumes, Cryptexes, or runtime locations may contain related files.",
            "Cache-image-list membership and filesystem path presence are separate evidence categories.",
            "This is static host-side metadata and does not establish dyld resolution, ABI compatibility, framework loading, service startup, hardware operation, kernel boot, or SpringBoard readiness."
        ]
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths-json", required=True, help="JSON file containing selected absolute framework paths")
    parser.add_argument("--target-root", action="append", required=True, help="19H422 mounted filesystem root; repeat for additional roots")
    parser.add_argument("--wrapper-depth", type=int, default=2, help="also check this many nested root/ wrapper levels (default: 2; max: 4)")
    args = parser.parse_args(argv)

    try:
        target_roots = [
            (f"target_root_{index}", Path(value))
            for index, value in enumerate(args.target_root)
        ]
        report = build_report(args.paths_json, target_roots, args.wrapper_depth)
    except InspectionError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
