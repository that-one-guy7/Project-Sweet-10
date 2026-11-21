# iPhone9,1 19H422 GUI-chain Mach-O dependency results

## Scope and provenance

This report records the user-supplied Ubuntu terminal output for the stock
iPhone 7 target reference, `iPhone9,1` / D10AP / A10-T8010 / iOS 15.8.8
build `19H422`. The physical phone remains on iOS 12.1.4.

The user reported:

- `file` at `/usr/bin/file`.
- `llvm-objdump` at `/usr/bin/llvm-objdump`.
- Ubuntu LLVM version `18.1.3`.
- All three commands exited with status 0 for each selected executable:
  `file`, `llvm-objdump --macho --dylibs-used`, and
  `llvm-objdump --macho --rpaths`.

The exact target paths were previously established by the completed
[Program-path presence report](launchd-program-path-presence-results.md).

## File identification

All three target executables were identified as:

`Mach-O 64-bit arm64 executable, flags:<NOUNDEFS|DYLDLINK|TWOLEVEL|PIE>`

| Executable | Direct dependency rows | Regular | Weak | Rpaths |
|---|---:|---:|---:|---|
| `/usr/libexec/backboardd` | 43 | 42 | 1 | none printed |
| `/usr/libexec/runningboardd` | 6 | 6 | 0 | none printed |
| `SpringBoard.app/SpringBoard` | 4 | 4 | 0 | `@executable_path/Frameworks` |

This establishes the file format and architecture string printed by `file`.
It does not establish a specific iOS minimum version, code-signing validity,
entitlements, ABI compatibility, dependency resolution, or runtime loadability.

## Target / donor comparison

The 20H392 donor executable output and loader audit are documented in
[the donor PrebuiltLoaderSet audit](20h392-prebuilt-loader-audit.md) and
[the iOS 16 userland launchd audit](ios16-userland-launchd-audit.md).

| Executable | 19H422 target | 20H392 donor | Direct-name comparison |
|---|---:|---:|---|
| `backboardd` regular | 42 | 45 | 42 shared; donor-only: 3 |
| `backboardd` weak | 1 named | 1 named in the donor Mach-O audit | `/usr/appleinternal/lib/liblinkguard.dylib` is named weak in both direct Mach-O inventories |
| `runningboardd` regular | 6 | 6 | Exact same six install names |
| `SpringBoard` regular | 4 | 4 | Exact same four install names |

The three donor-only **direct dependency edges** for `backboardd` are:

- `/System/Library/PrivateFrameworks/CarKit.framework/CarKit`
- `/System/Library/PrivateFrameworks/SystemWake.framework/SystemWake`
- `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`

The target's 42 regular `backboardd` install names are an exact set match to
the donor's 45 regular names after excluding those three donor-only edges.
The named weak `liblinkguard.dylib` appears in both direct Mach-O inventories.

**Weak-link caveat:** the separate donor `ipsw dyld image` PrebuiltLoaderSet
record reports an unnamed weak-link entry at index `32767` with text
`missing weak image`. That record does not expose its install name. Do not
claim that the unnamed PrebuiltLoaderSet marker is definitively the same row
as `liblinkguard.dylib`; retain these as separate evidence observations.

### runningboardd

Target and donor both report these six regular direct install names:

