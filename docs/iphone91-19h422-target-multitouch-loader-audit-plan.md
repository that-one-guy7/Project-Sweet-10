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


## Observed target result (user-supplied)

The user ran the documented command against the read-only 19H422 target
cache. It exited with status `0` and returned a PrebuiltLoaderSet record
for the exact image path. The record is captured in
[the target/donor loader comparison](20h392-19h422-multitouch-loader-comparison.md).

Important target-side values:

- VM Size: `0x2e9f4000`.
- Loader flags: `prebuilt|in-cache-dylib|objc|never-unload`.
- Loader reference: `index: 1947` (not the image-list index `1948`).
- Info flags: `initializers|regions=5`.
- Exports trie: offset `0x025fee90`, size `0xf0d0`.
- Five regions with `r-x`, `rw-`, and `r--` permissions.
- Thirteen reported dependencies: ten regular and three weak-link.

The target PrebuiltLoaderSet output does not print a Mach-O UUID or source
version. The previously inspected target image inventory supplies those
separately: version `5100.27.0.0.0`, UUID
`304953E6-6B67-3CF1-B7CA-E011978210DE`, image-list index `1948`.

The target's printed `Sections` block contains implausibly large decoded
offsets/sizes, as also occurred in the donor query. Those section rows are
excluded from interpretation. This is a parser-output limitation, not
evidence that the cached image is corrupt.

The direct dependency comparison shows that 13 of the donor's 14 reported
dependency names also appear in the target record. The donor-only row is
`SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter`.
The IOKit framework appears in both records but the printed install path
differs: the target includes `Versions/A/IOKit`, while the donor output
does not. See the comparison document for all paths and edge labels.

## Completed target dependency image inventory lookup

The user searched the existing read-only
`$HOME/19H422-dyld-images.json` inventory for the selected dependency names.
Seven relevant image records were returned: SymptomDiagnosticReporter,
WirelessDiagnostics, CoreAccessories, CoreAnalytics, MultitouchSupport,
IOKit, and ProtocolBuffer. The most important result is that target
SymptomDiagnosticReporter exists in the cache image list at index 1455,
version `174.140.2.0.0`, UUID
`ED77A600-C0BE-3240-9693-BF5238095816`, even though the target
MultitouchHID PrebuiltLoaderSet record does not list it as a direct
dependency.

The other six selected image records, their full paths, versions, and
UUIDs, are recorded in the
[target dependency image inventory](iphone91-19h422-multitouch-dependency-image-inventory.md).
A broad `IOKit.framework` substring search also returned CoreAudioKit;
that is a separate framework and not a second IOKit result.

This confirms cache image-list representation only. It does not prove
standalone filesystem presence, runtime dependency resolution, successful
loading, or transitive dependency closure.

## Completed donor/target inventory comparison

The user supplied the equivalent seven-name lookup from the existing
read-only donor inventory `$HOME/20H392-dyld-images.json`. All seven
selected image families are present in the donor and target inventories.
Every corresponding record has a different version string and UUID.
The complete side-by-side comparison is recorded in
[the donor/target dependency image comparison](20h392-19h422-multitouch-dependency-image-comparison.md).

This closes the selected image-list inventory check only. It does not
establish binary compatibility, dependency resolution, plugin loading,
or hardware behavior. The next bounded host-side research task is to inspect
the loader metadata for the target and donor `MultitouchSupport` images
and compare it with the existing target/donor `AppleMultitouchSPI` and
`AppleHIDTransportSPI` KernelCache records. Keep cache image-list
membership, loader edges, KEXT metadata, and runtime behavior separate.
