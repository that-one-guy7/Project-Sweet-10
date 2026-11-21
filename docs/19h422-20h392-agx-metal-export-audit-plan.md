# iPhone9,1 19H422 / iPhone10,3 20H392 AGX and Metal export audit plan

The AGXMetalA10 / AGXMetalA11 load-command follow-up has been completed. See [the recorded load-command and import results](19h422-20h392-agx-plugin-load-command-results.md); the command block below is retained as a reproducible read-only procedure.

## Purpose and evidence boundary

This plan defines the next bounded, read-only comparison after the graphics
PrebuiltLoader work:

- Target reference: iPhone 7 `iPhone9,1` / D10AP / A10-T8010,
  iOS 15.8.8 build `19H422`.
- Donor reference: iPhone X `iPhone10,3` / D22AP / A11-T8015,
  iOS 16.7.16 build `20H392`.
- Physical iPhone 7: remains on iOS 12.1.4.

The procedure reads the existing dyld shared caches on the Ubuntu host and
saves parser text output. It does not extract a Mach-O image, run an iOS
binary, load a KEXT, connect to the phone, or change firmware, partitions,
security state, or boot state. The helper in
`tools/compare_dyld_exports.py` reads only the saved text logs.

This work asks whether selected target and donor images expose the same
printed export names and kinds. It does not claim that matching export names
have matching implementations or ABI.

## Why this is the next step

The previous M5 graphics investigation recorded:

- Target `AGXG9P` / `gpu,t8010` metadata and its
  `AGXMetalA10` plugin image.
- Donor `AGXG10P` / `gpu,t8015` metadata and its
  `AGXMetalA11` plugin image.
- Eleven paired graphics loader records, including the generation-specific
  A10/A11 plugin pair.
- Four donor-only typed dependency edges in the donor Metal/CoreGraphics
  parent records. The corresponding dependency images were then confirmed
  present in both caches.

Loader dependency names are not a substitute for exported-symbol metadata.
The next narrow comparison therefore inspects the `Dyld Exports` section
for the exact cached images already identified in the two full image lists.

## Parser behavior and pin

The repository's recorded standalone `ipsw` version is 3.1.749, build
commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`.

At that pinned `ipsw` source revision:

- Command form: `ipsw dyld macho <DSC> <DYLIB>`.
- `--symbols` requests symbol output.
- Global `-V` enables verbose output.
- The command prints `Dyld Exports` when the cached Mach-O has a non-empty
  `LC_DYLD_EXPORTS_TRIE` and verbose mode is enabled.
- It calls `m.DyldExports()` and prints each parsed export entry.
- Do not pass `--extract`; this audit needs only parser output.

The pinned `go-macho` dependency is v1.1.296. Its `TrieExport.String()`
method prints an address, the parser's type/re-export description in
parentheses, and the symbol name. The comparison helper preserves that
parenthesized text verbatim as the row's kind field.

References:
- [Pinned ipsw dyld Mach-O parser](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/dyld/dyld_macho.go)
- [Pinned go-macho export-row formatter](https://github.com/blacktop/go-macho/blob/v1.1.296/pkg/trie/trie.go)
- [ipsw dyld shared-cache guide](https://blacktop.github.io/ipsw/docs/guides/dyld/)

## Image pairs

All paths below were already observed in the target/donor image inventories
and the preceding PrebuiltLoader queries. Query the target cache and donor
cache independently. The AGX plugin pair intentionally uses two different
install paths.

| Key | Target 19H422 image | Donor 20H392 image |
|---|---|---|
| Metal | `/System/Library/Frameworks/Metal.framework/Metal` | Same install path |
| CoreGraphics | `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics` | Same install path |
| IOSurface | `/System/Library/Frameworks/IOSurface.framework/IOSurface` | Same install path |
| IOMobileFramebuffer | `/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer` | Same install path |
| IOGPU | `/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU` | Same install path |
| IOKit | `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit` | Same install path |
| IOAccelerator | `/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator` | Same install path |
| AGXCompilerCore | `/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore` | Same install path |
| MetalKit | `/System/Library/Frameworks/MetalKit.framework/MetalKit` | Same install path |
| AGXPlugin | `/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10` | `/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11` |
| AppleMetalGLRenderer | `/System/Library/Extensions/AppleMetalGLRenderer.bundle/AppleMetalGLRenderer` | Same install path |

If any command reports that an image is not in its cache, preserve the
error and status. Do not replace the path with a guessed image name.

## Ubuntu command

Run this from the repository root after confirming the two already-mounted
cache paths are readable:

```bash
IPSW="$HOME/ipsw-standalone/ipsw"
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
DONOR_CACHE="$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/agx-metal-static-audit/export-symbols"
REPO_ROOT="$(git rev-parse --show-toplevel)"
COMPARATOR="$REPO_ROOT/tools/compare_dyld_exports.py"

