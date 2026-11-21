# 19H422 / 20H392 AGX libSystem symbol-level re-export chain results

## Scope and source basis

This follow-up traces the symbol-level re-export records printed in the saved
Dyld Exports logs for the exact one-level LC_REEXPORT_DYLIB provider paths
already recorded in the preceding reports. It uses the uploaded AGX consumer
Symtab logs and the 65-provider text archive (33 target, 32 donor).

Target: iPhone 7 iPhone9,1 / D10AP / A10-T8010, iOS 15.8.8 build 19H422.
Donor: iPhone X iPhone10,3 / D22AP / A11-T8015, iOS 16.7.16 build 20H392.

The parser is the standalone ipsw revision and go-macho dependency already
pinned in the AGX export audit plan. Its Dyld Exports kind text distinguishes
ordinary export rows from symbol-level re-export rows. The chain checker reads
only the already-saved text logs and does not open cache or Mach-O binaries.

## Results

| Build | Parent libSystem imports | One-level name matches | Imports with a symbol-level re-export row | Traced to one terminal row | Unresolved chains |
|---|---:|---:|---:|---:|---:|
| 19H422 | 100 | 100 | 13 | 13 | 0 |
| 20H392 | 102 | 102 | 13 | 13 | 0 |

All 13 chains in each build terminate at exactly one printed regular export
row in a downstream provider log. No missing provider log, missing forwarded
symbol, ambiguous downstream row, cycle, or depth-limit result was observed.

The 13 parent-import names and forwarded export names are:

| AGX import name | First provider | Forwarded symbol | Terminal provider |
|---|---|---|---|
| ___chkstk_darwin | libcompiler_rt | ____chkstk_darwin | libsystem_pthread |
| _bzero | libsystem_c | __platform_bzero | libsystem_platform |
| _memchr | libsystem_c | __platform_memchr | libsystem_platform |
| _memcmp | libsystem_c | __platform_memcmp | libsystem_platform |
| _memcpy | libsystem_c | __platform_memmove | libsystem_platform |
| _memmove | libsystem_c | __platform_memmove | libsystem_platform |
| _memset | libsystem_c | __platform_memset | libsystem_platform |
| _memset_pattern16 | libsystem_c | __platform_memset_pattern16 | libsystem_platform |
| _memset_pattern4 | libsystem_c | __platform_memset_pattern4 | libsystem_platform |
| _memset_pattern8 | libsystem_c | __platform_memset_pattern8 | libsystem_platform |
| _strcmp | libsystem_c | __platform_strcmp | libsystem_platform |
| _strlen | libsystem_c | __platform_strlen | libsystem_platform |
| _strncmp | libsystem_c | __platform_strncmp | libsystem_platform |

The 13-symbol mapping is identical in the target and donor logs: zero common
names changed forwarded symbol, downstream provider, terminal symbol, or
terminal export-row kind. The checked-in CSV records all 26 build/name rows.

## How to interpret this result

This adds a symbol-level forwarding hop to the earlier one-level provider
name map. The first provider's export row does not always represent a local
implementation: for these 13 imported names, the parser's export-trie output
names a forwarded symbol and another dylib. The downstream log then contains
the forwarded name as a regular export row.

This is still static export-trie evidence. It does not prove that dyld applied
a fixup for any AGX import, that the target and donor functions have matching
implementations or ABI, that the AGX plugin loads, that the GPU initializes,
or that the operating system boots or reaches SpringBoard. Export-row
addresses are cache-specific and are not compared.

## Reproducibility

From the repository root, after extracting the consumer archive and the
libSystem re-export provider archive into separate directories, run:

    python3 tools/compare_dyld_reexport_chains.py \
      --target-consumer /path/to/consumer/19H422-AGXPlugin.txt \
      --donor-consumer /path/to/consumer/20H392-AGXPlugin.txt \
      --target-provider-dir /path/to/providers \
      --donor-provider-dir /path/to/providers \
      --csv-output research/agx-libsystem-reexport-chain-map.csv

The checker follows the parser's same-name and alias re-export kind strings,
requires exactly one matching forwarded export row at each hop, and reports
missing logs, missing sections, missing or ambiguous symbols, cycles, and
excessive depth as unresolved results. It does not infer success from an
empty or absent export section.

No device, firmware, partition, security, or boot state was accessed or
changed. The physical iPhone 7 remains on iOS 12.1.4.
