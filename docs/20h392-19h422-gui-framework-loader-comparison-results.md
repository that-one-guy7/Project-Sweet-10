# 20H392 / 19H422 GUI framework PrebuiltLoader comparison

## Scope and input identity

This report records the three user-supplied iPhone X iOS 16.7.16 (20H392)
donor `ipsw dyld image` outputs and compares them with the previously recorded
iPhone 7 iOS 15.8.8 (19H422) target-reference cache outputs.

The same three install names were queried in both caches:
SpringBoard.framework, RunningBoard, and RunningBoardServices. All three
20H392 donor queries exited with status `0`. The collector was IPSW 3.1.749,
build commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`, invoked only as
`/home/hey/ipsw-standalone/ipsw`.

The machine-readable comparison is in
[`research/20h392-19h422-gui-framework-loader-comparison.json`](../research/20h392-19h422-gui-framework-loader-comparison.json).

## Loader summary

| Image | 19H422 loader ref | 20H392 loader ref | 19H422 VM size | 20H392 VM size |
|---|---:|---:|---:|---:|
| SpringBoard.framework / SpringBoard | 453 | 637 | `0x5923c000` | `0x6561c000` |
| RunningBoard | 552 | 1673 | `0x52358000` | `0x34f6c000` |
| RunningBoardServices | 61 | 84 | `0x7fbac000` | `0x97678000` |

The target's cache image-list indexes (454, 553, and 62) are different
identifiers from the PrebuiltLoader reference indexes. Do not compare those
index classes or treat the PrebuiltLoader indexes as stable cross-build IDs.

Each donor record reports five regions and adds the literal loader flags
`ro-objc|pre-2022`; RunningBoard and RunningBoardServices also report
`overridable`. SpringBoard reports `+load` and `initializers` in both
records. These strings are metadata only; no runtime meaning is inferred.

## RunningBoard

The target record has 15 regular and 5 weak-link rows (20 total). The donor
has 15 regular and 7 weak-link rows (22 total). All 20 target install names
also appear in the donor record.

**Donor-only rows:**

| Install name | Donor kind | Target image-list cross-reference |
|---|---|---|
| `/System/Library/Frameworks/ExtensionFoundation.framework/ExtensionFoundation` | regular | No exact path. A same-basename image is listed at `/System/Library/PrivateFrameworks/ExtensionFoundation.framework/ExtensionFoundation`, index 1093, version `51.6.0.0.0`, UUID `2440EEE5-9988-368C-A583-90353581845C`. |
| `/System/Library/PrivateFrameworks/PrivacyDisclosureCore.framework/PrivacyDisclosureCore` | weak-link | No same-basename image record in the 2,407-entry target cache image list. |

**Three shared paths change edge kind:**

| Install name | 19H422 kind | 20H392 kind |
|---|---|---|
| `PowerLog.framework/PowerLog` | regular | weak-link |
| `UserManagement.framework/UserManagement` | regular | weak-link |
| `PlugInKit.framework/PlugInKit` | weak-link | regular |

There are no target-only install names in this comparison. The alternate
ExtensionFoundation path does not establish that dyld resolves the donor's
`/System/Library/Frameworks` name to the target's
`/System/Library/PrivateFrameworks` image.

## RunningBoardServices

Both caches report the same eight install names: seven regular and one
weak-link in each record. There are no path additions or removals, but two
shared names switch edge kind:

| Install name | 19H422 kind | 20H392 kind |
|---|---|---|
| `/System/Library/Frameworks/Security.framework/Security` | weak-link | regular |
| `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard` | regular | weak-link |

The other six rows retain their regular classification: libbsm,
Foundation, libobjc, libSystem, CoreFoundation, and CoreServices.

## SpringBoard.framework

Both records report 198 regular and 10 weak-link rows (208 total). The ten
weak-link paths match exactly:

- `/usr/lib/liblockdown.dylib`
- `/usr/lib/libAccessibility.dylib`
- `/usr/lib/libSystem.B.dylib`
- `Contacts.framework/Contacts`
- `ContactsUI.framework/ContactsUI`
- `CoreMedia.framework/CoreMedia`
- `BaseBoard.framework/BaseBoard`
- `/usr/lib/libutil.dylib`
- `SiriUI.framework/SiriUI`
- `/usr/lib/libobjc.A.dylib`

The donor SpringBoard record contains newer UI/service names, including
SystemAperture, ActivityKit, ActivityUIServices, PosterBoardUI,
BacklightServices, PosterBoardServices, PosterKit, and related components.
Selected rows were checked against the 19H422 `dylibs` image array below.

A complete 198-name regular-edge path diff is **not** claimed here. The
committed target report preserves counts, all ten weak-link names, and
selected regular paths rather than the entire ordered 198-row list. Equal
counts do not prove identical regular dependency sets.

## Selected donor paths versus the target cache image list

The target inventory contains 2,407 records with 2,407 unique indexes and
2,407 unique install names. A missing result here means only that no
same-basename record appears in that cache image-list array.

| Donor dependency basename | 19H422 cache image-list result |
|---|---|
| SystemAperture | No same-basename record |
| ActivityKit | No same-basename record |
| ActivityUIServices | No same-basename record |
| PosterBoardUI | No same-basename record |
| BacklightServices | No same-basename record |
| BacklightServicesHost | No same-basename record |
| PosterBoardServices | No same-basename record |
| PosterKit | No same-basename record |
| CoverSheetKit | No same-basename record |
| SessionAssertion | No same-basename record |
| BiomeLibrary | No same-basename record |
| PointerUISystemServices | No same-basename record |
| PaperBoardUI | No same-basename record |
| SystemStatusUI | No same-basename record |
| SystemApertureUI | No same-basename record |

Other selected donor SpringBoard names have same-path image-list records:
MediaExperience (index 194), ProactiveSuggestionClientModel (index 137),
ZoomServices (index 1548), Recap (index 2274), and AccessibilityUtilities
(index 120). Cache-image membership does not imply that the target
SpringBoard record has the same direct edge.

## Parser and evidence caveats

All three donor records contain implausible decoded `Sections` values,
similar to the target output. Some offsets visibly decode as ASCII-like
fragments of install-name strings and the sizes are implausible. Those
fields are excluded from analysis and must not be used for file-range or
memory-layout calculations. The parser/format cause remains unresolved.

No `BindTargets` block was included in the six supplied outputs. This report
does not infer that any BindTargets set is empty.

Keep these evidence categories separate: executable Mach-O load commands,
framework PrebuiltLoader rows, cache image-list membership,
mounted-filesystem path presence, and runtime behavior. Cache image-list
non-membership is not proof of filesystem absence; membership is not proof
of runtime resolution.

The target reference is iPhone 7 19H422 and the donor is iPhone X 20H392.
Both product generation and OS build differ, so the results cannot isolate
hardware-only effects. No ABI compatibility, process launch, hardware
provider attachment, display/input operation, kernel boot, or SpringBoard
readiness is established. The physical iPhone 7 remains on iOS 12.1.4.

## Next bounded research

Cross-reference the selected donor-only/changed paths against the target
mounted filesystem inventory using bounded read-only metadata checks.
Prioritize the ExtensionFoundation alternate path and PrivacyDisclosureCore,
then the selected modern UI/service names. Do not follow symlinks or infer
filesystem absence from cache image-list membership. M6 remains in progress;
M7 has not started.
