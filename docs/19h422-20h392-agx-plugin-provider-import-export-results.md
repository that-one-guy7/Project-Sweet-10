# 19H422 / 20H392 AGX plugin provider import/export comparison

## Scope and evidence

This follow-up compares undefined import names printed in the saved AGX plugin
`AGXPlugin` Symtab logs against the Dyld Exports sections of four provider
logs from the same uploaded archive, `agx-metal-export-logs.tar.gz`.

- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, build `19H422`.
  The corresponding Mach-O load-command record identifies the consumer image
  as `AGXMetalA10`.
- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, build `20H392`.
  The corresponding Mach-O load-command record identifies the consumer image
  as `AGXMetalA11`.
- Consumer inputs: `19H422-AGXPlugin.txt` and `20H392-AGXPlugin.txt`.
- Provider inputs: the target/donor Metal, IOGPU, IOKit, and IOSurface logs.
- The eight corresponding provider query-status entries are all `0`.
  Their captured stderr files contain the informational `Parsing Cache`
  progress line; they are not empty, and the inspected text contains no error
  diagnostic.

The comparison reads only saved text output. It does not extract or execute a
Mach-O image, re-open a shared cache, or access the phone.

## Results for providers with saved export logs

All imported names attributed to these four providers occur in the matching
build's saved provider export-name set. There are no unmatched names in the
checked subsets.

| Provider | 19H422 import rows | 19H422 export rows | 19H422 exact matches | 20H392 import rows | 20H392 export rows | 20H392 exact matches |
|---|---:|---:|---:|---:|---:|---:|
| Metal | 102 | 960 | 102 | 126 | 1,063 | 126 |
| IOGPU | 74 | 248 | 74 | 73 | 281 | 73 |
| IOKit | 8 | 2,095 | 8 | 8 | 2,119 | 8 |
| IOSurface | 25 | 546 | 25 | 25 | 596 | 25 |
| **Total checked** | **209** | — | **209** | **232** | — | **232** |

For all eight provider logs, export-row count equals unique export-name count.
For the checked consumer rows, import-row count also equals the total of
provider-scoped unique import-name counts. Thus there are no repeated
(provider, symbol) pairs in these input rows.

- Target: 209 of 418 undefined imports were assessed; all 209 have exact
  provider-specific name matches in the target export logs.
- Donor: 232 of 464 undefined imports were assessed; all 232 have exact
  provider-specific name matches in the donor export logs.
- `not_in_saved_exports` is zero for each of the eight provider/build
  combinations.

## Providers still unassessed

The archive does not include provider export logs for the following labels.
Their imports are **unassessed**, not missing:

| Provider label | 19H422 import rows | 20H392 import rows |
|---|---:|---:|
| AggregateDictionary | 1 | 0 |
| CoreAnalytics | 1 | 1 |
| CoreFoundation | 24 | 24 |
| Foundation | 9 | 9 |
| GPURawCounter | 4 | 4 |
| libMobileGestalt.dylib | 1 | 1 |
| libSystem.B.dylib | 100 | 102 |
| libc++.1.dylib | 49 | 49 |
| libobjc.A.dylib | 20 | 42 |
| **Total unassessed** | **209** | **232** |

The plugin's load-command metadata lists 14 direct dylib dependencies. The
saved undefined-import rows use 13 distinct provider labels in the target and
12 in the donor; `libcompression.dylib` is a direct dependency but has no
undefined import row attributed to it in these two Symtab logs. The nine remaining images have the following exact install-name paths
from the paired AGXMetalA10/A11 load-command records:

| Provider label | Install-name path |
|---|---|
| AggregateDictionary | `/System/Library/PrivateFrameworks/AggregateDictionary.framework/AggregateDictionary` |
| CoreAnalytics | `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics` |
| CoreFoundation | `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation` |
| Foundation | `/System/Library/Frameworks/Foundation.framework/Foundation` |
| GPURawCounter | `/System/Library/PrivateFrameworks/GPURawCounter.framework/GPURawCounter` |
| libMobileGestalt.dylib | `/usr/lib/libMobileGestalt.dylib` |
| libSystem.B.dylib | `/usr/lib/libSystem.B.dylib` |
| libc++.1.dylib | `/usr/lib/libc++.1.dylib` |
| libobjc.A.dylib | `/usr/lib/libobjc.A.dylib` |

These names are the provider labels used in the saved Symtab output. The
collector writes output files using those same labels, so the logs can be
passed directly to `compare_dyld_imports.py`.

## Reproduction

After extracting the uploaded archive to a local directory, run from the
repository root:

```bash
LOG_DIR="/tmp/agx-metal-logs"
python3 tools/compare_dyld_imports.py \
  --target-consumer "$LOG_DIR/19H422-AGXPlugin.txt" \
  --donor-consumer "$LOG_DIR/20H392-AGXPlugin.txt" \
  --target-provider "Metal=$LOG_DIR/19H422-Metal.txt" \
  --target-provider "IOGPU=$LOG_DIR/19H422-IOGPU.txt" \
  --target-provider "IOKit=$LOG_DIR/19H422-IOKit.txt" \
  --target-provider "IOSurface=$LOG_DIR/19H422-IOSurface.txt" \
  --donor-provider "Metal=$LOG_DIR/20H392-Metal.txt" \
  --donor-provider "IOGPU=$LOG_DIR/20H392-IOGPU.txt" \
  --donor-provider "IOKit=$LOG_DIR/20H392-IOKit.txt" \
  --donor-provider "IOSurface=$LOG_DIR/20H392-IOSurface.txt"
```

To collect the nine remaining provider logs from the two already-mounted shared
caches on Ubuntu, run this from the repository root:

```bash
bash tools/collect_agx_provider_exports.sh
```

The collector runs 18 read-only `ipsw dyld macho ... --symbols -V` queries,
writes one text log and one stderr file per query plus a status table, and
creates:

```
$HOME/agx-metal-static-audit/agx-provider-export-logs.tar.gz
```

It does not use `--extract`, execute an iOS binary, access the phone, or alter
either shared cache. It exits nonzero if any provider query fails. Check the
status table and the matching `.err` files before treating the archive as
complete. Environment variables `IPSW`, `TARGET_CACHE`, `DONOR_CACHE`,
`OUT`, and `ARCHIVE` can override the documented defaults.

The comparison tool reuses the repository's `compare_dyld_exports.py`
parser for provider exports. Seven synthetic tests cover normal/weak import
parsing, malformed inputs, provider-map validation, matched names, missing
names, and the distinction between unassessed providers and missing exports.

## Interpretation limits

A printed `(from Provider)` label and an exact matching name in that
provider's saved export list are useful static metadata. They do **not**
prove a dyld bind was emitted, a fixup points to that export, the symbol's
ABI or version is compatible, code signing accepts the image, the loader
resolves the dependency at runtime, or the GPU starts. No bind locations
were present in the saved AGX plugin output used here.

The result does not establish GPU initialization, hardware support, boot, or
SpringBoard. It is not evidence that the donor AGXMetalA11 image can substitute
for the target AGXMetalA10 image.

No device, firmware, partition, security, boot, or iOS installation state was
changed. The physical iPhone 7 remains on iOS 12.1.4.