mkdir -p "$OUT"
test -x "$IPSW" || { echo "Standalone ipsw executable not found"; exit 1; }
test -f "$COMPARATOR" || { echo "Project comparator not found: $COMPARATOR"; exit 1; }
test -r "$TARGET_CACHE" || { echo "Target cache is not readable"; exit 1; }
test -r "$DONOR_CACHE" || { echo "Donor cache is not readable"; exit 1; }

run_one() {
  LABEL="$1"
  CACHE="$2"
  KEY="$3"
  IMAGE="$4"
  LOG="$OUT/$LABEL-$KEY.txt"
  ERR="$OUT/$LABEL-$KEY.err"

  if "$IPSW" dyld macho "$CACHE" "$IMAGE" --symbols -V > "$LOG" 2> "$ERR"; then
    STATUS=0
  else
    STATUS=$?
  fi
  printf '%s\t%s\t%s\n' "$LABEL" "$KEY" "$STATUS" >> "$OUT/query-status.tsv"
}

: > "$OUT/query-status.tsv"

while IFS='|' read -r KEY TARGET_IMAGE DONOR_IMAGE; do
  [ -n "$KEY" ] || continue
  run_one 19H422 "$TARGET_CACHE" "$KEY" "$TARGET_IMAGE"
  run_one 20H392 "$DONOR_CACHE" "$KEY" "$DONOR_IMAGE"
done <<'PAIRS'
Metal|/System/Library/Frameworks/Metal.framework/Metal|/System/Library/Frameworks/Metal.framework/Metal
CoreGraphics|/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics|/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics
IOSurface|/System/Library/Frameworks/IOSurface.framework/IOSurface|/System/Library/Frameworks/IOSurface.framework/IOSurface
IOMobileFramebuffer|/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer|/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer
IOGPU|/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU|/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU
IOKit|/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit|/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit
IOAccelerator|/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator|/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator
AGXCompilerCore|/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore|/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore
MetalKit|/System/Library/Frameworks/MetalKit.framework/MetalKit|/System/Library/Frameworks/MetalKit.framework/MetalKit
AGXPlugin|/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10|/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11
AppleMetalGLRenderer|/System/Library/Extensions/AppleMetalGLRenderer.bundle/AppleMetalGLRenderer|/System/Library/Extensions/AppleMetalGLRenderer.bundle/AppleMetalGLRenderer
PAIRS

echo "=== parser query status ==="
cat "$OUT/query-status.tsv"

for KEY in Metal CoreGraphics IOSurface IOMobileFramebuffer IOGPU IOKit IOAccelerator AGXCompilerCore MetalKit AGXPlugin AppleMetalGLRenderer; do
  if python3 "$COMPARATOR" \
      --target "$OUT/19H422-$KEY.txt" \
      --donor "$OUT/20H392-$KEY.txt" \
      > "$OUT/$KEY-comparison.txt" 2> "$OUT/$KEY-comparison.err"; then
    echo "Compared $KEY"
  else
    echo "No comparison report for $KEY; inspect both logs and the comparison error."
  fi
