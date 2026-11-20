# iOS 20H392 dyld PrebuiltLoaderSet records

## Scope

This is a read-only analysis of three executable loader records in the iPhone X
iOS 16.7.16 (20H392) donor SystemOS shared cache. The physical Project Sweet-10
target remains iPhone 7, iPhone9,1 / D10AP / A10-T8010. None of these records
is an iPhone 7 runtime observation.

The user inspected the cache with ipsw 3.1.749. For each executable, the
ipsw dyld image command exited 0. The cache path and split-cache identity are
recorded in [the cache inventory](20h392-dyld-cache-inventory.md).

Apple's dyld4 documentation describes a PrebuiltLoader as read-only
precomputed Mach-O metadata containing its path, validation information,
dependent dylibs, and precomputed bind targets. A PrebuiltLoaderSet groups
these records. The ipsw dyld guide documents that modern iOS caches use
prebuilt loader sets and that ipsw dyld image displays loader/image
information. See [Apple dyld4 documentation](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md)
and the [ipsw dyld guide](https://blacktop.github.io/ipsw/docs/guides/dyld/).

## Observed loader records

All three outputs begin with:

- PrebuiltLoaderSet version: 4d2b8647
- Loader flags: prebuilt|objc|ro-data|never-unload|pre-2022
- Loader reference: index 0
- Loader type: app

| Executable | Reported VM Size | Reported regions | Reported loader type |
|---|---:|---:|---|
| /usr/libexec/backboardd | 0x124000 | 5 | app |
| /usr/libexec/runningboardd | 0x14000 | 5 | app |
| /System/Library/CoreServices/SpringBoard.app/SpringBoard | 0x1c000 | 4 | app |

These are fields reported by ipsw for the donor's prebuilt loader records. They
are not runtime memory measurements from iPhone9,1.

## Direct dependent-loader records

### backboardd

The complete Dependents block supplied by the user contains **45 regular
dependent install names** in the order shown below:

1. /System/Library/PrivateFrameworks/StudyLog.framework/StudyLog
2. /System/Library/PrivateFrameworks/ButtonResolver.framework/ButtonResolver
3. /System/Library/PrivateFrameworks/Haptics.framework/Haptics
4. /System/Library/PrivateFrameworks/BiometricKit.framework/BiometricKit
5. /System/Library/PrivateFrameworks/CarKit.framework/CarKit
6. /usr/lib/libsp.dylib
7. /System/Library/PrivateFrameworks/CrashReporterSupport.framework/CrashReporterSupport
8. /usr/lib/liblockdown.dylib
9. /System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer
10. /System/Library/PrivateFrameworks/HangTracer.framework/HangTracer
11. /System/Library/PrivateFrameworks/WatchdogClient.framework/WatchdogClient
12. /System/Library/PrivateFrameworks/CoreAccessories.framework/CoreAccessories
13. /System/Library/PrivateFrameworks/SystemWake.framework/SystemWake
14. /System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices
15. /System/Library/Frameworks/QuartzCore.framework/QuartzCore
16. /System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation
17. /System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors
18. /System/Library/PrivateFrameworks/BoardServices.framework/BoardServices
19. /System/Library/Frameworks/Metal.framework/Metal
20. /System/Library/PrivateFrameworks/AggregateDictionary.framework/AggregateDictionary
21. /System/Library/Frameworks/AVFoundation.framework/AVFoundation
22. /System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices
23. /System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard
24. /System/Library/PrivateFrameworks/CoreBrightness.framework/CoreBrightness
25. /System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics
26. /System/Library/Frameworks/CoreGraphics.framework/CoreGraphics
27. /System/Library/Frameworks/CoreMotion.framework/CoreMotion
28. /System/Library/Frameworks/CoreText.framework/CoreText
29. /System/Library/PrivateFrameworks/DataMigration.framework/DataMigration
30. /System/Library/Frameworks/Foundation.framework/Foundation
31. /System/Library/PrivateFrameworks/GraphicsServices.framework/GraphicsServices
32. /System/Library/Frameworks/ImageIO.framework/ImageIO
33. /System/Library/Frameworks/CoreServices.framework/CoreServices
34. /System/Library/Frameworks/IOKit.framework/Versions/A/IOKit
35. /System/Library/Frameworks/IOSurface.framework/IOSurface
36. /usr/lib/libAccessibility.dylib
37. /usr/lib/libMobileGestalt.dylib
38. /System/Library/PrivateFrameworks/ProgressUI.framework/ProgressUI
39. /System/Library/Frameworks/Security.framework/Security
40. /System/Library/Frameworks/SystemConfiguration.framework/SystemConfiguration
41. /usr/lib/libobjc.A.dylib
42. /usr/lib/libc++.1.dylib
43. /usr/lib/libSystem.B.dylib
44. /System/Library/Frameworks/CoreFoundation.framework/CoreFoundation
45. /System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking

The same block contains one weak-link record:

`weak-link ) index: 32767 (missing weak image)`

The output does not expose an install name for that weak-link index, so this
audit leaves its identity unresolved. Do not treat the weak-link marker as a
missing regular dependency or infer which library it represents without
additional evidence.

The full Dependents block was subsequently supplied, so this list is no
longer limited to the earlier first-60-lines terminal excerpt. There are 45
regular install names plus one weak-link record in the supplied block.
### runningboardd

The supplied output shows six regular dependent install names:

- /System/Library/Frameworks/Foundation.framework/Foundation
- /System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard
- /System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices
- /usr/lib/libobjc.A.dylib
- /usr/lib/libSystem.B.dylib
- /System/Library/Frameworks/CoreFoundation.framework/CoreFoundation

The output also reports bind targets to CoreFoundation, libobjc, and
RunningBoard. These are precomputed binding records in the donor loader
metadata, not proof that the target provides equivalent runtime interfaces.

### SpringBoard

The supplied output shows four regular dependent install names:

- /System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard
- /System/Library/Frameworks/Foundation.framework/Foundation
- /usr/lib/libobjc.A.dylib
- /usr/lib/libSystem.B.dylib

The output reports one bind target to SpringBoard.framework. The executable's
short direct list does not describe the full dependency tree: SpringBoard's
framework has its own dependencies, and additional frameworks/services may be
loaded through other mechanisms.

## Parser caveat: section offsets

The output's Sections block contains implausible values for a number of
Swift and Objective-C section offsets and sizes (including values far outside
the executable's reported VM Size). Those fields are not accepted as valid
section metadata in this audit. They may reflect a parser/format interpretation
problem for this record type or cache version; the cause has not yet been
isolated.

For now, use the dependent install names and bind-target records only as
provisional static evidence. Do not use the suspicious section offsets to
calculate file ranges, map executable data, or infer runtime layout. A future
validation should compare the ipsw output with the exact loader record format
and an independent Mach-O/cache parser before relying on those fields.

## What this establishes—and what it does not

Established for the iPhone X donor cache:

- The selected cache contains prebuilt loader records for the three named
  GUI-chain executables.
- The records contain dependent install names and, for the supplied
  runningboardd and SpringBoard output, precomputed bind-target entries.
- The donor's backboardd record references HID event, framebuffer, graphics,
  haptics, biometric, accessory, watchdog, and other system frameworks.
- The donor's SpringBoard executable directly names SpringBoard.framework,
  Foundation, libobjc, and libSystem.

Not established:

- That any of these executables was run or launched successfully.
- That these dependencies are all available in the same form on iPhone9,1.
- That the iPhone 7 has matching IOKit providers, framebuffer/HID services,
  entitlements, launchd endpoints, or hardware implementations.
- That the weak-link index resolves to a particular install name or is used at runtime.
- That the suspect section metadata is correctly decoded.
- That the 20H392 donor userland can be used unchanged on an A10/T8010 device.

This is static donor evidence only. M6 remains in progress and M7 (SpringBoard
on the iPhone 7 target) has not started. The iPhone 7 remains on its existing
iOS 12.1.4 installation; no target firmware or device state was changed.

## Next host-side evidence

The next useful static step is to inspect the loader records for the major
frameworks named by backboardd and SpringBoard, then build a recursive graph
with each node classified as cache-resident, on-disk, app-bundle, weak-linked,
or unresolved. The graph must keep donor-only dependencies separate from
iPhone9,1 target evidence. Embedded XPC services and IOKit personality/provider
requirements remain separate follow-up work.


## Repeatable next collection pass

The priority framework list and a read-only host-side capture helper are now
specified in [the recursive loader collection note](20h392-recursive-loader-collection.md).
The helper saves ipsw output verbatim for the HID/display, graphics,
process-coordination, and core-runtime framework records. Its output must
still be reviewed and converted into a graph; no recursive edges are claimed
until those actual records have been collected. Failed image lookups remain
unresolved rather than being classified as missing dependencies.
