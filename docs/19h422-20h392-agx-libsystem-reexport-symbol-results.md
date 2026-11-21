# 19H422 / 20H392 AGX libSystem re-exported import results

## Scope and inputs

This report records the follow-up comparison using:

- AGX consumer Symtab logs in `agx-metal-export-logs.tar.gz`.
- The 65 provider logs and status table in `libsystem-reexport-export-logs.tar.gz`.
- The `LC_REEXPORT_DYLIB` path inventory for `/usr/lib/libSystem.B.dylib`
  recorded in [the preceding load-command report](19h422-20h392-libsystem-reexport-load-command-results.md).

Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8 build
`19H422`. Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16
build `20H392`.

The provider archive contains 65 text logs: 33 target and 32 donor. All 65
query-status entries are zero. The stderr files contain the expected
`Parsing Cache` progress message. One target-only provider log,
`libsystem_product_info_filter`, contains no `Dyld Exports` heading; the
remaining 32 target logs and all 32 donor logs contain parsed export rows.
This no-heading result is recorded as an uninspected direct export list,
not treated as a command failure.

## Main result: the parent imports are all present in one direct re-export provider

The 100 target and 102 donor undefined import names whose original Symtab
provider label was `libSystem.B.dylib` were checked against the union of
direct `Dyld Exports` names from that build's exact one-level
`LC_REEXPORT_DYLIB` dependencies.

| Build | Parent import rows | Unique names | Exact match in exactly one child provider | Ambiguous across providers | Not found |
|---|---:|---:|---:|---:|---:|
| 19H422 target | 100 | 100 | **100** | 0 | 0 |
| 20H392 donor | 102 | 102 | **102** | 0 | 0 |

Every one of these imported names occurs in exactly one of the supplied
re-export dependency export lists. None is absent from the one-level export
set, and none is duplicated across multiple provider lists for these
particular imported names.

This resolves the direct-export gap from the earlier report. The original
consumer Symtab rows name `libSystem.B.dylib` as the provider, while that
parent library declares re-exports of the child libraries listed in its
load commands. For the imported names checked here, the exact name appears
in one child library's own saved export section.

## Provider-by-provider mapping

Counts below are unique AGX import names from the parent libSystem provider
that matched the named child library's direct export list.

| Re-export provider | 19H422 target | 20H392 donor |
|---|---:|---:|
| libcommonCrypto | 3 | 3 |
| libcompiler_rt | 1 | 1 |
| libdispatch | 27 | 27 |
| libdyld | 3 | 4 |
| libsystem_blocks | 6 | 6 |
| libsystem_c | 31 | 31 |
| libsystem_darwin | 0 | 1 |
| libsystem_kernel | 8 | 7 |
| libsystem_m | 0 | 1 |
| libsystem_malloc | 4 | 4 |
| libsystem_notify | 2 | 2 |
| libsystem_platform | 3 | 3 |
| libsystem_trace | 11 | 11 |
| libunwind | 1 | 1 |
| **Total** | **100** | **102** |

The 19H422 provider directory contains 33 records, including the target-only
provider without a Dyld Exports heading. The 20H392 provider directory
contains the 32 common re-export providers. There were no repeated symbol
names within an individual provider's parsed export section. The aggregate
target provider logs contain 7,739 export rows and a union of 7,653 unique
export names; the aggregate donor provider logs contain 7,942 rows and
7,942 unique names. Although provider export lists can overlap in general,
none of the imported names in this comparison is ambiguous.

## Cross-build differences

The target and donor import-name sets have 96 common names, four target-only
names, and six donor-only names. All 96 common names map to the same direct
re-export provider in both builds.

Target-only names in this libSystem-attributed import subset:

| Symbol | 19H422 direct provider |
|---|---|
| `___error` | libsystem_kernel |
| `__os_crash_fmt` | libsystem_c |
| `__os_log_pack_fill` | libsystem_trace |
| `__os_log_pack_size` | libsystem_trace |

Donor-only names in this libSystem-attributed import subset:

| Symbol | 20H392 direct provider |
|---|---|
| `__os_crash_msg` | libsystem_c |
| `__os_log_fault_impl` | libsystem_trace |
| `__os_log_send_and_compose_impl` | libsystem_trace |
| `_dyld_program_sdk_at_least` | libdyld |
| `_os_parse_boot_arg_int` | libsystem_darwin |
| `_powf` | libsystem_m |

These are differences in the AGX plugin's recorded undefined-import names
between the two build-specific Symtab logs. They do not by themselves prove
a missing API, source-level feature, or runtime incompatibility.

## Combined AGX import coverage

The earlier direct-provider comparison covered the other 12 Symtab provider
labels: 318/418 target rows and 362/464 donor rows matched the direct export
lists of those named providers. This follow-up maps the remaining parent
`libSystem.B.dylib` subset: 100/100 target and 102/102 donor rows match
exactly one direct export list among the parent's recorded re-export
dependencies.

Therefore, across the saved provider logs collected so far, all **418/418
target** and **464/464 donor** undefined-import rows have an exact
provider-specific export-name match, once the parent `libSystem` imports are
expanded one level through their `LC_REEXPORT_DYLIB` entries.

This is stronger static name-coverage evidence than the initial direct
`libSystem.B.dylib` three-row export check, but it is still not evidence
that dyld successfully emitted or applied a bind at runtime.

## Reproducibility

The repository adds `tools/compare_dyld_reexports.py`. After extracting
both user-provided archives on Ubuntu from the repository root:

```bash
AUDIT="$HOME/agx-metal-static-audit"
mkdir -p "$AUDIT/consumer-logs" "$AUDIT/reexport-logs"
tar -xzf "$HOME/agx-metal-export-logs.tar.gz" -C "$AUDIT/consumer-logs"
tar -xzf "$HOME/agx-metal-static-audit/libsystem-reexport-export-logs.tar.gz" -C "$AUDIT/reexport-logs"

python3 tools/compare_dyld_reexports.py \
  --target-consumer "$AUDIT/consumer-logs/19H422-AGXPlugin.txt" \
  --donor-consumer "$AUDIT/consumer-logs/20H392-AGXPlugin.txt" \
  --target-provider-dir "$AUDIT/reexport-logs" \
  --donor-provider-dir "$AUDIT/reexport-logs" \
  --csv-output "$AUDIT/agx-libsystem-reexport-symbol-map.csv"
```

The checked-in [symbol mapping CSV](../research/agx-libsystem-reexport-symbol-map.csv)
contains one row per unique imported name across both builds (106 rows),
with the target and donor direct-provider assignment recorded separately.
The script reports missing or ambiguous names instead of silently assigning
them. It treats a provider log with no Dyld Exports heading as an empty
export-list observation, while an explicitly printed but empty export
section is considered a malformed/incomplete parser result.

Seven synthetic tests cover unique matches, ambiguous matches, unmatched
names, a provider with no export heading, malformed empty sections,
consumer-provider filtering, and cross-build stability. CI runs the unit
tests and the comparator's `--help` check.

## Interpretation limits

The result is an exact symbol-name comparison against the direct export
sections of one level of the recorded re-export graph. It does **not** prove:

- a dyld bind/fixup location or a successful runtime symbol resolution;
- matching symbol versions, calling conventions, ABI, or implementations;
- that the AGX plugins load, initialize the GPU, or work on the target board;
- kernel boot, SpringBoard launch, or overall iOS 16 compatibility.

The saved consumer output has no Dyld Binds section. The static import and
export evidence does not replace runtime validation. No Mach-O image was
extracted or executed, and no device, firmware, partition, security, or boot
state was modified. The physical iPhone 7 remains on iOS 12.1.4.
