#!/usr/bin/env python3
"""Trace symbol-level dyld export-trie re-exports in saved ipsw text logs.

This helper reads saved Symtab and Dyld Exports text only. It does not open
caches or binaries, extract images, contact devices, or modify source files.
A terminal export record is not proof of runtime binding or ABI compatibility.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

try:
    from tools.compare_dyld_exports import ExportLogError, parse_export_log_text
    from tools.compare_dyld_imports import ImportLogError, parse_import_log_text
except ModuleNotFoundError:
    from compare_dyld_exports import ExportLogError, parse_export_log_text
    from compare_dyld_imports import ImportLogError, parse_import_log_text

PARENT = "libSystem.B.dylib"
NO_SECTION = "no 'Dyld Exports' section was printed"
ALIAS_REEXPORT = re.compile(r"^(.+?) re-exported from ([^\s]+)$")
SAME_NAME_REEXPORT = re.compile(r"^from ([^\s]+)$")


class ChainAuditError(ValueError):
    """Raised when saved parser output cannot be safely interpreted."""


@dataclass(frozen=True)
class Export:
    address: int
    kind: str
    name: str


@dataclass(frozen=True)
class Provider:
    rows: tuple[Export, ...]
    has_section: bool


@dataclass(frozen=True)
class Chain:
    symbol: str
    first_provider: str
    first_kind: str
    edges: tuple[tuple[str, str, str, str], ...]
    terminal_provider: str | None
    terminal_symbol: str | None
    terminal_kind: str | None
    status: str
    detail: str = ""


def parse_reexport(kind: str, exported_name: str) -> tuple[str, str] | None:
    """Decode the pinned go-macho textual form of a re-export row."""
    match = ALIAS_REEXPORT.fullmatch(kind.strip())
    if match:
        return match.group(1), match.group(2)
    match = SAME_NAME_REEXPORT.fullmatch(kind.strip())
    if match:
        return exported_name, match.group(1)
    return None


def provider_key(library: str) -> str:
    return Path(library).name.removesuffix(".dylib")


def load_providers(directory: Path, build: str) -> dict[str, Provider]:
    if not directory.is_dir():
        raise ChainAuditError(f"provider directory does not exist: {directory}")
    paths = sorted(directory.glob(f"{build}-*.txt"))
    if not paths:
        raise ChainAuditError(f"no {build}-*.txt provider logs found in {directory}")
    providers: dict[str, Provider] = {}
    for path in paths:
        key = path.stem[len(build) + 1:]
        if not key or key in providers:
            raise ChainAuditError(f"duplicate or empty provider key: {path}")
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            rows = parse_export_log_text(text, str(path))
            providers[key] = Provider(
                tuple(Export(row.address, row.kind, row.name) for row in rows), True
            )
        except ExportLogError as exc:
            if NO_SECTION in str(exc):
                providers[key] = Provider((), False)
            else:
                raise ChainAuditError(str(exc)) from exc
        except OSError as exc:
            raise ChainAuditError(f"cannot read {path}: {exc}") from exc
    return providers


def trace_chain(symbol: str, first_provider: str, first: Export,
                providers: dict[str, Provider], max_hops: int = 16) -> Chain:
    edges: list[tuple[str, str, str, str]] = []
    current_provider, current = first_provider, first
    first_kind = first.kind
    seen = {(current_provider, current.name)}
    for _ in range(max_hops):
        forwarding = parse_reexport(current.kind, current.name)
        if forwarding is None:
            return Chain(symbol, first_provider, first_kind, tuple(edges),
                         current_provider, current.name, current.kind,
                         "terminal-export-record")
        next_symbol, next_library = forwarding
        next_provider = provider_key(next_library)
        edges.append((current_provider, current.name, next_provider, next_symbol))
        provider = providers.get(next_provider)
        if provider is None:
            return Chain(symbol, first_provider, first_kind, tuple(edges),
                         None, next_symbol, None, "provider-log-missing", next_library)
        if not provider.has_section:
            return Chain(symbol, first_provider, first_kind, tuple(edges),
                         next_provider, next_symbol, None,
                         "provider-export-section-missing")
        matches = [row for row in provider.rows if row.name == next_symbol]
        if not matches:
            return Chain(symbol, first_provider, first_kind, tuple(edges),
                         next_provider, next_symbol, None, "forwarded-symbol-not-found")
        if len(matches) != 1:
            return Chain(symbol, first_provider, first_kind, tuple(edges),
                         next_provider, next_symbol, None, "forwarded-symbol-ambiguous",
                         f"{len(matches)} matching export rows")
        current_provider, current = next_provider, matches[0]
        marker = (current_provider, current.name)
        if marker in seen:
            return Chain(symbol, first_provider, first_kind, tuple(edges),
                         current_provider, current.name, current.kind, "cycle-detected")
        seen.add(marker)
    return Chain(symbol, first_provider, first_kind, tuple(edges),
                 current_provider, current.name, current.kind, "depth-limit-exceeded",
                 f"maximum symbol re-export depth is {max_hops}")


def audit_build(build: str, consumer: Path, provider_dir: Path) -> dict:
    try:
        imports = parse_import_log_text(
            consumer.read_text(encoding="utf-8", errors="replace"), str(consumer)
        )
    except (OSError, ImportLogError) as exc:
        raise ChainAuditError(str(exc)) from exc
    names = sorted({row.name for row in imports if row.provider == PARENT})
    if not names:
        raise ChainAuditError(f"{consumer}: no undefined imports from {PARENT}")
    providers = load_providers(provider_dir, build)
    rows_by_name: dict[str, list[tuple[str, Export]]] = defaultdict(list)
    all_reexports = 0
    for key, provider in providers.items():
        for row in provider.rows:
            rows_by_name[row.name].append((key, row))
            all_reexports += parse_reexport(row.kind, row.name) is not None

    matched, ambiguous, missing, chains = {}, {}, [], []
    for name in names:
        matches = rows_by_name.get(name, [])
        if not matches:
            missing.append(name)
        elif len(matches) > 1:
            ambiguous[name] = sorted(key for key, _ in matches)
        else:
            key, row = matches[0]
            matched[name] = key
            if parse_reexport(row.kind, row.name) is not None:
                chains.append(trace_chain(name, key, row, providers))
    return {
        "build": build, "names": names, "matched": matched, "ambiguous": ambiguous,
        "missing": missing, "all_reexports": all_reexports, "chains": chains,
    }


def render_report(target: dict, donor: dict) -> str:
    lines = ["Project Sweet-10: symbol-level re-export chain audit",
             "Evidence: saved ipsw Symtab and Dyld Exports text logs", ""]
    for audit in (target, donor):
        terminal = defaultdict(int)
        unresolved = defaultdict(int)
        for chain in audit["chains"]:
            if chain.status == "terminal-export-record":
                terminal[chain.terminal_kind or "(unknown)"] += 1
            else:
                unresolved[chain.status] += 1
        lines.extend([
            audit["build"],
            f"  Unique imports attributed to {PARENT}: {len(audit['names'])}",
            f"  Unique one-level provider-name matches: {len(audit['matched'])}",
            f"  Ambiguous one-level matches: {len(audit['ambiguous'])}",
            f"  Unmatched one-level names: {len(audit['missing'])}",
            f"  Symbol-level re-export rows in provider logs: {audit['all_reexports']}",
            f"  Imported names whose first provider row is a re-export: {len(audit['chains'])}",
            f"  Traced to a terminal export row: {sum(terminal.values())}",
            f"  Terminal export-row kinds: {dict(sorted(terminal.items())) or '(none)'}",
            f"  Unresolved chains: {dict(sorted(unresolved.items())) or '(none)'}",
            "  Chains:",
        ])
        for chain in sorted(audit["chains"], key=lambda item: item.symbol):
            route = [f"{chain.first_provider}:{chain.symbol}"]
            route.extend(f"{src}:{srcsym} -> {dst}:{dstsym}"
                         for src, srcsym, dst, dstsym in chain.edges)
            if chain.terminal_provider and chain.terminal_symbol:
                route.append(f"[{chain.terminal_kind}] {chain.terminal_provider}:{chain.terminal_symbol}")
            else:
                route.append(f"[{chain.status}] {chain.detail}")
            lines.append("    " + chain.symbol + ": " + " | ".join(route))
        lines.append("")
    t = {c.symbol: c for c in target["chains"]}
    d = {c.symbol: c for c in donor["chains"]}
    common = sorted(set(t) & set(d))
    changed = [n for n in common if
               (t[n].edges, t[n].terminal_provider, t[n].terminal_symbol,
                t[n].terminal_kind, t[n].status) !=
               (d[n].edges, d[n].terminal_provider, d[n].terminal_symbol,
                d[n].terminal_kind, d[n].status)]
    lines.extend([
        "Cross-build comparison",
        f"  Common imported names with re-export chains: {len(common)}",
        f"  Different chain/terminal assignments: {len(changed)}",
        "",
        "Interpretation limits:",
        "- Export-trie re-export rows describe forwarded names and libraries.",
        "- A terminal export row is static metadata, not proof of a dyld bind or implementation.",
        "- This audit does not establish symbol-version, ABI, runtime, GPU, boot, or SpringBoard compatibility.",
        "- Only saved text logs are read; no cache, binary, device, firmware, partition, or boot state is changed.",
    ])
    if changed:
        lines.append("  Changed assignments: " + ", ".join(changed))
    return "\n".join(lines) + "\n"


def write_csv(target: dict, donor: dict, path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["build", "imported_symbol", "first_provider",
                             "first_export_kind", "forwarded_symbol",
                             "forwarded_provider", "terminal_provider",
                             "terminal_symbol", "terminal_export_kind", "status",
                             "detail"])
            for audit in (target, donor):
                for chain in sorted(audit["chains"], key=lambda item: item.symbol):
                    edge = chain.edges[0] if chain.edges else None
                    writer.writerow([
                        audit["build"], chain.symbol, chain.first_provider,
                        chain.first_kind, edge[3] if edge else "",
                        edge[2] if edge else "", chain.terminal_provider or "",
                        chain.terminal_symbol or "", chain.terminal_kind or "",
                        chain.status, chain.detail,
                    ])
    except OSError as exc:
        raise ChainAuditError(f"cannot write {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace symbol-level re-export chains in saved ipsw logs.")
    parser.add_argument("--target-consumer", required=True, type=Path)
    parser.add_argument("--donor-consumer", required=True, type=Path)
    parser.add_argument("--target-provider-dir", required=True, type=Path)
    parser.add_argument("--donor-provider-dir", required=True, type=Path)
    parser.add_argument("--csv-output", type=Path)
    args = parser.parse_args()
    try:
        target = audit_build("19H422", args.target_consumer, args.target_provider_dir)
        donor = audit_build("20H392", args.donor_consumer, args.donor_provider_dir)
        if args.csv_output:
            write_csv(target, donor, args.csv_output)
        sys.stdout.write(render_report(target, donor))
    except ChainAuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.csv_output:
        print(f"CSV mapping: {args.csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
