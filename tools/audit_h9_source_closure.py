#!/usr/bin/env python3
"""Compare historical H9 feature-macro consumers across two public XNU trees.

This is a read-only source scanner. It does not modify or build XNU and does
not establish hardware compatibility.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

H9_PATH = Path("pexpert/pexpert/arm64/H9.h")
H13_PATH = Path("pexpert/pexpert/arm64/H13.h")

DEFINE_RE = re.compile(r"^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\b(.*)$")
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]')
SOURCE_SUFFIXES = {
    ".c", ".h", ".S", ".s", ".cc", ".cpp", ".cxx", ".hpp", ".hh",
    ".inc", ".def", ".mk", ".pl", ".py", ".sh", ".y", ".l",
}
SKIP_DIRS = {".git", "Build", "DerivedData", "obj", "out", "__pycache__"}
SKIP_MACROS = {"_PEXPERT_ARM64_H9_H"}


class AuditError(Exception):
    """Raised when a source tree cannot be audited safely."""


def iter_source_files(root: Path):
    """Yield candidate source/build files, pruning generated and VCS trees."""
    for current, dirs, filenames in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        current_path = Path(current)
        for filename in sorted(filenames):
            path = current_path / filename
            if (
                path.suffix in SOURCE_SUFFIXES
                or filename == "Makefile"
                or filename.startswith("Makefile.")
            ):
                yield path


def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise AuditError("cannot read {}: {}".format(path, exc)) from exc


def parse_defines(header: Path):
    """Return ordered object-like macro definitions from H9.h."""
    definitions = []
    for line_no, line in enumerate(read_text(header).splitlines(), 1):
        match = DEFINE_RE.match(line)
        if not match:
            continue
        name = match.group(1)
        if name in SKIP_MACROS:
            continue
        definitions.append({
            "name": name,
            "line": line_no,
            "value": match.group(2).strip(),
        })
    if not definitions:
        raise AuditError("no feature macro definitions found in {}".format(header))
    return definitions


def parse_any_defines(header: Path):
    result = []
    for line_no, line in enumerate(read_text(header).splitlines(), 1):
        match = DEFINE_RE.match(line)
        if match:
            result.append({
                "name": match.group(1),
                "line": line_no,
                "value": match.group(2).strip(),
            })
    return result


def classify_line(line: str):
    stripped = line.strip()
    if re.match(r"#\s*(if|ifdef|ifndef|elif)\b", stripped):
        return "preprocessor-condition"
    if re.match(r"#\s*(define|undef)\b", stripped):
        return "preprocessor-definition"
    if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
        return "comment"
    return "code-or-other"


def scan_references(root: Path, definitions, excluded_paths=()):
    """Find identifier-token references in candidate source/build files."""
    excluded = {Path(p).resolve() for p in excluded_paths}
    patterns = {
        item["name"]: re.compile(
            r"(?<![A-Za-z0-9_])" + re.escape(item["name"]) + r"(?![A-Za-z0-9_])"
        )
        for item in definitions
    }
    found = {name: [] for name in patterns}
    file_count = 0

    for path in iter_source_files(root):
        if path.resolve() in excluded:
            continue
        relative = path.relative_to(root).as_posix()
        file_text = read_text(path)
        file_count += 1
        for line_no, line in enumerate(file_text.splitlines(), 1):
            for name, pattern in patterns.items():
                if pattern.search(line):
                    found[name].append({
                        "path": relative,
                        "line": line_no,
                        "context": classify_line(line),
                        "text": line.strip()[:240],
                    })
    return found, file_count


def _include_roots(root: Path):
    return [
        root,
        root / "pexpert",
        root / "osfmk",
        root / "bsd",
        root / "libkern",
        root / "iokit",
        root / "security",
        root / "san",
        root / "EXTERNAL_HEADERS",
    ]


def resolve_include(root: Path, including_file: Path, include_name: str):
    """Resolve an include against common XNU source include roots."""
    candidates = [including_file.parent / include_name]
    candidates.extend(base / include_name for base in _include_roots(root))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def include_closure(root: Path, entry: Path):
    """Return the locally resolvable include graph starting at one header."""
    graph = {}
    unresolved = []
    pending = [entry.resolve()]
    visited = set()

    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        if not current.is_file():
            unresolved.append({"from": str(current), "include": "<entry-missing>"})
            continue

        relative = current.relative_to(root.resolve()).as_posix()
        includes = []
        for line_no, line in enumerate(read_text(current).splitlines(), 1):
            match = INCLUDE_RE.match(line)
            if not match:
                continue
            include_name = match.group(1)
            target = resolve_include(root, current, include_name)
            record = {"line": line_no, "include": include_name, "resolved": None}
            if target is None:
                unresolved.append({
                    "from": relative,
                    "line": line_no,
                    "include": include_name,
                })
            else:
                target_relative = target.relative_to(root.resolve()).as_posix()
                record["resolved"] = target_relative
                pending.append(target)
            includes.append(record)
        graph[relative] = includes

    return {
        "entry": entry.relative_to(root.resolve()).as_posix(),
        "resolved_file_count": len(graph),
        "files": graph,
        "unresolved_includes": unresolved,
        "note": (
            "Only locally resolvable quoted/angled includes are listed; compiler "
            "SDK, generated headers, and build-system include search flags are "
            "not reconstructed."
        ),
    }


def audit_pair(old_root: Path, new_root: Path):
    old_root = Path(old_root).resolve()
    new_root = Path(new_root).resolve()
    if not old_root.is_dir():
        raise AuditError("historical source root is not a directory: {}".format(old_root))
    if not new_root.is_dir():
        raise AuditError("candidate source root is not a directory: {}".format(new_root))

    h9_header = old_root / H9_PATH
    if not h9_header.is_file():
        raise AuditError("historical H9 header not found: {}".format(h9_header))

    definitions = parse_defines(h9_header)
    old_refs, old_files = scan_references(
        old_root, definitions, excluded_paths=(h9_header,)
    )
    new_refs, new_files = scan_references(new_root, definitions)

    h13 = new_root / H13_PATH
    h13_definitions = {}
    if h13.is_file():
        h13_definitions = {
            item["name"]: item["value"] for item in parse_any_defines(h13)
        }

    comparisons = []
    for item in definitions:
        name = item["name"]
        old_items = old_refs[name]
        new_items = new_refs[name]
        old_paths = sorted({x["path"] for x in old_items})
        new_paths = sorted({x["path"] for x in new_items})
        comparisons.append({
            "name": name,
            "h9_value": item["value"],
            "h9_definition_line": item["line"],
            "old_reference_count": len(old_items),
            "old_reference_paths": old_paths,
            "old_occurrences": old_items,
            "new_reference_count": len(new_items),
            "new_reference_paths": new_paths,
            "new_occurrences": new_items,
            "present_in_new_h13": name in h13_definitions,
            "new_h13_value": h13_definitions.get(name),
            "new_only_reference_paths": sorted(set(new_paths) - set(old_paths)),
            "old_only_reference_paths": sorted(set(old_paths) - set(new_paths)),
        })

    return {
        "schema_version": 1,
        "method": (
            "identifier-token scan of candidate source/build files; not a "
            "compiler/preprocessor dependency graph"
        ),
        "old_source": {
            "label": "historical-xnu-7195.121.3",
            "source_files_scanned": old_files,
        },
        "new_source": {
            "label": "candidate-xnu-8796.141.3",
            "source_files_scanned": new_files,
        },
        "historical_h9_header": H9_PATH.as_posix(),
        "modern_profile_header": H13_PATH.as_posix() if h13.is_file() else None,
        "h9_macro_count": len(definitions),
        "macros": comparisons,
        "old_h9_include_closure": include_closure(old_root, h9_header),
        "caveats": [
            (
                "Textual occurrences include conditional checks, definitions, "
                "comments, and other uses; inspect context before classifying a "
                "reference as active code."
            ),
            (
                "A missing textual occurrence is not proof that a capability is "
                "unsupported; code may be generated, renamed, indirect, or supplied "
                "by private build inputs."
            ),
            (
                "The scanner does not evaluate preprocessor conditions, macro "
                "expansion, generated headers, or compiler configuration."
            ),
            (
                "No macro value is inferred from H13 when H13 does not define the "
                "corresponding H9 feature."
            ),
            (
                "This is static source evidence only; it does not build XNU or "
                "establish iPhone9,1 compatibility."
            ),
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("historical_xnu_root", type=Path)
    parser.add_argument("candidate_xnu_root", type=Path)
    parser.add_argument("--json-output", type=Path, help="write machine-readable results")
    args = parser.parse_args(argv)

    try:
        report = audit_pair(args.historical_xnu_root, args.candidate_xnu_root)
    except AuditError as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

    print("H9 source closure scan")
    print("Historical files scanned:", report["old_source"]["source_files_scanned"])
    print("Candidate files scanned:", report["new_source"]["source_files_scanned"])
    print("H9 feature macros:", report["h9_macro_count"])
    for item in report["macros"]:
        print(
            "{}: historical refs={} in {} files; candidate refs={} in {} files; "
            "H13-defined={}".format(
                item["name"],
                item["old_reference_count"],
                len(item["old_reference_paths"]),
                item["new_reference_count"],
                len(item["new_reference_paths"]),
                item["present_in_new_h13"],
            )
        )
    if args.json_output:
        print("JSON report:", args.json_output)
    print("NOTE: textual scan only; inspect preprocessor context and unresolved includes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
