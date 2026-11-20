# iOS 20H392 IOKit and font-framework dependency results

## Scope

This note records three user-supplied `ipsw dyld image` dependent blocks from
the iPhone X iOS 16.7.16 (20H392) donor SystemOS shared cache:

- IOKit
- CoreGraphics
- FontServices `libGSFont.dylib`

All three commands reported exit status 0. The supplied terminal output showed
no stderr text. Project Sweet-10's actual target remains iPhone 7
`iPhone9,1` / D10AP / A10-T8010. These are donor-side static loader records,
not target runtime observations.

## Summary

| Requested image | Regular | Explicit weak-link | Raw kind 3 (weak-link + re-export) |
|---|---:|---:|---:|
| IOKit | 6 | 0 | 0 |
| CoreGraphics | 12 | 1 | 0 |
| libGSFont.dylib | 7 | 0 | 3 |
| **Total** | **25** | **1** | **3** |

The three `libGSFont.dylib` rows are printed by ipsw as `unknown 3`.
The source-level decoding described below indicates that raw kind value 3
sets both the weak-link and re-export attributes. The original printed
representation is retained in every case.

## Ordered dependent records

### IOKit

Six regular dependents, in printed order:

1. `/usr/lib/libenergytrace.dylib`
2. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
3. `/usr/lib/libz.1.dylib`
4. `/usr/lib/libbsm.0.dylib`
5. `/usr/lib/libSystem.B.dylib`
6. `/usr/lib/libobjc.A.dylib`

### CoreGraphics

Twelve regular dependents, in printed order:

1. `/System/Library/PrivateFrameworks/FontServices.framework/libFontParser.dylib`
2. `/usr/lib/libMobileGestalt.dylib`
3. `/System/Library/Frameworks/IOSurface.framework/IOSurface`
4. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
5. `/System/Library/Frameworks/Foundation.framework/Foundation`
6. `/usr/lib/libz.1.dylib`
7. `/usr/lib/libxml2.2.dylib`
8. `/System/Library/Frameworks/Accelerate.framework/Accelerate`
9. `/System/Library/Frameworks/CFNetwork.framework/CFNetwork`
10. `/usr/lib/libc++.1.dylib`
11. `/usr/lib/libSystem.B.dylib`
12. `/usr/lib/libobjc.A.dylib`

One explicit weak-link dependent:

- `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics`

### FontServices: libGSFont.dylib

Three raw kind-3 dependents (each printed as `unknown 3`):

1. `/System/Library/Frameworks/CoreText.framework/CoreText`
2. `/System/Library/PrivateFrameworks/FontServices.framework/FontServices`
3. `/System/Library/PrivateFrameworks/FontServices.framework/libGSFontCache.dylib`

Seven regular dependents, in printed order:

1. `/usr/lib/libMobileGestalt.dylib`
2. `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`
3. `/System/Library/Frameworks/Foundation.framework/Foundation`
4. `/usr/lib/libobjc.A.dylib`
5. `/usr/lib/libSystem.B.dylib`
6. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
7. `/System/Library/Frameworks/Security.framework/Security`

## Decoding raw dependency kind 3

