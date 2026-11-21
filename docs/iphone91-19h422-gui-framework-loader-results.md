# iPhone9,1 / 19H422 SpringBoard and RunningBoard framework loader results

## Scope and input identity

This is a read-only record of three user-supplied `ipsw dyld image` outputs from the iPhone 7 / `iPhone9,1` / D10AP target-reference SystemOS shared cache for iOS 15.8.8 build 19H422.

The SpringBoard path queried here is `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard`. It is the private framework binary, not the separate `/System/Library/CoreServices/SpringBoard.app/SpringBoard` application executable recorded in the donor executable audit. Keep those image identities distinct.

The standalone IPSW version file identifies:

- Version: `3.1.749`
- Build commit: `a7dfadbcaca8375b424c12a68dae40767e5e07c1`
- Executable: `/home/hey/ipsw-standalone/ipsw`

The physical iPhone 7 remains on iOS 12.1.4. These are host-side cache metadata observations only; no device state was accessed or changed.

The first supplied `status.tsv` copy was empty. The user subsequently located the completed status listing and supplied these exact rows: all three requested image queries exited with status `0`. The successful statuses are therefore confirmed for SpringBoard.framework, RunningBoard, and RunningBoardServices.

## Loader summary

| Requested image | PrebuiltLoader reference index | Target cache image-list index | VM size | Regions | Loader flags |
|---|---:|---:|---:|---:|---|
| SpringBoard.framework / SpringBoard | 453 | 454 | `0x5923c000` | 5 | `prebuilt|in-cache-dylib|objc|+load|never-unload` |
| RunningBoardServices | 61 | 62 | `0x7fbac000` | 5 | `prebuilt|in-cache-dylib|objc|never-unload` |
| RunningBoard | 552 | 553 | `0x52358000` | 5 | `prebuilt|in-cache-dylib|objc|never-unload` |

The cache image-list indexes (454, 62, and 553) come from the earlier target cache inventory. The PrebuiltLoader reference indexes (453, 61, and 552) come from the newly supplied loader output. They are distinct identifiers and must not be substituted for one another. Their one-number difference in these three observations is recorded, not generalized into an indexing rule.

SpringBoard's loader record additionally prints `Info: initializers|regions=5` and the `+load` flag. This is metadata in the returned record; it does not establish that an Objective-C initializer ran.

## Direct dependent rows

The following counts are from the supplied Dependents blocks and preserve regular and weak-link rows as separate types.

No `BindTargets` block appears in the supplied three outputs. This report does not infer that any of the three records has an empty BindTargets set.

The recovered `status.tsv` confirms exit status `0` for all three requested images:

```text
/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard\t0
/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard\t0
/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices\t0
```

| Requested image | Regular rows | Weak-link rows | Total rows |
|---|---:|---:|---:|
| SpringBoard.framework / SpringBoard | 198 | 10 | 208 |
| RunningBoardServices | 7 | 1 | 8 |
| RunningBoard | 15 | 5 | 20 |
| **Total** | **220** | **16** | **236** |

### SpringBoard.framework / SpringBoard

The record includes direct regular dependencies relevant to the GUI chain, including:

- `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices`
- `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`
- `/System/Library/PrivateFrameworks/FrontBoard.framework/FrontBoard`
- `/System/Library/PrivateFrameworks/FrontBoardServices.framework/FrontBoardServices`
- `/System/Library/PrivateFrameworks/SpringBoardServices.framework/SpringBoardServices`
- `/System/Library/PrivateFrameworks/SpringBoardHome.framework/SpringBoardHome`
- `/System/Library/PrivateFrameworks/SpringBoardFoundation.framework/SpringBoardFoundation`
- `/System/Library/PrivateFrameworks/SpringBoardUIServices.framework/SpringBoardUIServices`
- `/System/Library/PrivateFrameworks/SpringBoardUI.framework/SpringBoardUI`
- `/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport`
- `/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer`
- `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
- `/System/Library/Frameworks/IOSurface.framework/IOSurface`
- `/System/Library/Frameworks/UIKit.framework/UIKit`
- `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics`

The ten weak-link rows are:

1. `/usr/lib/liblockdown.dylib`
2. `/usr/lib/libAccessibility.dylib`
3. `/usr/lib/libSystem.B.dylib`
4. `/System/Library/Frameworks/Contacts.framework/Contacts`
5. `/System/Library/Frameworks/ContactsUI.framework/ContactsUI`
6. `/System/Library/Frameworks/CoreMedia.framework/CoreMedia`
7. `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
8. `/usr/lib/libutil.dylib`
9. `/System/Library/PrivateFrameworks/SiriUI.framework/SiriUI`
10. `/usr/lib/libobjc.A.dylib`

The record also names a wide range of other system frameworks and services, including connectivity, notifications, media, account, application-installation, and analytics components. This is a large direct-dependency list, not a recursively resolved dependency closure.

### RunningBoardServices

