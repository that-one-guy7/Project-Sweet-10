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

The visible excerpt lists these regular dependent install names:

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

The same excerpt includes one weak-link record reported as
index 32767 (missing weak image). This is recorded as a weak-linked image
entry in the donor loader metadata. Its absence must not be generalized into
a claim that an ordinary required dependency is missing; the exact weak
install name and any runtime symbol use have not been established here.

**Completeness note:** the captured backboardd text was limited to the first
60 lines by the inspection command. The 21 regular paths above are the entries
visible in that excerpt, not a verified complete dependent list. Do not treat
this list as a final count.

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
- That the visible backboardd list is complete.
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
