# 19H422 / 20H392 AGX plugin import-provider audit: libSystem follow-up

## Scope and source archives

This report completes the direct export-name comparison for the 13 provider
labels shown in the AGXMetalA10/A11 saved Symtab import records, using:

- Earlier archive: `agx-metal-export-logs.tar.gz` (AGX consumer logs and
  Metal, IOGPU, IOKit, IOSurface provider logs).
- New archive: `agx-provider-export-logs.tar.gz` (the other nine provider
  logs and `query-status.tsv`).

Target is iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8 build
`19H422`. Donor is iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16
build `20H392`.

The new archive contains all 18 expected provider text logs, 18 stderr logs,
and one status table. All 18 queries exited with status 0. Each stderr file
contains only the expected `Parsing Cache` progress line and no parser error
diagnostic. This establishes successful command completion, not that every
provider has a broad public export list.

## Complete direct provider-name comparison

Each undefined import was compared by exact name to the parsed `Dyld Exports`
rows of the library printed in that import's `(from Provider)` field. Export
row counts below equal unique export-name counts; no duplicate export names
were printed in any of the 26 provider/build log files.

| Provider | Target imports | Target export rows | Target direct name matches | Donor imports | Donor export rows | Donor direct name matches |
|---|---:|---:|---:|---:|---:|---:|
| Metal | 102 | 960 | 102 | 126 | 1,063 | 126 |
| IOGPU | 74 | 248 | 74 | 73 | 281 | 73 |
| IOKit | 8 | 2,095 | 8 | 8 | 2,119 | 8 |
| IOSurface | 25 | 546 | 25 | 25 | 596 | 25 |
| AggregateDictionary | 1 | 62 | 1 | 0 | 15 | 0 |
| CoreAnalytics | 1 | 99 | 1 | 1 | 85 | 1 |
| Foundation | 9 | 1,482 | 9 | 9 | 11,036 | 9 |
| GPURawCounter | 4 | 35 | 4 | 4 | 35 | 4 |
| libMobileGestalt.dylib | 1 | 43 | 1 | 1 | 775 | 1 |
| libc++.1.dylib | 49 | 2,184 | 49 | 49 | 2,195 | 49 |
| CoreFoundation | 24 | 2,717 | 24 | 24 | 2,756 | 24 |
| libobjc.A.dylib | 20 | 333 | 20 | 42 | 398 | 42 |
| libSystem.B.dylib | 100 | 3 | 0 | 102 | 3 | 0 |
| **Total** | **418** | — | **318** | **464** | — | **362** |

The target import log has 418 undefined rows (414 normal and four weak);
the donor has 464 (460 normal and four weak). There are no repeated
(provider, symbol) pairs in the import rows.

For the first 12 provider labels in the table, all 318 target and 362 donor
imports have exact-name matches in the corresponding provider's saved export
list. The target has no import attributed to AggregateDictionary in the
donor (the target has one); no import rows are inferred from the presence of
that provider's export log.

## The libSystem.B.dylib discrepancy

Both libSystem export logs contain exactly the same three direct export names:

- `___crashreporter_info__`
- `_libSystem_init_after_boot_tasks_4launchd`
- `_mach_init_routine`

Neither direct export-name list contains the AGX plugin's imports attributed
to `libSystem.B.dylib`. That yields 100 target and 102 donor names not found
in the direct `libSystem.B.dylib` export rows.

This must **not** be called 100/102 missing runtime symbols. A Mach-O library
can re-export symbols from another library through `LC_REEXPORT_DYLIB`.
Apple's Mach-O header defines that load-command family, and Apple's dyld
source explicitly represents a linked dylib's `reExport` attribute. Those
sources establish the mechanism, not that these exact 19H422/20H392
`libSystem.B.dylib` images use it.

The new provider archive contains symbol/export text only; it does **not**
contain libSystem's own load-command JSON. The exact next check is therefore
to inspect `/usr/lib/libSystem.B.dylib` in both caches for
`LC_REEXPORT_DYLIB` commands, then compare the 100/102 imported names with
the direct exports of the specific libraries it re-exports.

References:
- [Apple XNU Mach-O load-command definitions](https://github.com/apple-oss-distributions/xnu/blob/main/EXTERNAL_HEADERS/mach-o/loader.h)
- [Apple dyld linked-dylib and re-export handling](https://github.com/apple-oss-distributions/dyld/blob/main/mach_o/UnsafeHeader.cpp)

## Read-only next collection step

The repository includes `tools/collect_libsystem_load_commands.sh`. On
Ubuntu, from the repository root, run:

```bash
bash tools/collect_libsystem_load_commands.sh
```

The script runs only these two host-side queries against the already-mounted
shared caches:

```bash
"$IPSW" dyld macho "$TARGET_CACHE" "/usr/lib/libSystem.B.dylib" --loads --json
"$IPSW" dyld macho "$DONOR_CACHE" "/usr/lib/libSystem.B.dylib" --loads --json
```

It saves the JSON, stderr, and exit status for both queries, then creates:

```text
$HOME/agx-metal-static-audit/libsystem-load-command-logs.tar.gz
```

It does not use `--extract`, execute an iOS binary, access the phone, or
modify either cache. Check that both statuses are zero and inspect both JSON
files for `LC_REEXPORT_DYLIB` entries before interpreting the symbols.

## Evidence boundary

Direct export-name membership is a static parser comparison only. It does
not establish dyld fixup locations, resolved bindings, symbol ABI/version
compatibility, code-signing acceptance, runtime dependency resolution, GPU
initialization, hardware support, boot, or SpringBoard.

The 100/102 libSystem imports remain unresolved by this direct-export pass.
They are not evidence of a compatibility failure. No device, firmware,
partition, security, boot, or iOS installation state was changed; the
physical iPhone 7 remains on iOS 12.1.4.