Seven regular dependencies, as shown in the supplied block:

- `/usr/lib/libbsm.0.dylib`
- `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard`
- `/System/Library/Frameworks/Foundation.framework/Foundation`
- `/usr/lib/libobjc.A.dylib`
- `/usr/lib/libSystem.B.dylib`
- `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
- `/System/Library/Frameworks/CoreServices.framework/CoreServices`

One weak-link row:

- `/System/Library/Frameworks/Security.framework/Security`

### RunningBoard

Fifteen regular dependencies, as shown in the supplied block:

- `/System/Library/PrivateFrameworks/AppServerSupport.framework/AppServerSupport`
- `/System/Library/Frameworks/CoreServices.framework/CoreServices`
- `/System/Library/PrivateFrameworks/PowerLog.framework/PowerLog`
- `/System/Library/PrivateFrameworks/WatchdogClient.framework/WatchdogClient`
- `/System/Library/PrivateFrameworks/UserManagement.framework/UserManagement`
- `/usr/lib/libbsm.0.dylib`
- `/usr/lib/libsqlite3.dylib`
- `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
- `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`
- `/System/Library/Frameworks/Security.framework/Security`
- `/System/Library/Frameworks/Foundation.framework/Foundation`
- `/usr/lib/libobjc.A.dylib`
- `/usr/lib/libSystem.B.dylib`
- `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
- `/System/Library/PrivateFrameworks/OSAnalytics.framework/OSAnalytics`

Five weak-link rows:

1. `/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU`
2. `/System/Library/PrivateFrameworks/CrashReporterSupport.framework/CrashReporterSupport`
3. `/usr/lib/libsp.dylib`
4. `/System/Library/PrivateFrameworks/PlugInKit.framework/PlugInKit`
5. `/usr/lib/libtailspin.dylib`

## Parser caveat: Sections

All three reports contain implausible values in the decoded `Sections` table. For example, several reported offsets decode to ASCII-like fragments of install-name strings rather than plausible section offsets. The reported values are not accepted as valid Swift or Objective-C section metadata in this audit.

Do not use these section offsets or sizes for file-range calculations, memory-layout analysis, or compatibility conclusions. The exact parser/format cause has not been isolated. The dependent install-name rows above are retained as provisional static observations, but they also require independent parser validation before being treated as definitive loader behavior.

## Comparison with the 20H392 donor

Matching framework loader records have now been captured from the iPhone X
20H392 donor cache for all three exact install names. All three donor queries
exited with status 0. See
[the comparative report](20h392-19h422-gui-framework-loader-comparison-results.md)
and its [machine-readable data](../research/20h392-19h422-gui-framework-loader-comparison.json).

At summary level:

- SpringBoard.framework reports 198 regular and 10 weak-link rows in each
  cache; the ten weak-link install names match. This does not prove the full
  regular path sets are identical.
- RunningBoard has 20 shared install names, two donor-only names, and three
  shared paths whose regular/weak-link kinds change.
- RunningBoardServices has the same eight install names in both caches,
  with Security and BaseBoard switching edge kinds.

The two caches' PrebuiltLoader reference indexes are distinct from their
cache image-list indexes. The comparison preserves that distinction and
excludes the malformed `Sections` fields.

## What this establishes—and what it does not

Established from the supplied 19H422 cache output:

- The parser returned loader records for the three requested in-cache framework images.
- Their records report the PrebuiltLoader reference indexes, VM sizes, region counts, flags, and direct dependent rows documented above.
- The SpringBoard.framework record includes the `+load` and `initializers` metadata flags.
- The selected framework records expose a broad direct GUI dependency layer beneath the SpringBoard / RunningBoard subsystem.

Not established:

- The query exit statuses; the subsequently located `status.tsv` confirms all three are `0`.
- That the suspicious `Sections` offsets and sizes are decoded correctly.
- That each dependency is resolvable for a particular process or recursively available.
- That any framework or executable launches successfully.
- That the device has matching IOKit providers, display/input hardware support, entitlements, launchd endpoints, or service implementations.
- That iOS 16.7.16 (20H392) userland can run on the iPhone 7 A10/T8010 target.
- That SpringBoard is ready or has run on the target.

The target reference is stock iOS 15.8.8 build 19H422, not the intended iOS 16 userland. M6 remains in progress and M7 (SpringBoard on the iPhone 7 target) has not started. The physical iPhone 7 remains on iOS 12.1.4; no device or firmware state was changed.

## Next bounded host-side work

1. Cross-reference the complete dependent-path sets against the target 19H422 cache image inventory and mounted filesystem, keeping cache membership separate from filesystem presence.
2. Collect matching 20H392 PrebuiltLoader records for SpringBoard.framework, RunningBoard, and RunningBoardServices before making a donor comparison.
3. Validate the malformed section output with an independent parser before relying on section metadata.

All next steps remain host-side static inspection. No device boot, restore, partition write, or firmware change is part of this audit.
