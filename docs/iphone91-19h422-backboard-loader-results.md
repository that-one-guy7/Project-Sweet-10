# iPhone9,1 / 19H422 BackBoard loader results

## Scope and input identity

This is the completed read-only collection of four PrebuiltLoader records from the iPhone 7 / iPhone9,1 / D10AP target-reference shared cache for iOS 15.8.8 build 19H422. The records were queried with standalone Linux IPSW 3.1.749, build commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`, extracted from the official Linux x86_64 Debian package. The package SHA-256 was verified before extraction:

`333cab58451330f0080c3c2b7bec3d9e6f4be588b27f6213a5233dd08821d071`

The target cache path was:

`$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`

The donor comparison uses the previously recorded iPhone X / iPhone10,3 / D22AP / iOS 16.7.16 build 20H392 results in [20H392 BackBoard framework dependency results](20h392-backboard-framework-dependency-results.md). These are different iOS releases and different device identities; dependency differences must not be attributed to A10 hardware without separate evidence.

The physical iPhone 7 remains on iOS 12.1.4. All work described here was performed against host-side files only; no phone was connected to, booted, or modified.

## Target loader summary

| Target image | PrebuiltLoader ref index | VM size | Regions | Regular dependencies | Re-exports | Weak links | Supplied query status |
|---|---:|---:|---:|---:|---:|---:|---|
| BackBoardHIDEventFoundation | 587 | `0x50ae4000` | 5 | 9 | 0 | 0 | Loader record returned; stderr empty; explicit exit-status line not present in supplied excerpt |
| BackBoardHIDEventProcessors | 933 | `0x442b8000` | 5 | 8 | 0 | 0 | 0 |
| BackBoardServices | 18 | `0x865a8000` | 5 | 12 | 1 | 0 | 0 |
| IOMobileFramebuffer | 308 | `0x6096c000` | 5 | 4 | 0 | 0 | 0 |
| **Total** | — | — | **20** | **33** | **1** | **0** | Four records returned |

All four outputs identify prebuilt in-cache dylib loader records. The three HID / BackBoard records also print `objc`; IOMobileFramebuffer does not. No BindTargets section was printed in the supplied outputs, so this document does not infer an empty BindTargets set.

### BackBoardHIDEventFoundation

- Install name: `/System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation`
- Loader flags: `prebuilt|in-cache-dylib|objc|never-unload`
- PrebuiltLoader reference index: **587**
- VM size: `0x50ae4000`; regions: **5**
- Export trie: offset `0x015f1e98`, size `0x8f0`
- Nine regular dependencies, in printed order:

1. `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices`
2. `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
3. `/System/Library/PrivateFrameworks/BoardServices.framework/BoardServices`
4. `/System/Library/PrivateFrameworks/GraphicsServices.framework/GraphicsServices`
5. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
6. `/System/Library/Frameworks/Foundation.framework/Foundation`
7. `/usr/lib/libobjc.A.dylib`
8. `/usr/lib/libSystem.B.dylib`
9. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

The supplied excerpt showed an empty stderr section but did not include the explicit exit-status line for this first query. The loader record itself was returned and is documented; the missing status is left unasserted.

### BackBoardHIDEventProcessors

- Install name: `/System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors`
- Loader flags: `prebuilt|in-cache-dylib|objc|never-unload`
- PrebuiltLoader reference index: **933**
- VM size: `0x442b8000`; regions: **5**
- Export trie: offset `0x019e21e8`, size `0x378`
- Query exit status: **0**; stderr empty
- Eight regular dependencies, in printed order:

