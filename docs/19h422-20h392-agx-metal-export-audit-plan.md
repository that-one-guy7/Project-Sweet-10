# 19H422 target / 20H392 donor AGX and Metal Mach-O export audit plan

## Scope and image identity

This is a bounded, read-only host-side comparison of the dyld export-trie
metadata for five GPU-related image pairs already confirmed in the target
and donor shared-cache inventories and PrebuiltLoader queries.

- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8 build
  `19H422`.
- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16 build
  `20H392`.
- The physical iPhone 7 remains on iOS 12.1.4.

| Pair | Target 19H422 image | Donor 20H392 image |
|---|---|---|
| AGX plugin | `/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10` | `/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11` |
| Metal | `/System/Library/Frameworks/Metal.framework/Metal` | Same install path |
| IOGPU | `/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU` | Same install path |
| IOAccelerator | `/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator` | Same install path |
| AGXCompilerCore | `/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore` | Same install path |

These exact paths come from the existing 19H422/20H392 image-inventory and
PrebuiltLoader reports. The AGX plugin pair is generation-specific: the A11
image is not a replacement for the A10 image.

## Parser and field semantics

The pinned standalone `ipsw` parser is version `3.1.749`, source commit
`a7dfadbcaca8375b424c12a68dae40767e5e07c1`.

The selected command is:

```bash
ipsw dyld macho <dyld_shared_cache> <exact-image-install-path> --symbols -V
```

At the pinned source revision, `--symbols` enters the symbol-report path;
when verbose mode is enabled and the Mach-O has a non-empty
`LC_DYLD_EXPORTS_TRIE`, the command prints a `Dyld Exports` section from
the parsed export trie. The command also emits other symbol-table and bind
information; the collection script below isolates only the export section.
It does not use `--extract` and does not write an extracted Mach-O file.

Pinned implementation references:

- [dyld_macho.go at the pinned commit](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/dyld/dyld_macho.go)
- [ipsw dyld shared-cache guide](https://blacktop.github.io/ipsw/docs/guides/dyld/)
- [Apple dyld shared-cache format definitions](https://github.com/apple-oss-distributions/dyld/blob/main/include/mach-o/dyld_cache_format.h)

The export comparator compares exact exported names and their printed
export kinds (for example regular, weak definition, or re-export). It
preserves duplicate rows. It intentionally excludes addresses because the
target and donor caches have different layouts and load addresses.

A missing `Dyld Exports` heading or an unparseable section is a collection
or parser result to investigate. It must not be converted into a claim that
the image exports no symbols.

## Existing read-only cache paths

The recorded host cache paths are:

- Target:
  `$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`
- Donor:
  `$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`

The companion subcache files must remain beside their respective main
cache files. Do not mix target and donor cache components.

## Exact host-side collection command

Run from the Project-Sweet-10 repository root after this plan and
`tools/compare_dyld_exports.py` are available locally. The script reads
only the two already-mounted shared caches on the host.

```bash
set -euo pipefail

BIN="$HOME/ipsw-standalone/ipsw"
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
DONOR_CACHE="$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/agx-metal-static-audit/export-audit"

if [ ! -x "$BIN" ]; then
  echo "Standalone ipsw executable is missing or not executable: $BIN" >&2
  exit 1
fi
if [ ! -r "$TARGET_CACHE" ] || [ ! -r "$DONOR_CACHE" ]; then
  echo "One or both existing shared-cache files are not readable." >&2
  exit 1
fi

mkdir -p "$OUT/raw" "$OUT/exports" "$OUT/errors" "$OUT/comparisons"
: > "$OUT/status.tsv"
printf 'build\timage_key\texit_status\texport_section\texport_rows\n' > "$OUT/status.tsv"

run_query() {
  LABEL="$1"
  CACHE="$2"
  KEY="$3"
  IMAGE="$4"
  RAW="$OUT/raw/$LABEL-$KEY.full.log"
  EXPORTS="$OUT/exports/$LABEL-$KEY.exports.txt"
  ERROR="$OUT/errors/$LABEL-$KEY.err"

  set +e
  "$BIN" dyld macho "$CACHE" "$IMAGE" --symbols -V > "$RAW" 2> "$ERROR"
  STATUS=$?
  set -e

  HAS_SECTION="no"
  ROWS=0
  if grep -q '^Dyld Exports$' "$RAW"; then
    HAS_SECTION="yes"
    awk '
      /^Dyld Exports$/ { inside=1; print; next }
      inside {
        print
        if ($0 ~ /^[[:space:]]*0x[[:xdigit:]]+:/) saw_row=1
        if (saw_row && NF==0) exit
      }
    ' "$RAW" > "$EXPORTS"
    ROWS="$(grep -cE '^[[:space:]]*0x[[:xdigit:]]+:' "$EXPORTS" || true)"
  else
    printf 'No Dyld Exports heading was printed.\n' > "$EXPORTS"
  fi

  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$LABEL" "$KEY" "$STATUS" "$HAS_SECTION" "$ROWS" >> "$OUT/status.tsv"
}

# AGX plugin: exact generation-specific counterpart paths.
run_query 19H422 "$TARGET_CACHE" AGXMetalPlugin \
  "/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10"
run_query 20H392 "$DONOR_CACHE" AGXMetalPlugin \
  "/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11"

# Same-install-path framework pairs.
run_query 19H422 "$TARGET_CACHE" Metal \
  "/System/Library/Frameworks/Metal.framework/Metal"
run_query 20H392 "$DONOR_CACHE" Metal \
  "/System/Library/Frameworks/Metal.framework/Metal"
run_query 19H422 "$TARGET_CACHE" IOGPU \
  "/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU"
run_query 20H392 "$DONOR_CACHE" IOGPU \
  "/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU"
run_query 19H422 "$TARGET_CACHE" IOAccelerator \
  "/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator"
run_query 20H392 "$DONOR_CACHE" IOAccelerator \
  "/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator"
run_query 19H422 "$TARGET_CACHE" AGXCompilerCore \
  "/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore"
run_query 20H392 "$DONOR_CACHE" AGXCompilerCore \
  "/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore"

echo "=== query status ==="
cat "$OUT/status.tsv"

compare_pair() {
  KEY="$1"
  LABEL="$2"
  set +e
  python3 tools/compare_dyld_exports.py \
    --target "$OUT/exports/19H422-$KEY.exports.txt" \
    --donor "$OUT/exports/20H392-$KEY.exports.txt" \
    --pair "$LABEL" \
    > "$OUT/comparisons/$KEY.txt" \
    2> "$OUT/comparisons/$KEY.err"
  STATUS=$?
  set -e
  printf '%s\t%s\n' "$KEY" "$STATUS" >> "$OUT/comparison-status.tsv"
}

: > "$OUT/comparison-status.tsv"
compare_pair AGXMetalPlugin "AGXMetalA10 versus AGXMetalA11"
compare_pair Metal "Metal"
compare_pair IOGPU "IOGPU"
compare_pair IOAccelerator "IOAccelerator"
compare_pair AGXCompilerCore "AGXCompilerCore"

echo "=== comparison status ==="
cat "$OUT/comparison-status.tsv"

tar -czf "$OUT/agx-metal-export-audit.tar.gz" \
  -C "$OUT" status.tsv comparison-status.tsv exports errors comparisons
ls -lh "$OUT/agx-metal-export-audit.tar.gz"
```

The full logs are retained under `raw/` for local troubleshooting but are
not included in the archive. The archive includes the extracted text
sections, statuses, errors, and comparison summaries only. Do not upload
shared-cache binaries or firmware images.

Before interpreting results, check that each of the ten query statuses is
zero and each row says `export_section=yes`. A parser error, absent image,
missing section, or failed comparator must remain unresolved rather than
being treated as an empty export set.

## Result fields to record

For each of the five pairs, record:

1. Query exit status and whether a `Dyld Exports` section was printed.
2. Parsed export-row count and unique exported-name count on each side.
3. Target-only and donor-only exported names.
4. Names whose printed export-kind sets differ.
5. Duplicate names and duplicate typed rows.
6. Parser errors and unresolved re-export references, if present.

Keep the image-list version and UUID from the separate cache inventory
report; the `Dyld Exports` section itself is not a replacement for those
identity fields.

## Interpretation limits

An overlapping exported-name set is only an interface-surface clue. It
does not establish matching function implementations, calling conventions,
structure layouts, private ABI/KPI compatibility, code-signing validity,
runtime dependency resolution, successful plugin loading, IOKit attachment,
GPU initialization, Metal rendering, kernel boot, or SpringBoard.

Likewise, a donor-only export does not by itself establish that the target
lacks the relevant behavior or that the difference causes a failure. The
two records come from different iOS releases and different SoC generations.
Do not substitute donor binaries or libraries into the target.

No device, firmware, partition, security, or boot state is accessed or
changed by this plan. M6 remains in progress; M7/SpringBoard has not
started. The physical iPhone 7 remains on iOS 12.1.4.
