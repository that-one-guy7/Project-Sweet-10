# iOS 20H392 service and graphics framework dependency results

## Scope

This note records six user-supplied `ipsw dyld image` dependent blocks from
the iPhone X iOS 16.7.16 (20H392) donor SystemOS shared cache.

Project Sweet-10's target remains iPhone 7 `iPhone9,1` / D10AP /
A10-T8010. Every result below is donor-side static loader metadata, not an
iPhone 7 runtime measurement. The records do not prove a framework, service,
IOKit provider, or driver is available or compatible on the target.

All six commands reported exit status 0 in the supplied terminal output.
The pasted output showed no stderr lines, but the actual stderr files were
not provided for independent review.

## Summary

| Requested image | Regular dependencies | Weak-link entries | Other / unknown entries |
|---|---:|---:|---:|
| `BoardServices` | 6 | 0 | 0 |
| `BaseBoard` | 15 | 0 | 0 |
| `GraphicsServices` | 6 | 0 | 1 (`unknown 3`) |
| `RunningBoardServices` | 7 | 1 | 0 |
| `AssertionServices` | 5 | 1 | 0 |
| `IOSurface` | 5 | 0 | 0 |
| **Total** | **44** | **2** | **1** |

Do not recast the `unknown 3` entry as a regular dependency or re-export.
The supplied ipsw output does not explain that numeric kind. Preserve its
original classification until the encoding is independently verified.

## Ordered dependent records

### BoardServices

Six regular dependents, in printed order:

1. `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
2. `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`
3. `/System/Library/Frameworks/Foundation.framework/Foundation`
4. `/usr/lib/libobjc.A.dylib`
5. `/usr/lib/libSystem.B.dylib`
6. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

### BaseBoard

Fifteen regular dependents, in printed order:

1. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
2. `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`
3. `/System/Library/Frameworks/Foundation.framework/Foundation`
4. `/System/Library/Frameworks/ImageIO.framework/ImageIO`
5. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
6. `/System/Library/Frameworks/IOSurface.framework/IOSurface`
7. `/usr/lib/libbsm.0.dylib`
8. `/usr/lib/libicucore.A.dylib`
9. `/usr/lib/libMobileGestalt.dylib`
10. `/usr/lib/libsqlite3.dylib`
11. `/System/Library/PrivateFrameworks/ProtocolBuffer.framework/ProtocolBuffer`
12. `/System/Library/Frameworks/Security.framework/Security`
13. `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`
14. `/usr/lib/libobjc.A.dylib`
15. `/usr/lib/libSystem.B.dylib`

### GraphicsServices

One entry whose kind is reported as `unknown 3`:

- `/System/Library/PrivateFrameworks/FontServices.framework/libGSFont.dylib`

Six regular dependents, in printed order:

1. `/usr/lib/libobjc.A.dylib`
2. `/usr/lib/libMobileGestalt.dylib`
3. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
4. `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`
5. `/System/Library/Frameworks/Foundation.framework/Foundation`
6. `/usr/lib/libSystem.B.dylib`

### RunningBoardServices

Seven regular dependents, in printed order:

1. `/usr/lib/libbsm.0.dylib`
2. `/System/Library/Frameworks/Security.framework/Security`
3. `/System/Library/Frameworks/Foundation.framework/Foundation`
4. `/usr/lib/libobjc.A.dylib`
5. `/usr/lib/libSystem.B.dylib`
6. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
7. `/System/Library/Frameworks/CoreServices.framework/CoreServices`

One weak-link entry:

- `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`

### AssertionServices

Five regular dependents, in printed order:

1. `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`
2. `/System/Library/Frameworks/Foundation.framework/Foundation`
3. `/usr/lib/libobjc.A.dylib`
4. `/usr/lib/libSystem.B.dylib`
5. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

One weak-link entry:

- `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`

### IOSurface

Five regular dependents, in printed order:

1. `/System/Library/Frameworks/Foundation.framework/Foundation`
2. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
3. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
4. `/usr/lib/libSystem.B.dylib`
5. `/usr/lib/libobjc.A.dylib`

## Derived donor-side relationships

The newly supplied records add the following direct edges:

- `BoardServices` → `BaseBoard` (regular)
- `BaseBoard` → `IOSurface` (regular)
- `BaseBoard` → `IOKit` (regular)
- `BaseBoard` → `CoreGraphics` (regular)
- `GraphicsServices` → `FontServices/libGSFont.dylib` (kind unresolved; printed as `unknown 3`)
- `RunningBoardServices` → `BaseBoard` (weak link)
- `AssertionServices` → `RunningBoardServices` (regular)
- `AssertionServices` → `BaseBoard` (weak link)
- `IOSurface` → `IOKit` (regular)

The `BaseBoard` record has a broad set of dependencies spanning graphics,
I/O, image handling, security, protocol buffers, device gestalt, storage,
and common runtime libraries. This is a description of the donor-side load
metadata, not evidence that every subsystem is used by the Sweet-10 target.

## Interpretation limits

- The two weak-link entries explicitly name BaseBoard. Their weak-link status
  must be preserved; it does not mean the image is absent or that the weak
  dependency is necessarily required at runtime.
- The `unknown 3` row must remain unclassified pending a source-level mapping
  from dyld's dependency-kind encoding to ipsw's formatter.
- A framework dependency on IOKit does not identify a matching iPhone9,1
  kernel driver, IOKit personality, DeviceTree provider, interrupt, or register.
- These records are not observations of successful loading, process launch,
  or SpringBoard stability.
- The prior concern about implausible Swift/Objective-C section offsets
  remains separate and unresolved; those values are not used here.

## Next bounded inspection

The next read-only cache queries should focus on:

1. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
   — a shared dependency of BackBoard and BaseBoard, and the closest userland
   framework boundary to kernel I/O services. Its cache loader metadata still
   cannot prove target driver availability.
2. `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`
   — shared by BaseBoard and BackBoardServices, relevant to the graphics path.
3. `/System/Library/PrivateFrameworks/FontServices.framework/libGSFont.dylib`
   — the exact install name associated with the `unknown 3` row. Preserve
   the unknown type while checking whether ipsw can locate this image's loader.

See [the next service and graphics dependency inspection plan](20h392-service-graphics-dependency-plan.md)
for commands and graph-recording rules.

M6 remains in progress. M7 (SpringBoard on iPhone 7) has not started.

## References

- [Apple dyld4 design](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md)
- [ipsw dyld guide](https://blacktop.github.io/ipsw/docs/guides/dyld/)
- [20H392 split shared-cache inventory](20h392-dyld-cache-inventory.md)
- [BackBoard framework dependency results](20h392-backboard-framework-dependency-results.md)