The exact ipsw build used for these inspections was 3.1.749, with source
commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`.

In that pinned ipsw source, `pkg/dyld/prebuilt_types.go` defines:

- `KindNormal = 0`
- `KindWeakLink = 1`
- `KindReexport = 2`
- `KindUpward = 4`
- `KindDelayed = 8`

Its `DependentKind.String()` uses an exact-value switch, so combined value
`3` does not match either the single weak-link value `1` or the single
re-export value `2`; ipsw therefore prints `unknown 3`.

Apple dyld's source defines `LinkedDylibAttributes` as a one-byte bitfield:
`weakLink` is bit 0 and `reExport` is bit 1. Its
`LinkedDylibAttributes::toString()` checks and appends those two fields
independently. Therefore the parsed kind value `3` (binary `00000011`)
means **weak-link + re-export** in Apple's attribute layout.

This is a source-verified mapping of the numeric kind that ipsw printed,
not a fresh independent extraction of the byte from the split cache. The raw
terminal text `unknown 3` remains preserved to make the parser behavior
auditable. Do not convert these edges into ordinary strong dependencies.

References pinned for this interpretation:

- [ipsw 3.1.749 dependent-kind definitions and formatter](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/dyld/prebuilt_types.go)
- [Apple dyld LinkedDylibAttributes bitfield](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/mach_o/UnsafeHeader.h)
- [Apple dyld LinkedDylibAttributes::toString implementation](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/mach_o/UnsafeHeader.cpp)

## Derived donor-side relationships

The new records add these direct edges:

- `IOKit` → `libenergytrace.dylib`, CoreFoundation, libz, libbsm,
  libSystem, and libobjc (all regular).
- `CoreGraphics` → `libFontParser.dylib`, MobileGestalt, IOSurface,
  CoreFoundation, Foundation, libz, libxml2, Accelerate, CFNetwork,
  libc++, libSystem, and libobjc (all regular).
- `CoreGraphics` → `CoreAnalytics` (explicit weak link).
- `libGSFont.dylib` → `CoreText`, FontServices, and
  `libGSFontCache.dylib` (each weak-link + re-export, raw kind 3).
- `libGSFont.dylib` → MobileGestalt, CoreGraphics, Foundation, libobjc,
  libSystem, CoreFoundation, and Security (all regular).

The font-related chain is now better defined: CoreGraphics has a regular
edge to `libFontParser.dylib`; GraphicsServices had a raw kind-3 edge to
`libGSFont.dylib`; and `libGSFont.dylib` has three raw kind-3 edges to
CoreText, FontServices, and libGSFontCache. Keep the edge kinds intact
throughout any graph rendering or summary.

## Interpretation limits

- These are iPhone X 20H392 donor records, not iPhone9,1 measurements.
- IOKit's six dependent libraries do not identify its kernel-side drivers,
  IOKit personalities, matching DeviceTree providers, or actual hardware.
- CoreGraphics' dependencies do not prove an A10-compatible GPU, framebuffer,
  display pipeline, or IOSurface provider.
- The weak-link CoreAnalytics row and the three weak-link + re-export font
  rows are not ordinary strong dependencies.
- A successful `ipsw dyld image` parse does not prove that any process or
  framework loads successfully at runtime.
- The unrelated suspicious Swift/Objective-C section offsets in earlier
  output remain excluded pending independent parser validation.

## Completed FontServices/CoreText expansion

The four font-chain loader records named in the prior inspection plan have
now been queried successfully. Their ordered dependency records, counts,
and graph observations are documented in
[the FontServices and CoreText dependency results](20h392-fontservices-coretext-dependency-results.md).

The next phase is a target-side applicability crosswalk against verified
iPhone9,1 artifacts, not a further broad crawl of generic donor frameworks.
See [the iPhone9,1 target-native hardware and service crosswalk](iphone9,1-target-hardware-crosswalk.md).

M6 remains in progress. M7 (SpringBoard on iPhone 7) has not started.

## References

- [20H392 split dyld shared-cache inventory](20h392-dyld-cache-inventory.md)
- [20H392 service and graphics dependency results](20h392-platform-framework-dependency-results.md)
- [20H392 BackBoard framework dependency results](20h392-backboard-framework-dependency-results.md)
- [Apple dyld4 design](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md)


## Completed FontServices/CoreText expansion

The user's four additional loader queries succeeded and are documented in
[the FontServices and CoreText dependency results](20h392-fontservices-coretext-dependency-results.md).
The new records contain 37 regular dependencies, one explicit weak link, and
six raw kind-3 rows mapped to weak-link + re-export from the pinned dyld
attribute definition. The next task is to cross-check concrete donor-side
requirements against iPhone9,1 target-native evidence.
