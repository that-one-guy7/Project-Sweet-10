# iPhone9,1 19H422 target MultitouchHID loader audit plan

## Objective

Inspect the target-native 19H422 dyld image/loader record for:

```text
/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID
```

The purpose is to determine what target-side static dependency and loader
metadata is available for comparison with the already recorded 20H392 donor
PrebuiltLoaderSet record. This is a host-side inspection of the read-only
mounted IPSW filesystem. The physical iPhone 7 remains on iOS 12.1.4.

## Verified input paths

The target main cache path recorded from the user's read-only mount is:

```text
$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

The cache directory also contains numbered subcache files. Keep all of the
original cache files together; do not rename or move them for this query.

## Read-only command

Run the following from the existing Ubuntu terminal:

```bash
BIN="$(find "$HOME/ipsw-standalone" -type f -name ipsw -executable -print -quit)"

TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
IMAGE="/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID"
OUTPUT="$HOME/19H422-MultitouchHID-loader.txt"

echo "===== TARGET 19H422 MULTITOUCHHID LOADER RECORD ====="

if [ -z "$BIN" ]; then
    echo "Could not locate the standalone ipsw executable."
elif [ ! -f "$TARGET_CACHE" ]; then
    echo "Target shared cache not found: $TARGET_CACHE"
else
    "$BIN" dyld image "$TARGET_CACHE" "$IMAGE" > "$OUTPUT" 2>&1
    IPSW_STATUS=$?

    echo "ipsw exit code: $IPSW_STATUS"
    echo
    echo "===== CAPTURED TARGET RECORD ====="
    sed -n '1,180p' "$OUTPUT"
    echo
    echo "Saved report: $OUTPUT"
fi

read -r -p "Press Enter to close..."
```

The command intentionally omits `-V`. The first useful comparison is the
dependency list, image UUID, CDHash metadata (if present), flags, and mapping
information; detailed initializer/terminator offsets are not needed.

## Expected output paths

Pinned ipsw 3.1.749 source shows that `ipsw dyld image <cache> <image>`
first tries the PrebuiltLoaderSet path:

- If the target cache supports a dylib PrebuiltLoaderSet, ipsw prints that
  loader record, including loader metadata and dependency rows.
- If the cache reports that PrebuiltLoaderSets are unsupported, ipsw parses
  the older image arrays and prints the matching image-array record. That
  record can include the image name, flags, UUID, CDHash, code-signature
  location, mappings, dependents, and initialization order.

These are two different metadata formats. Do not equate their indexes or
field semantics without independent evidence. The command is expected to
capture whichever record is valid for the actual 19H422 cache.

## Comparison checklist

When the output is available, record only fields actually emitted:

1. Exact image path and image identity (UUID/version where reported).
2. Loader/image flags and image mapping/region information.
3. Dependency path names and edge kinds (regular, weak-link, re-export,
   or other labels exactly as printed).
4. Any CDHash or signature-location fields, without describing them as
   cryptographic signature validation.
5. Parser warnings and exit status.

Compare target dependency names to the 20H392 donor list, but keep the
edge model explicit: donor PrebuiltLoaderSet dependencies and any target
legacy closure dependents may encode relationships differently. A matching
name is not proof of the same provider, version, or runtime resolution.

## Evidence boundaries

This query does not load the plugin, execute it, modify firmware, or access
the physical phone. A dependency list is static loader metadata, not proof
that all providers exist at runtime, that IOKit attaches, or that touch
events reach SpringBoard. The donor is iPhone10,3 / A11-T8015; the target
is iPhone9,1 / A10-T8010.

No donor binaries are to be copied to the target. No device, partition,
activation, security, boot, or restore operation is part of this audit.

## Pinned parser source

The following ipsw 3.1.749 files were reviewed to choose this query and
interpret its possible output paths:

- [dyld image command](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/dyld/dyld_image.go)
- [PrebuiltLoaderSet parser](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/dyld/prebuilt.go)
- [legacy cache-image record formatter](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/dyld/closure.go)
