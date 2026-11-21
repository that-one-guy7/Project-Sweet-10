# iPhone9,1 / 19H422 versus iPhone10,3 / 20H392 AGX and Metal userland audit plan

## Purpose and boundary

This plan defines the next bounded, read-only host-side comparison for the
Project Sweet-10 graphics path:

- Target hardware reference: iPhone 7 `iPhone9,1` / D10AP / A10-T8010,
  iOS 15.8.8 build `19H422`.
- Donor userland reference: iPhone X `iPhone10,3` / D22AP / A11-T8015,
  iOS 16.7.16 build `20H392`.

The physical iPhone 7 remains on iOS 12.1.4. The two IPSW/cache sets are
host-side reference artifacts. This procedure reads parsed KEXT JSON and
dyld shared-cache metadata only. It does not extract or execute graphics
binaries, load a KEXT, connect to the phone, or change firmware, partitions,
security state, or boot state.

The goal is to identify the graphics-related image records and their
prebuilt-loader dependency metadata on both sides. It is not to make a
compatibility verdict from matching names or differing UUIDs.

## Evidence already recorded

### Target 19H422 KEXT metadata

The target KernelCache inventory records:

- `com.apple.AGXG9P`, version / source version `190.23`.
- Personalities `AGXG9P_A0` and `AGXG9P_B0`.
- Accelerator classes `AGXAcceleratorG9P_A0` and
  `AGXAcceleratorG9P_B0`.
- `IONameMatch=gpu,t8010`.
- `MetalPluginName=AGXMetalA10`.
- `com.apple.iokit.IOGPUFamily`, version `35.29`.

These are target-side parsed KernelCache metadata records. The inventory
does not establish that the GPU driver attaches to a live provider or that
the Metal stack works.

### Donor 20H392 KEXT metadata

The selected donor record is `com.apple.AGXG10P`, not AGXG9P. It contains
`AGXG10P_A0` and `AGXG10P_B0`, uses the match string
`gpu,t8015`, and names `AGXMetalG10A0` / `AGXMetalA11` in its
personalities. The seven-pair recursive comparison records 41 differing
JSON paths between AGXG9P and AGXG10P.

This is a generation-specific metadata difference between T8010 and T8015.
Do not treat the donor's AGXG10P KEXT or plugin labels as substitutes for
the target's AGXG9P record.

### Cache evidence already recorded

The 20H392 donor dyld image inventory lists, among other GUI-related images:

| Image | Donor 20H392 reported version |
|---|---:|
| `CoreGraphics.framework/CoreGraphics` | `1690.8.1` |
| `Metal.framework/Metal` | `306.6.6` |
| `IOSurface.framework/IOSurface` | `336.60.1` |
| `IOKit.framework/Versions/A/IOKit` | `2022.140.2.701.1` |

The 19H422 target split dyld cache and JSON image inventory have already
been located and used for the multitouch/BackBoard audits. A focused,
paired graphics-image table (including target/donor version strings, UUIDs,
and loader dependency rows) has not yet been recorded in the repository.
That is the next evidence gap.

## Step 1 — extract the selected graphics KEXT metadata

From the repository root, run:

```bash
python3 tools/inspect_graphics_kext_metadata.py \
  --target "$HOME/19H422-kernel-inspect/analysis/kexts.json" \
  --donor "$HOME/20H392-kernel-inspect/analysis/kexts.json" \
  | tee "$HOME/19H422-20H392-graphics-kext-metadata.json"
```

The read-only helper selects exact top-level IDs for:

| Target 19H422 | Donor 20H392 | Reason |
|---|---|---|
| `com.apple.AGXG9P` | `com.apple.AGXG10P` | T8010 / T8015 accelerator records |
| `com.apple.iokit.IOGPUFamily` | `com.apple.iokit.IOGPUFamily` | Shared GPU framework-family record, if present in both inventories |
| `com.apple.driver.AppleA7IOP` | `com.apple.driver.AppleA7IOP` | Shared I/O-processor metadata with a retained T8010 graphics-IO personality |

The output preserves the selected identity fields, `os_bundle_libraries`,
and complete `io_kit_personalities` subtrees. Missing fields remain omitted;
explicit `null` and empty strings remain unchanged. A missing top-level
record is reported only as absent from that parsed JSON inventory.

The paths above match the previously documented local inventory layout. If
the JSON files are stored elsewhere, change only the two input path values;
do not change the bundle IDs to make a record appear.

Run the test suite after pulling this branch:

```bash
python3 -m unittest discover -s tests -v
```

## Step 2 — inventory both dyld caches for exact graphics image paths

Use the already mounted, read-only cache locations:

