#!/usr/bin/env python3
"""Map libSystem imports to exact names in its saved LC_REEXPORT_DYLIB providers.

This reads saved ipsw text logs only. A name match is direct export-list
membership, not a resolved dyld bind, ABI check, or runtime result.
"""
from __future__ import annotations
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

try:
    from tools.compare_dyld_exports import ExportLogError, parse_export_log_text
    from tools.compare_dyld_imports import ImportLogError, parse_import_log_text
except ModuleNotFoundError:
    from compare_dyld_exports import ExportLogError, parse_export_log_text
    from compare_dyld_imports import ImportLogError, parse_import_log_text

PARENT = "libSystem.B.dylib"
NO_SECTION = "no 'Dyld Exports' section was printed"


class ReexportAuditError(ValueError):
    pass


def load_provider_logs(directory: Path, build: str) -> dict:
    if not directory.is_dir():
        raise ReexportAuditError(f"provider directory does not exist: {directory}")
    paths = sorted(directory.glob(f"{build}-*.txt"))
    if not paths:
        raise ReexportAuditError(f"no {build}-*.txt provider logs found in {directory}")
    providers = {}
    for path in paths:
        key = path.stem[len(build) + 1:]
        if not key or key in providers:
            raise ReexportAuditError(f"duplicate or empty provider key: {path}")
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            rows = parse_export_log_text(text, str(path))
            providers[key] = {
                "path": path, "rows": len(rows),
                "names": {row.name for row in rows}, "has_section": True,
            }
        except ExportLogError as exc:
            if NO_SECTION in str(exc):
                providers[key] = {
                    "path": path, "rows": 0, "names": set(), "has_section": False,
                }
            else:
                raise ReexportAuditError(str(exc)) from exc
        except OSError as exc:
            raise ReexportAuditError(f"cannot read {path}: {exc}") from exc
    return providers


def audit_build(build: str, consumer: Path, provider_dir: Path) -> dict:
    try:
        parsed = parse_import_log_text(
            consumer.read_text(encoding="utf-8", errors="replace"), str(consumer)
        )
    except (OSError, ImportLogError) as exc:
        raise ReexportAuditError(str(exc)) from exc
    imports = [row.name for row in parsed if row.provider == PARENT]
    if not imports:
        raise ReexportAuditError(f"{consumer}: no undefined imports from {PARENT}")
    providers = load_provider_logs(provider_dir, build)
    name_providers = defaultdict(list)
    for key, provider in providers.items():
        for name in provider["names"]:
            name_providers[name].append(key)
    matches, ambiguous, missing = {}, {}, []
    for name in sorted(set(imports)):
        hits = tuple(sorted(name_providers.get(name, [])))
        if len(hits) == 1:
            matches[name] = hits[0]
        elif len(hits) > 1:
            ambiguous[name] = hits
        else:
            missing.append(name)
    return {
        "build": build, "imports": imports, "providers": providers,
        "matches": matches, "ambiguous": ambiguous, "missing": missing,
    }


def render_report(target: dict, donor: dict) -> str:
    lines = ["Project Sweet-10: libSystem re-export import-name audit",
             "Evidence: saved ipsw Symtab and Dyld Exports text logs", ""]
    for audit in (target, donor):
        providers = audit["providers"]
        export_rows = sum(p["rows"] for p in providers.values())
        export_union = set().union(*(p["names"] for p in providers.values()))
        no_section = sorted(k for k, p in providers.items() if not p["has_section"])
        lines.extend([
            audit["build"],
            f"  Parent imports: {len(audit['imports'])} rows / {len(set(audit['imports']))} unique names",
            f"  Re-export provider logs: {len(providers)}",
            f"  Providers with export sections: {len(providers) - len(no_section)}",
            f"  Providers without an export section: {len(no_section)} ({', '.join(no_section)})" if no_section else "  Providers without an export section: 0",
            f"  Provider export rows: {export_rows}",
            f"  Union of unique provider export names: {len(export_union)}",
            f"  Unique imports matched in exactly one provider: {len(audit['matches'])}",
            f"  Unique imports matching multiple providers: {len(audit['ambiguous'])}",
            f"  Unique imports not found in one-level exports: {len(audit['missing'])}",
            "  Matched import names by provider:",
        ])
        counts = defaultdict(int)
        for provider in audit["matches"].values():
            counts[provider] += 1
        for provider, count in sorted(counts.items()):
            lines.append(f"    {provider}: {count}")
        if audit["ambiguous"]:
            lines.append("  Ambiguous names:")
            lines.extend(f"    {name}: {', '.join(hits)}" for name, hits in sorted(audit["ambiguous"].items()))
        if audit["missing"]:
            lines.append("  Unmatched names:")
            lines.extend(f"    {name}" for name in audit["missing"])
        lines.append("")
    target_names, donor_names = set(target["imports"]), set(donor["imports"])
    common = target_names & donor_names
    changed = [
        name for name in common
        if name in target["matches"] and name in donor["matches"]
        and target["matches"][name] != donor["matches"][name]
    ]
    lines.extend([
        "Cross-build comparison",
        f"  Common unique imported names: {len(common)}",
        f"  Target-only names: {len(target_names - donor_names)}",
        f"  Donor-only names: {len(donor_names - target_names)}",
        f"  Common names with different unique direct provider: {len(changed)}",
        "",
        "Interpretation limits:",
        "- A match is exact-name membership in one provider's saved direct export list.",
        "- This checks one level of the recorded LC_REEXPORT_DYLIB graph only.",
        "- It does not prove dyld fixups, runtime resolution, symbol versions, ABI, or implementation compatibility.",
        "- No cache, binary, device, firmware, partition, security, or boot state was modified.",
    ])
    return "\n".join(lines) + "\n"


def write_csv(target: dict, donor: dict, path: Path) -> None:
    target_names, donor_names = set(target["imports"]), set(donor["imports"])
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["symbol", "target_imported_from_libSystem",
                             "target_direct_reexport_provider",
                             "donor_imported_from_libSystem",
                             "donor_direct_reexport_provider"])
            for name in sorted(target_names | donor_names):
                t = target["matches"].get(name, "AMBIGUOUS" if name in target["ambiguous"] else "UNMATCHED")
                d = donor["matches"].get(name, "AMBIGUOUS" if name in donor["ambiguous"] else "UNMATCHED")
                writer.writerow([name, name in target_names, t, name in donor_names, d])
    except OSError as exc:
        raise ReexportAuditError(f"cannot write {path}: {exc}") from exc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare libSystem imports with saved one-level re-export provider exports."
    )
    parser.add_argument("--target-consumer", required=True, type=Path)
    parser.add_argument("--donor-consumer", required=True, type=Path)
    parser.add_argument("--target-provider-dir", required=True, type=Path)
    parser.add_argument("--donor-provider-dir", required=True, type=Path)
    parser.add_argument("--csv-output", type=Path)
    args = parser.parse_args(argv)
    try:
        target = audit_build("19H422", args.target_consumer, args.target_provider_dir)
        donor = audit_build("20H392", args.donor_consumer, args.donor_provider_dir)
        if args.csv_output:
            write_csv(target, donor, args.csv_output)
        sys.stdout.write(render_report(target, donor))
    except ReexportAuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.csv_output:
        print(f"CSV mapping: {args.csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