done

tar -czf "$HOME/agx-metal-export-logs.tar.gz" -C "$OUT" .
ls -lh "$HOME/agx-metal-export-logs.tar.gz"
```

The command writes text logs, stderr, and query statuses only. The final
archive is saved outside the output directory so it does not include itself.
No shared-cache file or device is modified.

### AGX plugin load-command follow-up

The first export-log archive showed no `Dyld Exports` heading for the target
AGXMetalA10 plugin and an empty `Dyld Exports` section for donor AGXMetalA11.
To distinguish load-command presence from parser export-row output, run this
additional read-only host-side query. It prints parsed Mach-O load-command
metadata as JSON; it does not extract either image:

```bash
TARGET_AGX="/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10"
DONOR_AGX="/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11"

set +e
"$IPSW" dyld macho "$TARGET_CACHE" "$TARGET_AGX" --loads --json \
  > "$OUT/19H422-AGXMetalA10-loads.json" \
  2> "$OUT/19H422-AGXMetalA10-loads.err"
printf '19H422 AGXMetalA10 load-command exit status: %s\n' "$?" \
  > "$OUT/19H422-AGXMetalA10-loads.status"

"$IPSW" dyld macho "$DONOR_CACHE" "$DONOR_AGX" --loads --json \
  > "$OUT/20H392-AGXMetalA11-loads.json" \
  2> "$OUT/20H392-AGXMetalA11-loads.err"
printf '20H392 AGXMetalA11 load-command exit status: %s\n' "$?" \
  > "$OUT/20H392-AGXMetalA11-loads.status"
set -e
```

Record whether `LC_DYLD_EXPORTS_TRIE` or legacy export-related load-command
metadata is present, including the parser-reported data offset and size. Do
not infer an empty export set from a missing field, and do not interpret a
present load command as proof of usable symbols or runtime compatibility.
Preserve the JSON and status/stderr text with the follow-up archive.

## Local comparison tool

After the parser logs have been generated, the helper can also be run for a
single pair:

```bash
python3 tools/compare_dyld_exports.py \
  --target "$HOME/agx-metal-static-audit/export-symbols/19H422-Metal.txt" \
  --donor "$HOME/agx-metal-static-audit/export-symbols/20H392-Metal.txt"
```

The tool reports:

- Parser row counts and unique export-name counts.
- Duplicate symbol names, with repeated rows preserved.
- Target-only and donor-only names.
- Common names whose parser-printed kind multisets differ.
- Common names whose first printed addresses differ.

A missing `Dyld Exports` section or a section with no parsed rows is a
non-zero parser/evidence error. It is not silently converted into an empty
export set. Query exit statuses must also be reviewed separately.

## Interpretation rules

1. Export names are names, not implementations. A shared name does not prove
   matching code, calling convention, structure layout, or ownership rules.
2. Preserve the parser's kind text, including re-export descriptions. Do not
   reduce every entry to a generic "symbol exists" result.
3. Addresses are cache-local metadata. Target and donor address differences
   are expected across separately built caches and are not a compatibility
   score.
4. An absent export section is not proof that an image exports no public
   symbols; it may reflect parser support or the image's load-command format.
5. Export overlap does not prove private API/KPI compatibility, dependency
   resolution, code-signing acceptance, IOKit attachment, GPU initialization,
   or rendering.
6. The target and donor are different iOS releases and different SoCs.
   Any static differences must not be attributed to hardware alone.
7. Do not substitute donor binaries or libraries into the target environment.

## Expected handoff

Upload `agx-metal-export-logs.tar.gz` from the Ubuntu host. The archive should
contain only text logs, stderr files, comparison summaries, and
`query-status.tsv`; it must not contain firmware images, cache binaries,
device identifiers, or personal backups.

The next report will compare the observed target/donor export names and kinds
for each pair and retain parser failures as unresolved evidence. M5 graphics
research remains static. M6 userland research remains in progress. M7 /
SpringBoard has not started.