- `/System/Library/Frameworks/Foundation.framework/Foundation`
- `/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard`
- `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`
- `/usr/lib/libobjc.A.dylib`
- `/usr/lib/libSystem.B.dylib`
- `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

Both report no `LC_RPATH` rows.

### SpringBoard

Target and donor both report these four regular direct install names:

- `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard`
- `/System/Library/Frameworks/Foundation.framework/Foundation`
- `/usr/lib/libobjc.A.dylib`
- `/usr/lib/libSystem.B.dylib`

Both report the rpath `@executable_path/Frameworks`.

The rpath is a search-path declaration. It does not show that the directory
exists in the mounted target application bundle, or that any image is
successfully resolved from it.

## Complete target direct install-name lists

### backboardd — 42 regular rows

```text
/System/Library/PrivateFrameworks/StudyLog.framework/StudyLog
/System/Library/PrivateFrameworks/ButtonResolver.framework/ButtonResolver
/System/Library/PrivateFrameworks/Haptics.framework/Haptics
/System/Library/PrivateFrameworks/BiometricKit.framework/BiometricKit
/usr/lib/libsp.dylib
/System/Library/PrivateFrameworks/CrashReporterSupport.framework/CrashReporterSupport
/usr/lib/liblockdown.dylib
/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer
/System/Library/PrivateFrameworks/HangTracer.framework/HangTracer
/System/Library/PrivateFrameworks/WatchdogClient.framework/WatchdogClient
/System/Library/PrivateFrameworks/CoreAccessories.framework/CoreAccessories
/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices
/System/Library/Frameworks/QuartzCore.framework/QuartzCore
/System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation
/System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors
/System/Library/PrivateFrameworks/BoardServices.framework/BoardServices
/System/Library/Frameworks/Metal.framework/Metal
/System/Library/PrivateFrameworks/AggregateDictionary.framework/AggregateDictionary
/System/Library/Frameworks/AVFoundation.framework/AVFoundation
/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices
/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard
/System/Library/PrivateFrameworks/CoreBrightness.framework/CoreBrightness
/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics
/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics
/System/Library/Frameworks/CoreMotion.framework/CoreMotion
/System/Library/Frameworks/CoreText.framework/CoreText
/System/Library/PrivateFrameworks/DataMigration.framework/DataMigration
/System/Library/Frameworks/Foundation.framework/Foundation
/System/Library/PrivateFrameworks/GraphicsServices.framework/GraphicsServices
/System/Library/Frameworks/ImageIO.framework/ImageIO
/System/Library/Frameworks/CoreServices.framework/CoreServices
/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit
/System/Library/Frameworks/IOSurface.framework/IOSurface
/usr/lib/libAccessibility.dylib
/usr/lib/libMobileGestalt.dylib
/System/Library/PrivateFrameworks/ProgressUI.framework/ProgressUI
/System/Library/Frameworks/Security.framework/Security
/System/Library/Frameworks/SystemConfiguration.framework/SystemConfiguration
/usr/lib/libobjc.A.dylib
/usr/lib/libc++.1.dylib
/usr/lib/libSystem.B.dylib
/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation
```

One additional weak dependency:

```text
/usr/appleinternal/lib/liblinkguard.dylib
```

### runningboardd — 6 regular rows

```text
/System/Library/Frameworks/Foundation.framework/Foundation
/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard
/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices
/usr/lib/libobjc.A.dylib
/usr/lib/libSystem.B.dylib
/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation
```

### SpringBoard — 4 regular rows

```text
/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard
/System/Library/Frameworks/Foundation.framework/Foundation
/usr/lib/libobjc.A.dylib
/usr/lib/libSystem.B.dylib
```

The complete structured record is
[`research/iphone91-19h422-gui-macho-dependency-results.json`](../research/iphone91-19h422-gui-macho-dependency-results.json).

## Interpretation and next static evidence

The output confirms that the target 19H422 executables have ARM64 Mach-O
headers and records their direct link-command install names. The target
`runningboardd` and SpringBoard lists match the donor lists, and the target
`backboardd` differs by three donor-only regular dependency edges.

The next useful host-side check is to cross-reference each target install
name against the target 19H422 dyld cache image inventory and mounted
filesystem, with the SpringBoard app-local rpath checked separately. The
cache image inventory, standalone-file presence, and direct dependency graph
must remain separate evidence categories. For any unresolved dependency,
record whether it is present in the target cache image list, on the mounted
filesystem, or neither in the inspected sources; do not infer runtime
resolution from names alone.

## Evidence boundary

These are direct Mach-O load-command observations, not a recursive dependency
closure. The `arm64` architecture label does not establish that an iOS 16
donor binary or framework is ABI-compatible with the target system.

The 19H422 target is an iOS 15.8.8 stock iPhone 7 reference; 20H392 is an
iOS 16.7.16 iPhone X donor. Similar install names or identical dependency
sets do not establish iOS 16 userland compatibility, launchd execution,
IOKit provider attachment, hardware support, successful process launch, or
SpringBoard readiness. No target executable was run. No device, firmware,
partition, activation, security, or boot state was accessed or changed.
