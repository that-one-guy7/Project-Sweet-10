# 19H422 / 20H392 libSystem re-export load-command results

## Source and command status

This report records the uploaded `libsystem-load-command-logs.tar.gz` archive.
It contains the target and donor `ipsw dyld macho --loads --json` outputs,
both stderr files, and a status table.

| Build | Consumer | Query status | Mach-O | CPU | UUID | Current version | Minimum OS / SDK |
|---|---|---:|---|---|---|---|---|
| 19H422 target | iPhone9,1 / D10AP / A10-T8010 | 0 | 64-bit DYLIB | AARCH64 / ARM64 | EFE3ECA7-89AB-3B10-ADE7-C8527E93ED56 | 1311.120.1 | iOS 15.8 / 15.8 |
| 20H392 donor | iPhone10,3 / D22AP / A11-T8015 | 0 | 64-bit DYLIB | AARCH64 / ARM64 | 616FA041-BFAA-389C-8C6A-3DC585DAD933 | 1319.100.3 | iOS 16.7 / 16.7.3 |

Both stderr files are empty. The recorded image path is
`/usr/lib/libSystem.B.dylib` in each cache. These are host-side load-command
metadata queries; no Mach-O image was extracted or executed and no device
was accessed or changed.

## Confirmed re-export topology

Both images contain `LC_REEXPORT_DYLIB` commands:

| Field | 19H422 target | 20H392 donor |
|---|---:|---:|
| Total load commands | 46 | 46 |
| `LC_REEXPORT_DYLIB` count | **33** | **32** |
| Shared re-export install-name paths | **32** | **32** |
| Target-only re-export paths | **1** | **0** |
| Donor-only re-export paths | **0** | **0** |
| Shared paths with same current version | 8 | 8 |
| Shared paths with different current version | 24 | 24 |
| Compatibility version for all listed re-export commands | 1 | 1 |

The single target-only path is
`/usr/lib/system/libsystem_product_info_filter.dylib` (current version 10,
compatibility version 1). There are no donor-only re-export paths.

This confirms that the earlier three-row direct export list for
`libSystem.B.dylib` is not its entire public symbol surface: the load-command
metadata explicitly re-exports symbols from a further set of system
libraries. Therefore the 100 target / 102 donor AGX import names that did not
appear in the parent image's three direct export rows must not be called
missing based on that direct comparison alone.

## Shared re-export paths with differing current versions

The 24 common re-export paths below have different current-version strings
between 19H422 and 20H392. Their compatibility-version strings are all 1.

| Re-export image | 19H422 current version | 20H392 current version |
|---|---:|---:|
| libcache.dylib | 85 | 92 |
| libcommonCrypto.dylib | 60191.100.1 | 65535.100.4 |
| libcorecrypto.dylib | 1218.120.10 | 1387.140.3 |
| libdispatch.dylib | 1325.120.2 | 1415.140.2 |
| libmacho.dylib | 994.2 | 1005 |
| libremovefile.dylib | 60 | 68 |
| libsystem_asl.dylib | 392.100.2 | 395 |
| libsystem_blocks.dylib | 79.1 | 87 |
| libsystem_c.dylib | 1507.100.9 | 1534.100.14 |
| libsystem_collections.dylib | 1507.100.9 | 1534.100.14 |
| libsystem_configuration.dylib | 1163.140.3 | 1241.140.6 |
| libsystem_coreservices.dylib | 133 | 129 |
| libsystem_dnssd.dylib | 1557.140.4 | 1807.140.16 |
| libsystem_featureflags.dylib | 56 | 74 |
| libsystem_kernel.dylib | 8020.241.44 | 8796.142.1 |
| libsystem_m.dylib | 3204.80.2 | 3226.100.4 |
| libsystem_malloc.dylib | 374.120.1 | 425.100.7 |
| libsystem_notify.dylib | 301 | 312.140.2 |
| libsystem_platform.dylib | 273.100.5 | 292.120.1 |
| libsystem_pthread.dylib | 486.100.11 | 514.100.2 |
| libsystem_sandbox.dylib | 1657.241.1 | 1846.140.7 |
| libsystem_trace.dylib | 1375.140.2 | 1431.140.4 |
| libunwind.dylib | 202.2 | 1500.26 |
| libxpc.dylib | 2236.241.1 | 2462.140.4 |

The other eight common re-export entries print identical current versions:
libcompiler_rt (103.1), libcopyfile (1), libdyld (1),
libsystem_containermanager (1), libsystem_darwin (1), libsystem_info (1),
libsystem_networkextension (1), and libsystem_symptoms (1).

A current-version difference is a version metadata difference; it is not by
itself evidence of a missing symbol or incompatible ABI.

## Additional export-table metadata

| Field | 19H422 target | 20H392 donor |
|---|---:|---:|
| `LC_DYLD_EXPORTS_TRIE` payload size | 120 bytes | 112 bytes |
| `LC_SYMTAB.nsyms` | 77 | 79 |
| `LC_DYSYMTAB.nextdefsym` | 3 | 3 |
| `LC_DYSYMTAB.nundefsym` | 66 | 68 |

The saved `--symbols -V` logs show three direct export rows for each
`libSystem.B.dylib` image. Those direct exports were the same three names
for both builds; the re-export load commands establish the separate
forwarding topology.

## Next static comparison

The repository adds `tools/collect_libsystem_reexport_exports.sh` to collect
the export logs for the exact re-export paths in the uploaded metadata:
33 target cache queries and 32 donor cache queries. The script uses the
paths recorded above, runs `ipsw dyld macho ... --symbols -V` against the
already-mounted caches, saves one text/stderr pair per query plus a status
table, and creates:

```text
$HOME/agx-metal-static-audit/libsystem-reexport-export-logs.tar.gz
```

Run on Ubuntu from the Project-Sweet-10 repository root:

```bash
bash tools/collect_libsystem_reexport_exports.sh
```

The script does not use `--extract`, does not execute an iOS binary, and
does not communicate with the phone or modify the shared caches. Review the
query-status table and stderr files; all expected queries must have status
zero before using the archive.

That comparison is now complete. See [the provider-by-provider
symbol results](19h422-20h392-agx-libsystem-reexport-symbol-results.md):
all 100 target and 102 donor imports originally attributed to
`libSystem.B.dylib` occur in exactly one child provider's direct export
list. None was ambiguous or absent from the one-level re-export set.
The report includes the per-provider counts, cross-build name differences,
a checked-in CSV mapping, and a reproducible comparator.

## Interpretation limits

The `LC_REEXPORT_DYLIB` records confirm that the image declares re-export
dependencies. They do not, by themselves, prove that a given AGX import is
actually represented by an export in one of those providers, that the
dynamic loader resolves it at runtime, or that the two releases provide
matching symbol implementations and ABI.

This is static Mach-O metadata only. It does not establish dyld bind
locations, successful resolution, code-signing acceptance, GPU
initialization, hardware support, kernel boot, or SpringBoard.

No device, firmware, partition, security, boot, or iOS installation state
was changed. The physical iPhone 7 remains on iOS 12.1.4.
