# iOS 20H392 BackBoard framework dependency results

## Scope

This is a read-only record of user-supplied `ipsw dyld image` output from the
iPhone X iOS 16.7.16 (20H392) donor SystemOS shared cache.

Project Sweet-10's actual target remains iPhone 7 `iPhone9,1` / D10AP /
A10-T8010. These are donor-cache loader records only. They do not demonstrate
that these frameworks, services, IOKit providers, or hardware drivers are
available or compatible on iPhone9,1.

The user ran each query with ipsw 3.1.749 against the previously identified
split SystemOS cache. All four commands exited with status 0. The captured
stderr files printed no error text in the supplied terminal output.

## Observed dependent-loader entries

| Requested image | Regular dependencies | Re-export entries | Weak-link entries |
|---|---:|---:|---:|
| `BackBoardHIDEventFoundation` | 10 | 0 | 0 |
| `BackBoardHIDEventProcessors` | 9 | 0 | 0 |
| `BackBoardServices` | 12 | 1 | 0 |
| `IOMobileFramebuffer` | 4 | 0 | 0 |
| **Total rows** | **35** | **1** | **0** |

The counts preserve the kind printed by ipsw. In particular, the
`AssertionServices` entry from BackBoardServices is a `re-export`, not a
regular dependent row. No weak-link entries appeared in the four supplied
blocks.

### BackBoardHIDEventFoundation

Ten regular dependents, in printed order:

1. `/System/Library/PrivateFrameworks/StudyLog.framework/StudyLog`
2. `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices`
3. `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
4. `/System/Library/PrivateFrameworks/BoardServices.framework/BoardServices`
5. `/System/Library/PrivateFrameworks/GraphicsServices.framework/GraphicsServices`
6. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
7. `/System/Library/Frameworks/Foundation.framework/Foundation`
8. `/usr/lib/libobjc.A.dylib`
9. `/usr/lib/libSystem.B.dylib`
10. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

### BackBoardHIDEventProcessors

Nine regular dependents, in printed order:

1. `/System/Library/PrivateFrameworks/StudyLog.framework/StudyLog`
2. `/System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation`
3. `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices`
4. `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
5. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
6. `/System/Library/Frameworks/Foundation.framework/Foundation`
7. `/usr/lib/libobjc.A.dylib`
8. `/usr/lib/libSystem.B.dylib`
9. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

### BackBoardServices

One re-export entry:

- `/System/Library/PrivateFrameworks/AssertionServices.framework/AssertionServices`

Twelve regular dependents, in printed order:

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

Four regular dependents, in printed order:

1. `/System/Library/Frameworks/IOSurface.framework/IOSurface`
2. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
3. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
4. `/usr/lib/libSystem.B.dylib`

## Derived donor-side relationships

The newly inspected rows establish these direct edges in the donor loader
metadata:

- `BackBoardHIDEventProcessors` → `BackBoardHIDEventFoundation`
- `BackBoardHIDEventFoundation` → `BackBoardServices`
- `BackBoardHIDEventProcessors` → `BackBoardServices`
- `BackBoardHIDEventFoundation` → `IOKit`
- `BackBoardHIDEventProcessors` → `IOKit`
- `BackBoardServices` → `IOKit`
- `IOMobileFramebuffer` → `IOSurface`
- `IOMobileFramebuffer` → `IOKit`
- `BackBoardServices` → `AssertionServices` as a re-export

The two HID framework records share several donor dependencies, including
StudyLog, BackBoardServices, BaseBoard, IOKit, Foundation, libobjc, libSystem,
and CoreFoundation. BackBoardHIDEventFoundation additionally names
BoardServices and GraphicsServices. BackBoardHIDEventProcessors names
BackBoardHIDEventFoundation itself.

These are install-name relationships reported by the donor cache. They do
not identify which APIs are actually used, the clients of each service, the
kernel-side provider implementation, or whether an image loads successfully
on a different device.

## Interpretation

- The four requested paths were accepted by ipsw and each query returned
  status 0.
- The reported dependent rows provide one static dependency layer below
  four backboardd dependencies.
- The BackBoardServices re-export must remain separately typed; it is not
  counted as a regular dependency.
- No weak-link rows were printed for these four framework records.
- A dependency on IOKit or IOSurface is not proof of an iPhone9,1 display or
  HID provider, driver, DeviceTree node, or hardware resource.
- This output is not a recursive closure for every framework. Frameworks
  named in these lists need their own loader inspection before further
  dependency edges are asserted.
- The earlier suspicious Swift/Objective-C section offsets remain excluded
  pending independent parser validation.

## Next bounded inspection

The new edges point to a manageable next set of framework-level records:
`BoardServices`, `BaseBoard`, `GraphicsServices`,
`RunningBoardServices`, `AssertionServices`, and `IOSurface`.
`IOKit`, `Foundation`, and `CoreFoundation` are additional large shared
dependencies; inspect them only as needed to answer a specific question rather
than expanding every framework indiscriminately.

After the donor graph is extended, compare relevant requirements with
iPhone9,1-specific public firmware and XNU evidence. Keep each observation
classified as target-confirmed, donor-reference-only, missing, or unverified.
M6 remains in progress; M7 (SpringBoard on the iPhone 7) has not started.

## References

- [Apple dyld4 design](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md)
- [ipsw dyld guide](https://blacktop.github.io/ipsw/docs/guides/dyld/)
- [20H392 split dyld shared-cache inventory](20h392-dyld-cache-inventory.md)
- [20H392 PrebuiltLoaderSet audit](20h-prebuilt-loader-audit.md)
- [BackBoard framework dependency expansion plan](20h392-backboard-framework-dependency-expansion.md)
