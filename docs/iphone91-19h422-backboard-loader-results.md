# iPhone9,1 / 19H422 BackBoard loader results

## Scope and input identity

This record documents one successful, read-only loader query against the iPhone 7 / iPhone9,1 / D10AP target-reference shared cache from iOS 15.8.8 build 19H422. The query used the standalone Linux IPSW executable version 3.1.749, build commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`, extracted locally from the official Linux x86_64 Debian package. The package SHA-256 was verified before extraction:

`333cab58451330f0080c3c2b7bec3d9e6f4be588b27f6213a5233dd08821d071`

The queried install name was:

`/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices`

The target cache is the existing host-side 19H422 cache at:

`$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`

No phone was connected to, booted, or modified. The physical iPhone 7 remains on iOS 12.1.4.

## Result

- Command exit status: **0**
- Standard error: empty
- Loader record: `prebuilt|in-cache-dylib|objc|never-unload`
- PrebuiltLoader reference index: **18**
- VM size: `0x865a8000`
- Region count: **5**
- Export trie: offset `0x003de6c8`, size `0x5268`
- Dependency rows: **12 regular**, **1 re-export**, **0 weak-link** in the supplied output
- BindTargets: no BindTargets section was printed in the supplied output; this record does not infer an empty bind-target set.

### Re-export

- `/System/Library/PrivateFrameworks/AssertionServices.framework/AssertionServices`

### Regular dependencies, in printed order

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

## Comparison with the recorded 20H392 donor

The corresponding iPhone X / iPhone10,3 / D22AP / 20H392 donor record in [20H392 BackBoard framework dependency results](20h392-backboard-framework-dependency-results.md) contains the same one AssertionServices re-export and the same twelve regular dependency install names in the same printed order. This is an exact match of the dependency names and printed kinds for this one framework loader record.

This agreement is useful static userland evidence, but it is not an ABI comparison and does not prove that the framework can load or run on iPhone9,1. The target and donor are different iOS releases and device identities.

## Parser caveat

The ipsw output printed implausible decoded Swift/Objective-C `Sections` offsets and sizes. Those fields are excluded from this audit and must not be used for file-range calculations, memory-layout claims, or binary-compatibility conclusions. The PrebuiltLoader reference index 18 is not a dyld-cache image-list index. No UUID or raw Mach-O comparison is claimed here.

## Audit status

This is the **first of the four planned target BackBoard framework queries** to return a successful record. Results for BackBoardHIDEventFoundation, BackBoardHIDEventProcessors, and IOMobileFramebuffer remain pending. M6 remains in progress; M7/SpringBoard has not started. Static loader metadata does not prove runtime loading, IOKit attachment, HID event delivery, display operation, or iPhone9,1 compatibility.
