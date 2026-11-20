# iOS 20H392 FontServices and CoreText dependency results

## Scope and provenance

This note records the four user-supplied `ipsw dyld image` dependent blocks
for the iPhone X iOS 16.7.16 (20H392) donor SystemOS shared cache:

- FontServices `libFontParser.dylib`
- FontServices `FontServices`
- FontServices `libGSFontCache.dylib`
- CoreText `CoreText`

All four commands reported exit status 0. The supplied output showed no
stderr text. The actual stderr files were not supplied separately.

Project Sweet-10's target remains iPhone 7 `iPhone9,1` / D10AP /
A10-T8010. Every item below is donor-side static loader metadata and is not
evidence of iPhone9,1 runtime compatibility, target drivers, or a successful
SpringBoard launch.

## Summary

| Requested image | Regular | Explicit weak-link | Raw kind 3 (weak-link + re-export) |
|---|---:|---:|---:|
| `libFontParser.dylib` | 10 | 0 | 1 |
| `FontServices` | 6 | 1 | 2 |
| `libGSFontCache.dylib` | 4 | 0 | 0 |
| `CoreText` | 17 | 0 | 3 |
| **Total** | **37** | **1** | **6** |

The six raw kind-3 entries were printed by ipsw as `unknown 3`. The exact
ipsw source revision and Apple dyld bitfield mapping are documented in
[the earlier framework results](20h392-platform-framework-dependency-results.md):
kind value 3 sets weak-link bit 0 and re-export bit 1. The original raw label
is preserved in each inventory below.

## Ordered dependent records

### FontServices: libFontParser.dylib

One raw kind-3 dependent (printed as `unknown 3`):

- `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`

Ten regular dependents, in printed order:

1. `/System/Library/PrivateFrameworks/FontServices.framework/libhvf.dylib`
2. `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`
3. `/usr/lib/libcompression.dylib`
4. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
5. `/System/Library/Frameworks/Foundation.framework/Foundation`
6. `/usr/lib/libicucore.A.dylib`
7. `/usr/lib/libxml2.2.dylib`
8. `/usr/lib/libobjc.A.dylib`
9. `/usr/lib/libc++.1.dylib`
10. `/usr/lib/libSystem.B.dylib`

### FontServices: FontServices

Two raw kind-3 dependents (each printed as `unknown 3`):

1. `/System/Library/Frameworks/CoreText.framework/CoreText`
2. `/System/Library/PrivateFrameworks/FontServices.framework/libGSFont.dylib`

Six regular dependents, in printed order:

1. `/System/Library/Frameworks/Security.framework/Security`
2. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
3. `/System/Library/Frameworks/Foundation.framework/Foundation`
4. `/usr/lib/libobjc.A.dylib`
5. `/usr/lib/libc++.1.dylib`
6. `/usr/lib/libSystem.B.dylib`

One explicit weak-link dependent:

- `/System/Library/PrivateFrameworks/SpringBoardServices.framework/SpringBoardServices`

### FontServices: libGSFontCache.dylib

Four regular dependents, in printed order:

1. `/System/Library/Frameworks/Foundation.framework/Foundation`
2. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
3. `/usr/lib/libSystem.B.dylib`
4. `/usr/lib/libobjc.A.dylib`

### CoreText

Three raw kind-3 dependents (each printed as `unknown 3`):

1. `/System/Library/PrivateFrameworks/FontServices.framework/libGSFontCache.dylib`
2. `/System/Library/PrivateFrameworks/FontServices.framework/libGSFont.dylib`
3. `/usr/lib/libAccessibility.dylib`

Seventeen regular dependents, in printed order:

1. `/System/Library/PrivateFrameworks/OTSVG.framework/OTSVG`
2. `/usr/lib/libcompression.dylib`
3. `/System/Library/Frameworks/Accelerate.framework/Accelerate`
4. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
5. `/System/Library/Frameworks/Foundation.framework/Foundation`
6. `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`
7. `/System/Library/Frameworks/CoreServices.framework/CoreServices`
8. `/System/Library/PrivateFrameworks/FontServices.framework/FontServices`
9. `/System/Library/Frameworks/ImageIO.framework/ImageIO`
10. `/System/Library/Frameworks/UniformTypeIdentifiers.framework/UniformTypeIdentifiers`
11. `/usr/lib/libicucore.A.dylib`
12. `/usr/lib/libobjc.A.dylib`
13. `/System/Library/PrivateFrameworks/FontServices.framework/libFontParser.dylib`
14. `/usr/lib/libMobileGestalt.dylib`
15. `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`
16. `/usr/lib/libc++.1.dylib`
17. `/usr/lib/libSystem.B.dylib`

