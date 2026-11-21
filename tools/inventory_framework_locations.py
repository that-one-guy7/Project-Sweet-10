#!/usr/bin/env python3
"""Recursively inventory selected GUI framework names in a mounted iOS filesystem.

This is a host-side metadata scan. It reads candidate JSON and directory
metadata only; it does not open, hash, parse, or execute framework files.
Directory symlinks are recorded when their names match and are never followed.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

from inspect_framework_paths import InspectionError, load_candidates

OUTPUT_SCHEMA = "project-sweet-10.framework-location-inventory.v2"


def _metadata_kind(metadata: os.stat_result) -> str:
    """Return a stable label without opening or following the entry."""
    mode = metadata.st_mode
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "regular-file"
    return "other-file-type"


def _relative_path(root: Path, path: str) -> str:
    try:
        return Path(path).relative_to(root).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _candidate_name_index(candidates: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    """Index final binary names and enclosing .framework bundle names."""
    index: dict[str, list[dict[str, str]]] = {}
    for candidate in candidates:
        parts = Path(candidate["path"]).parts
        binary_name = parts[-1]
        index.setdefault(binary_name, []).append({
            "candidate_id": candidate["id"],
            "candidate_path": candidate["path"],
            "match_kind": "binary-name",
        })
        if len(parts) >= 2 and parts[-2].endswith(".framework"):
            bundle_name = parts[-2]
            index.setdefault(bundle_name, []).append({
                "candidate_id": candidate["id"],
                "candidate_path": candidate["path"],
                "match_kind": "framework-bundle-name",
            })
    for name in index:
        unique = {
            (item["candidate_id"], item["candidate_path"], item["match_kind"]): item
            for item in index[name]
        }
        index[name] = [unique[key] for key in sorted(unique)]
    return index


def build_inventory(candidates_path: str | Path, target_root: str | Path) -> dict[str, Any]:
    """Search one explicit tree recursively without following symlinks."""
    document, candidate_sha256 = load_candidates(candidates_path)
    root = Path(target_root).expanduser().absolute()
    try:
        root_metadata = os.lstat(root)
    except OSError as exc:
        raise InspectionError(f"cannot inspect target root {root}: {exc}") from exc
    if stat.S_ISLNK(root_metadata.st_mode):
        raise InspectionError(f"target root must not itself be a symlink: {root}")
    if not stat.S_ISDIR(root_metadata.st_mode):
        raise InspectionError(f"target root is not a directory: {root}")

    candidate_names = _candidate_name_index(document["candidates"])
    matches: list[dict[str, Any]] = []
    walk_errors: list[dict[str, str]] = []
    entry_errors: list[dict[str, str]] = []
    directories_scanned = 0
    entries_seen = 0

    def record_match(entry_path: str, name: str, metadata: os.stat_result) -> None:
        matches.append({
            "path": _relative_path(root, entry_path),
            "basename": name,
            "entry_kind": _metadata_kind(metadata),
            "matched_candidates": candidate_names[name],
        })

    def record_error(collection: list[dict[str, str]], path: str, exc: OSError) -> None:
        collection.append({
            "path": _relative_path(root, path),
            "error_type": type(exc).__name__,
            "message": str(exc),
        })

    def on_walk_error(exc: OSError) -> None:
        error_path = exc.filename if isinstance(exc.filename, str) else str(root)
        record_error(walk_errors, error_path, exc)

    for directory, dirnames, filenames in os.walk(
        str(root), topdown=True, onerror=on_walk_error, followlinks=False
    ):
        directories_scanned += 1
        entries_seen += len(dirnames) + len(filenames)

        # os.walk(followlinks=False) does not recurse into directory symlinks.
        # Filter them explicitly as well, so the invariant is clear and tested.
        kept_directories: list[str] = []
        for name in sorted(dirnames):
            entry_path = os.path.join(directory, name)
            try:
                metadata = os.lstat(entry_path)
            except OSError as exc:
                record_error(entry_errors, entry_path, exc)
                kept_directories.append(name)
                continue
            if name in candidate_names:
                record_match(entry_path, name, metadata)
            if not stat.S_ISLNK(metadata.st_mode):
                kept_directories.append(name)
        dirnames[:] = kept_directories

        for name in sorted(filenames):
            if name not in candidate_names:
                continue
            entry_path = os.path.join(directory, name)
            try:
                metadata = os.lstat(entry_path)
            except OSError as exc:
                record_error(entry_errors, entry_path, exc)
                continue
            record_match(entry_path, name, metadata)

    matches.sort(key=lambda item: (item["path"], item["basename"]))
    errors = walk_errors + entry_errors
    matches_by_id: dict[str, list[dict[str, Any]]] = {
        candidate["id"]: [] for candidate in document["candidates"]
    }
    for match in matches:
        for candidate_match in match["matched_candidates"]:
            row = {
                "path": match["path"],
                "basename": match["basename"],
                "entry_kind": match["entry_kind"],
                "match_kind": candidate_match["match_kind"],
            }
            matches_by_id[candidate_match["candidate_id"]].append(row)

    candidate_rows: list[dict[str, Any]] = []
    for candidate in document["candidates"]:
        candidate_matches = matches_by_id[candidate["id"]]
        binary_entries = [
            item for item in candidate_matches if item["match_kind"] == "binary-name"
        ]
        binary_files = [
            item for item in binary_entries if item["entry_kind"] == "regular-file"
        ]
        bundle_directories = [
            item for item in candidate_matches
            if item["match_kind"] == "framework-bundle-name"
            and item["entry_kind"] == "directory"
        ]
        if binary_files:
            status = "binary-file-found"
        elif binary_entries:
            status = "binary-name-entry-found"
        elif bundle_directories:
            status = "bundle-directory-only"
        elif candidate_matches:
            status = "bundle-name-entry-only"
        elif errors:
            status = "no-match-scan-incomplete"
        else:
            status = "no-match-in-complete-scan"
        candidate_rows.append({
            "id": candidate["id"],
            "path": candidate["path"],
            "group": candidate.get("group"),
            "reason": candidate.get("reason"),
            "binary_basename": Path(candidate["path"]).name,
            "framework_bundle_basename": (
                Path(candidate["path"]).parent.name
                if Path(candidate["path"]).parent.name.endswith(".framework")
                else None
            ),
            "status": status,
            "binary_matches": sorted(
                binary_entries,
                key=lambda item: (item["path"], item["entry_kind"]),
            ),
            "bundle_directory_matches": sorted(
                bundle_directories,
                key=lambda item: (item["path"], item["entry_kind"]),
            ),
            "matches": sorted(
                candidate_matches,
                key=lambda item: (item["path"], item["match_kind"]),
            ),
        })

    status_counts: dict[str, int] = {}
    for row in candidate_rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    return {
        "schema": OUTPUT_SCHEMA,
        "target_reference": document.get("target_reference"),
        "donor_reference_context": document.get("donor_reference"),
        "candidate_file_sha256": candidate_sha256,
        "target_root": str(root),
        "scan_status": "complete" if not errors else "incomplete",
        "summary": {
            "candidate_count": len(candidate_rows),
            "candidate_status_counts": dict(sorted(status_counts.items())),
            "directories_scanned": directories_scanned,
            "entries_seen": entries_seen,
            "matching_entries": len(matches),
            "walk_error_count": len(walk_errors),
            "entry_stat_error_count": len(entry_errors),
        },
        "candidates": candidate_rows,
        "matches": matches,
        "walk_errors": walk_errors,
        "entry_stat_errors": entry_errors,
        "scope_notes": [
            "Searches entry basenames recursively beneath only the explicitly supplied target root.",
            "Matches final binary basenames and enclosing .framework directory basenames from the candidate paths.",
            "Uses os.walk with followlinks=False and lstat metadata; matching directory symlinks are recorded but never traversed.",
            "Does not open, hash, parse, or execute framework files.",
            "A basename match anywhere in the tree is not proof that the candidate's exact install path exists or that dyld resolves it.",
            "Candidates sharing a basename can point to the same discovered entry; inspect the match path and match kind before drawing path-specific conclusions.",
            "no-match-in-complete-scan applies only to the traversed tree and its accessible directories; it says nothing about other filesystems, Cryptexes, caches, snapshots, or runtime locations.",
            "Permission and stat errors make the scan incomplete; unmatched candidates must not be described as absent when the scan is incomplete.",
            "This is filesystem metadata only and does not establish Mach-O validity, code-signature validity, ABI compatibility, dyld loading, service startup, hardware operation, kernel boot, or SpringBoard readiness.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paths-json",
        required=True,
        help="candidate JSON produced by the Project Sweet-10 framework path inventory",
    )
    parser.add_argument(
        "--target-root",
        required=True,
        help="one mounted target filesystem tree to scan recursively",
    )
    args = parser.parse_args(argv)
    try:
        report = build_inventory(args.paths_json, args.target_root)
    except InspectionError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