1. `/System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation`
2. `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices`
3. `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
4. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
5. `/System/Library/Frameworks/Foundation.framework/Foundation`
6. `/usr/lib/libobjc.A.dylib`
7. `/usr/lib/libSystem.B.dylib`
8. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

### BackBoardServices

- Install name: `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices`
- Loader flags: `prebuilt|in-cache-dylib|objc|never-unload`
- PrebuiltLoader reference index: **18**
- VM size: `0x865a8000`; regions: **5**
- Export trie: offset `0x003de6c8`, size `0x5268`
- Query exit status: **0**; stderr empty
- One re-export:

  - `/System/Library/PrivateFrameworks/AssertionServices.framework/AssertionServices`

- Twelve regular dependencies, in printed order:

1. `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`
2. `/System/Library/PrivateFrameworks/BoardServices.framework/BoardServices`
3. `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
4. `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`
5. `/System/Library/Frameworks/Foundation.framework/Foundation`
6. `/System/Library/PrivateFrameworks/GraphicsServices.framework/GraphicsServices`
7. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
8. `/usr/lib/libMobileGestalt.dylib`
9. `/usr/lib/libobjc.A.dylib`
10. `/usr/lib/libSystem.B.dylib`
11. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
12. `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`

### IOMobileFramebuffer

- Install name: `/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer`
- Loader flags: `prebuilt|in-cache-dylib|never-unload`
- PrebuiltLoader reference index: **308**
- VM size: `0x6096c000`; regions: **5**
- Export trie: offset `0x010bc0b8`, size `0xbf8`
- Query exit status: **0**; stderr empty
- Four regular dependencies, in printed order:

1. `/System/Library/Frameworks/IOSurface.framework/IOSurface`
2. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
3. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
4. `/usr/lib/libSystem.B.dylib`

## Exact comparison with the 20H392 donor

| Framework | 20H392 donor regular | 19H422 target regular | Re-export rows (donor / target) | Difference |
|---|---:|---:|---:|---|
| BackBoardHIDEventFoundation | 10 | 9 | 0 / 0 | Donor-only `StudyLog` |
| BackBoardHIDEventProcessors | 9 | 8 | 0 / 0 | Donor-only `StudyLog` |
| BackBoardServices | 12 | 12 | 1 / 1 | Exact dependency-name and kind match |
| IOMobileFramebuffer | 4 | 4 | 0 / 0 | Exact dependency-name and kind match |
| **Total** | **35** | **33** | **1 / 1** | Two donor-only dependency occurrences |

Detailed set comparison:

- `BackBoardHIDEventFoundation`: the target's nine regular dependency names match nine donor names. The donor additionally lists `/System/Library/PrivateFrameworks/StudyLog.framework/StudyLog`.
- `BackBoardHIDEventProcessors`: the target's eight regular dependency names match eight donor names. The donor additionally lists `/System/Library/PrivateFrameworks/StudyLog.framework/StudyLog`.
- `BackBoardServices`: all twelve regular dependency names and the AssertionServices re-export match the donor record, including printed order and kind.
- `IOMobileFramebuffer`: all four regular dependency names match the donor record, including printed order.

There are **no target-only dependency rows** among these four records. The only distinct donor-only install name is StudyLog, occurring as a dependency edge in both HID framework records. No weak-link entries were printed for either side.

The donor and target use different OS builds (20H392 / iOS 16.7.16 versus 19H422 / iOS 15.8.8) and different devices (iPhone10,3 versus iPhone9,1). The two StudyLog edge differences may be release-related; this comparison does not establish why they differ and does not prove a hardware compatibility issue.

## Parser and interpretation caveats

The ipsw output prints implausible decoded Swift/Objective-C `Sections` offsets and sizes. Those fields are excluded from this audit and must not be used for file-range calculations, memory-layout claims, or binary-compatibility conclusions.

PrebuiltLoader reference indexes (587, 933, 18, 308) are loader-table references, not dyld-cache image-list indexes. No UUID or raw Mach-O comparison is claimed here. No BindTargets section was printed; no empty set is inferred.

A static loader record shows that the parser found a loader entry in the cache. It does not prove that the framework loads at runtime, that its APIs are ABI-compatible, that an IOKit provider attaches, that HID events are delivered, that the display operates, or that iPhone9,1 can run the 20H392 userland.

## Status

The planned four-framework target-side BackBoard collection and direct donor comparison are **complete**. This closes this bounded M6 subtask only. M6 remains in progress for the broader userland audit; M7/SpringBoard has not started. The physical iPhone 7 remains on iOS 12.1.4, with no device or firmware state changed.