```bash
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
DONOR_CACHE="$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/agx-metal-static-audit"
mkdir -p "$OUT"

test -r "$TARGET_CACHE" || echo "Target cache is not readable: $TARGET_CACHE"
test -r "$DONOR_CACHE" || echo "Donor cache is not readable: $DONOR_CACHE"

set +e
ipsw dyld info -l "$TARGET_CACHE" \
  > "$OUT/19H422-image-list.txt" 2> "$OUT/19H422-image-list.err"
printf '19H422 image-list exit status: %s\n' "$?" | tee "$OUT/19H422-image-list.status"

ipsw dyld info -l "$DONOR_CACHE" \
  > "$OUT/20H392-image-list.txt" 2> "$OUT/20H392-image-list.err"
printf '20H392 image-list exit status: %s\n' "$?" | tee "$OUT/20H392-image-list.status"
set -e

for LABEL in 19H422 20H392; do
  grep -Ei 'AGX|Metal|IOGPU|IOSurface|IOMobileFramebuffer|CoreGraphics|GPU' \
    "$OUT/$LABEL-image-list.txt" > "$OUT/$LABEL-graphics-candidates.txt" || true
done
```

Keep the full image-list files, stderr files, and exit-status files. The
`ipsw dyld info -l` listing is used to discover exact install paths; do not
invent an AGX plug-in path from the `MetalPluginName` string alone.
A `MetalPluginName` personality value is not itself proof of a corresponding
dyld image path.

The target and donor use split caches. Keep each cache's companion files
beside its main cache file. Do not concatenate, rename, or mix the donor and
target subcaches.

## Step 3 — inspect the exact image loader records

For each exact image path found in both image lists, run the loader query
against each cache separately. Example for the Metal framework path, only
after that exact path is confirmed in the image list:

```bash
IMAGE="/System/Library/Frameworks/Metal.framework/Metal"

ipsw dyld image "$TARGET_CACHE" "$IMAGE" -V \
  > "$OUT/19H422-Metal.txt" 2> "$OUT/19H422-Metal.err"
printf '19H422 Metal query exit status: %s\n' "$?"

ipsw dyld image "$DONOR_CACHE" "$IMAGE" -V \
  > "$OUT/20H392-Metal.txt" 2> "$OUT/20H392-Metal.err"
printf '20H392 Metal query exit status: %s\n' "$?"
```

Repeat for the confirmed exact paths for CoreGraphics, IOSurface, IOKit,
IOMobileFramebuffer, IOGPU-related images, and any AGX Metal plug-in images
found in the cache listings. If a path differs between builds, query each
exact path separately and preserve the distinct paths in the report.

Record, when the tool prints them:

- Exact image install path and cache identity.
- Image-list version and Mach-O UUID from the JSON/image inventory.
- Prebuilt-loader reference fields, keeping loader reference indexes separate
  from image-list indexes.
- Ordered dependent-image paths and their printed kinds (regular,
  weak-link, re-export, or other).
- Bind-target information separately from dependency edges.

Keep the full command output and stderr. Do not use suspicious or implausible
decoded section offsets as evidence. Do not interpret an image-list index as
a cross-cache identity; indexes are local to each cache.

The upstream ipsw dyld guide documents the `dyld info` image listing and
`dyld image` inspection forms. See the references below.

## Step 4 — compare results without overclaiming

The result table should contain one row per exact image path or clearly
paired counterpart:

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| Exact install path | Observed path | Observed path |
| Image version | Observed value or not printed | Observed value or not printed |
| Mach-O UUID | Observed UUID or not printed | Observed UUID or not printed |
| Loader dependencies | Ordered path + kind list | Ordered path + kind list |
| Query status | Exit status / stderr status | Exit status / stderr status |

Interpretation rules:

1. A different Mach-O UUID identifies a different recorded build; it does
   not by itself prove incompatibility.
2. A matching UUID would be an identity clue, not proof of runtime loading,
   code-signing validity, or hardware support.
3. Cache image-list membership is distinct from a PrebuiltLoaderSet
   dependency edge. A framework can be present in the cache but not be a
   direct dependency of the selected loader.
4. Preserve weak-link and re-export kinds. Do not promote them to ordinary
   strong dependencies.
5. A KEXT bundle's presence or `IONameMatch` value does not prove runtime
   IOKit attachment, GPU initialization, or rendered output.
6. The target and donor are different iOS releases and different SoCs.
   Differences cannot be attributed to hardware alone.

## Expected deliverable and status

The next result report should include the selected KEXT metadata output, the
exact target/donor image paths, per-image version/UUID records, and direct
loader dependencies where the parser exposes them. It must distinguish
target-confirmed, donor-only, absent-from-this-inventory, and unverified
findings.

This plan does not report that an iPhone 7 iOS 16 build works. M6 remains in
progress; M7/SpringBoard has not started. The physical iPhone 7 remains on
iOS 12.1.4.

## References

- [ipsw dyld shared-cache guide](https://blacktop.github.io/ipsw/docs/guides/dyld/)
- [Apple dyld shared-cache format](https://github.com/apple-oss-distributions/dyld/blob/main/include/mach-o/dyld_cache_format.h)
- [Target 19H422 KernelCache KEXT inventory](iphone91-19h422-kernelcache-kext-inventory.md)
- [Target/donor selected KEXT metadata comparison](20h392-19h422-selected-kext-metadata-field-comparison.md)
- [Seven-pair recursive KEXT comparison](20h392-19h422-seven-pair-kext-recursive-results.md)
- [Target 19H422 dyld cache multitouch audit](iphone91-19h422-dyld-cache-multitouch-audit.md)
- [20H392 donor dyld cache inventory](20h392-dyld-cache-inventory.md)
