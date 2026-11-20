# 20H392 service and graphics dependency inspection plan

## Scope

This read-only host-side inspection for the iPhone X iOS 16.7.16 (20H392)
donor SystemOS cache is complete. The collected dependent records for
BoardServices, BaseBoard, GraphicsServices, RunningBoardServices,
AssertionServices, and IOSurface are documented in
[the result inventory](20h392-platform-framework-dependency-results.md).

The physical Project Sweet-10 target remains iPhone 7 `iPhone9,1` / D10AP /
A10-T8010. The donor cache must not be treated as target firmware or target
compatibility evidence. Do not change the phone's firmware or boot state for
these static queries.

## Why these three images

The next bounded set is selected from observed edges:

- **IOKit** is named by BaseBoard, IOSurface, BackBoard HID frameworks,
  BackBoardServices, and IOMobileFramebuffer. Inspecting its donor loader
  metadata gives the shared userspace dependency shape, but does not reveal
  the target's actual IOKit drivers or providers.
- **CoreGraphics** is named by BaseBoard and BackBoardServices and is central
  to the donor-side graphics framework chain.
- **FontServices/libGSFont.dylib** is the exact install name associated with
  the GraphicsServices row printed as `unknown 3`. The pinned ipsw parser
  defines kind 1 as weak-link and kind 2 as re-export, but its exact-value
  formatter does not name combined value 3. Apple dyld formats those attributes
  independently, so 3 is likely weak-link + re-export. Preserve the raw value
  and inspect the corresponding loader; do not treat it as a regular edge.

## Commands on the analysis PC

Use the existing read-only SystemOS Cryptex mount. Keep output files outside
the repository:

```sh
CACHE="$HOME/20H392/systemos-mnt/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/20H392/framework-closures"
mkdir -p "$OUT"

for IMAGE in \
  /System/Library/Frameworks/IOKit.framework/Versions/A/IOKit \
  /System/Library/Frameworks/CoreGraphics.framework/CoreGraphics \
  /System/Library/PrivateFrameworks/FontServices.framework/libGSFont.dylib
do
  NAME=$(basename "$IMAGE")
  printf '\n=== Inspecting %s ===\n' "$NAME"

  ipsw dyld image "$CACHE" "$IMAGE" \
    > "$OUT/$NAME.txt" 2> "$OUT/$NAME.err"
  STATUS=$?

  printf 'Exit status: %s\n' "$STATUS"
  if [ -s "$OUT/$NAME.err" ]; then
    cat "$OUT/$NAME.err"
  fi
  if [ -s "$OUT/$NAME.txt" ]; then
    sed -n '/^Dependents:/,/^BindTargets:/p' "$OUT/$NAME.txt"
  fi
done
```

Keep the full output and stderr files. If the FontServices image lookup
returns no loader, report the exact exit status, stderr, and first part of
the output. Do not substitute a similarly named image without documenting
the exact requested and returned paths.

## Record rules

- Preserve the printed dependency kind exactly: regular, weak-link, re-export,
  or an unknown numeric kind.
- Keep bind targets separate from dependency edges.
- For raw kind 3, record weak-link + re-export based on the pinned ipsw
  constants and Apple's independent bitfield formatting. Preserve the raw
  `unknown 3` display; the original cache byte has not been separately extracted.
- Preserve weak links as weak edges. Do not drop them from the graph or
  promote them to hard requirements.
- Deduplicate only a derived graph view; keep the original per-image ordered
  records in the evidence document.
- A missing path on the OS root filesystem alone is not proof of absence:
  the root filesystem and SystemOS Cryptex are separate volumes.
- Do not commit the proprietary shared cache, binaries, IPSW/DMG data,
  raw device identifiers, or full private machine data. Commit reviewed,
  sanitized path/count observations only.

## What this inspection can and cannot answer

The loader outputs can extend a static iPhone X donor dependency graph.
They cannot establish:

- actual runtime API use or successful `dlopen`;
- successful daemon or SpringBoard startup;
- code-signing, entitlement, closure validation, or service registration;
- iPhone9,1 kernel drivers, IOKit personalities, or DeviceTree resources;
- matching A10 graphics/framebuffer/HID implementations.

After these three results are reviewed, choose further donor inspections from
the observed graph, then separately map requirements to verified iPhone9,1
stock firmware and XNU source evidence. Keep donor-only, target-confirmed,
missing, and unverified findings separate.

M6 remains in progress; M7 has not started.

## References

- [Apple dyld4 design](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md)
- [ipsw dyld guide](https://blacktop.github.io/ipsw/docs/guides/dyld/)
- [20H392 service and graphics dependency results](20h392-platform-framework-dependency-results.md)
- [20H392 BackBoard framework dependency results](20h392-backboard-framework-dependency-results.md)


## Results collected

All three queries (IOKit, CoreGraphics, and libGSFont.dylib) reported exit
status 0. Their dependent blocks contain 25 regular rows, one explicit weak
link, and three kind-3 rows from libGSFont. The three kind-3 rows are now
source-mapped to weak-link + re-export using the pinned ipsw and Apple dyld
definitions; the original `unknown 3` labels remain in the result inventory.
See [the IOKit and font-framework results](20h392-iokit-font-framework-dependency-results.md).

The next bounded inspection follows libFontParser, FontServices,
libGSFontCache, and CoreText. See
[the FontServices/CoreText plan](20h392-fontservices-coretext-plan.md).