## Derived donor-side relationships

The four records add these direct edges:

- `libFontParser.dylib` → CoreGraphics (weak-link + re-export; raw kind 3).
- `libFontParser.dylib` → libhvf, SoftLinking, libcompression,
  CoreFoundation, Foundation, libicucore, libxml2, libobjc, libc++, and
  libSystem (regular).
- `FontServices` → CoreText and libGSFont
  (weak-link + re-export; raw kind 3).
- `FontServices` → Security, CoreFoundation, Foundation, libobjc,
  libc++, and libSystem (regular).
- `FontServices` → SpringBoardServices (explicit weak link).
- `libGSFontCache.dylib` → Foundation, CoreFoundation, libSystem,
  and libobjc (regular).
- `CoreText` → libGSFontCache, libGSFont, and libAccessibility
  (weak-link + re-export; raw kind 3).
- `CoreText` → OTSVG, libcompression, Accelerate, CoreFoundation,
  Foundation, CoreGraphics, CoreServices, FontServices, ImageIO,
  UniformTypeIdentifiers, libicucore, libobjc, libFontParser,
  MobileGestalt, SoftLinking, libc++, and libSystem (regular).

### Graph observations

- **CoreGraphics / libFontParser reciprocal references:** CoreGraphics
  lists libFontParser as regular, while libFontParser lists CoreGraphics
  with raw kind 3 (weak-link + re-export). This is not a pair of equivalent
  strong edges; preserve each direction's original kind.
- **FontServices / CoreText / libGSFont family:** FontServices has kind-3
  edges to CoreText and libGSFont; CoreText has kind-3 edges back to
  libGSFont and libGSFontCache; libGSFont's earlier inventory has kind-3
  edges to CoreText, FontServices, and libGSFontCache.
- **FontServices → SpringBoardServices:** this is an explicit weak-link
  dependency. It does not by itself show a runtime call relationship or
  prove SpringBoardServices is required for all FontServices use.
- The `libGSFontCache.dylib` record contains only the four common runtime
  dependencies printed above; the supplied record does not add a new
  downstream framework beyond those.

These are relationships in the donor's PrebuiltLoaderSet records, not proof
that every listed path is loaded in a particular process. Weak-link and
re-export flags must not be flattened to ordinary dependency edges.

## Interpretation limits

- The source mapping of raw kind 3 is verified against the pinned ipsw and
  Apple dyld definitions, but the raw dependent-kind bytes have not been
  separately extracted from the cache.
- Successful parser exit status does not prove runtime loading or API use.
- The CoreGraphics / libFontParser reference pattern is not evidence of an
  unresolved runtime cycle; dyld's weak-link and re-export semantics matter.
- No font framework result establishes that the A10/T8010 GPU, display
  pipeline, CoreText clients, BackBoard stack, or target IOKit providers work.
- The earlier suspicious Swift/Objective-C section-offset issue remains
  separate and unresolved.

## Next phase: target-side applicability crosswalk

The planned generic donor-framework crawl is now complete for this bounded
font chain. Further generic cache expansion has diminishing value unless a
concrete requirement needs it.

The next useful step is to compare selected donor requirements against
target-native iPhone9,1 evidence: board-specific DeviceTree properties,
display and touch device descriptions, available kernel/driver identifiers,
and service/provider names. The next plan is
[the iPhone9,1 hardware and service crosswalk](iphone9,1-target-hardware-crosswalk.md).

M6 remains in progress. M7 (SpringBoard on iPhone 7) has not started.

## References

- [20H392 IOKit and font-framework dependency results](20h392-iokit-font-framework-dependency-results.md)
- [20H392 service and graphics dependency results](20h392-platform-framework-dependency-results.md)
- [ipsw 3.1.749 dependent-kind formatter](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/dyld/prebuilt_types.go)
- [Apple dyld LinkedDylibAttributes bitfield](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/mach_o/UnsafeHeader.h)
