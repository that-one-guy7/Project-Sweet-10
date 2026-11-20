# 20H392 BackBoard framework dependency expansion

## Scope and status

This note defines the next read-only host-side inspection for the iPhone X
iOS 16.7.16 (20H392) donor SystemOS shared cache. **This is an inspection
plan, not a report of results:** the four framework-specific loader records
below have not yet been supplied or validated.

The Project Sweet-10 target remains iPhone 7 `iPhone9,1` / D10AP /
A10-T8010. Nothing in this donor cache establishes target compatibility.
Keep donor observations and iPhone9,1 evidence in separate columns.

## Why these four images

The supplied `backboardd` PrebuiltLoaderSet record listed the following
install names as direct dependents:

- `BackBoardHIDEventFoundation`
- `BackBoardHIDEventProcessors`
- `IOMobileFramebuffer`
- `BackBoardServices`

All four images also appear in the previously inventoried 20H392 SystemOS
cache image list. They are the best next bounded expansion because they cover
the donor's HID-event, display/framebuffer, and BackBoard service interfaces.
Their presence in the donor cache does **not** demonstrate that matching
iPhone9,1 providers or drivers exist.

## Reproduction on the analysis PC

Use the already-mounted, separate SystemOS Cryptex cache. Do not substitute the
OS root-filesystem mount or the DriverKit cache.

```sh
CACHE="$HOME/20H392/systemos-mnt/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/20H392/framework-closures"
mkdir -p "$OUT"

for IMAGE in \
  /System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation \
  /System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors \
  /System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices \
  /System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer
do
  NAME=$(basename "$IMAGE")
  printf '\n=== %s ===\n' "$IMAGE"

  ipsw dyld image "$CACHE" "$IMAGE" \
    > "$OUT/$NAME.txt" \
    2> "$OUT/$NAME.err"
  STATUS=$?

  printf 'exit status: %s\n' "$STATUS"
  if [ -s "$OUT/$NAME.err" ]; then
    cat "$OUT/$NAME.err"
  fi
  if [ -s "$OUT/$NAME.txt" ]; then
    sed -n '/^Dependents:/,/^BindTargets:/p' "$OUT/$NAME.txt"
  fi
done
```

This uses the `ipsw dyld image <DSC> <IMAGE>` form documented by the
ipsw dyld guide. The exact install paths are chosen from the user's prior
20H392 cache inventory and backboardd output. Preserve each complete output
file and its stderr file. A nonzero exit, missing loader, or empty dependent
block is a result to report, not a reason to silently substitute another image.
If the tool rejects an absolute path, record the exact error before trying a
unique image-name lookup; verify the printed image path before accepting it.

## How to record the results

For each framework, record:

1. Exact requested install path and the path printed by ipsw.
2. ipsw version, exit status, stderr, and PrebuiltLoaderSet version/flags.
3. Every `Dependents` entry in source order, retaining its kind
   (`regular`, `weak-link`, or any other printed kind).
4. Every `BindTargets` entry separately. Do not infer an API or hardware
   provider from a bind-target offset alone.
5. Whether the dependent install name is listed in the donor cache inventory,
   present on the mounted donor root/SystemOS volumes, app-bundle-local, or
   unresolved. A root-volume-only miss is not proof that an image is absent
   from the complete donor system.

Keep the raw per-image outputs outside Git. Commit only a reviewed, sanitized
summary of paths, counts, and relevant caveats. Do not commit IPSW/DMG files,
shared-cache binaries, private identifiers, or entire proprietary loader
records.

## Graph rules and interpretation limits

Apple's dyld4 design describes PrebuiltLoaders as read-only metadata containing
dependent dylibs and precomputed bind targets. The dyld source also describes
recursive dependent loading and missing weak images. This supports using
loader records as static graph evidence, but not treating the printed graph as
a successful process launch.

- Add a directed edge from the inspected image to each reported dependent.
- Preserve the weak-link kind. The earlier backboardd record's
  `index: 32767 (missing weak image)` has no install name in the supplied
  output; it remains an unresolved weak edge.
- Keep bind-target records separate from dependent edges.
- When the same install name occurs more than once, preserve the original
  rows and deduplicate only a derived graph view.
- Continue recursively only for dependent images whose loader records can be
  independently queried. Stop and label unresolved paths instead of guessing.
- Do not use the suspicious Swift/Objective-C section offsets from the earlier
  ipsw output to calculate file ranges or infer image layout; that parser
  question remains open.
- A dependency on IOKit, framebuffer, HID, or a BackBoard framework is not
  proof that an iPhone9,1 DeviceTree node, kernel driver, IOKit provider,
  entitlement, or Mach service satisfies the dependency.

## Next M6 decision

After the four outputs are reviewed, select the next layer based on the actual
reported dependents rather than preselecting an assumed framework tree. Later
candidates may include `BoardServices`, `IOSurface`, `IOKit`,
`QuartzCore`, `CoreGraphics`, and `CoreBrightness`, but inspect them only
when the collected edges justify it.

M6 remains in progress until the donor dependency graph is documented and
the relevant services are separately matched against reliable iPhone9,1
evidence. M7 (SpringBoard on the iPhone 7) has not started. No device, firmware,
activation state, partition, or security setting is changed by this work.

## References

- [Apple dyld4 design](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md)
- [Apple PrebuiltLoader implementation](https://github.com/apple-oss-distributions/dyld/blob/main/dyld/PrebuiltLoader.cpp)
- [ipsw dyld guide](https://blacktop.github.io/ipsw/docs/guides/dyld/)
- [20H392 split-cache inventory](20h392-dyld-cache-inventory.md)
- [20H392 PrebuiltLoaderSet audit](20h392-prebuilt-loader-audit.md)


## Results collected

All four requested ipsw dyld image queries exited 0. The supplied output has
10 regular dependencies for BackBoardHIDEventFoundation, 9 for
BackBoardHIDEventProcessors, 12 regular dependencies plus one re-export for
BackBoardServices, and 4 regular dependencies for IOMobileFramebuffer.
No weak-link rows appeared in these four blocks. See the
[result inventory](20h392-backboard-framework-dependency-results.md) for
the complete ordered lists and derived edges.

The next inspection candidates are selected from those observed edges; they
are not pre-asserted recursive requirements.
