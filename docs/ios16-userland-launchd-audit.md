# iOS 16 userland and launchd dependency audit

## Scope and target distinction

Project Sweet-10 uses the iPhone X iOS 16.7.16 (20H392) root filesystem as a
userland reference. The physical target remains iPhone 7, `iPhone9,1`,
A10/T8010. The donor's launchd jobs, IOKit personalities, device identity,
activation state, and hardware service providers are not assumed to be suitable
for the iPhone 7.

This note is based on the pinned public `14sea/ios-sunstone` reference revision
`e0471191ddbfb17fde6674db41320bffa832a85b` (reviewed 2026-11-20), plus a new
read-only inventory tool. Sunstone is a Qualcomm SM4375 port. Its userland
observations describe that port only; they are not iPhone9,1 measurements.

## Findings from the pinned 20H392 reference

The pinned Sunstone README reports this high-level startup chain:

`XNU -> UFS/HFS+ root -> SWEETDRP file drop -> dyld/shared cache -> launchd -> backboardd + SpringBoard`.

It reports launchd and system daemons running, with backboardd, SpringBoard,
the lock screen, home screen, and Settings reached on its SM4375 target. These
are upstream-reported results, not tests performed by Project Sweet-10.

The pinned root-filesystem tweak script documents the following specific
workarounds for that port:

| Area | What the reference script changes | What it tells Sweet-10 |
|---|---|---|
| launchd crash handling | Renames the private `_PanicOnCrash` key in each central LaunchDaemons entry | Daemon crash policy was adjusted during bring-up; do not copy private-key changes as a general fix |
| CoreTelephony | Removes entries whose `Label` is `com.apple.CommCenter` | The upstream author reports CommCenter crash-looping without a baseband and Setup waiting on its CoreTelephony XPC |
| Containers | Creates missing `/private/var/containers` subdirectories | Root-image creation alone did not provide all runtime container directories expected by the userland |
| Migration | Seeds `LastSystemVersion` and migration disposition preferences | First-boot migration behavior was adjusted in that environment |
| Audio/media | Disables `VirtualAudio.plugin` and sets MediaToolbox `StartRecorderServer` false | The reference reports mediaserverd failures related to unavailable audio/graphics paths |
| SpringBoard | Sets `BKNoWatchdogs` and hides cloud-configuration UI | Slow-path/watchdog and setup UI behavior needed accommodations on that target |
| Setup | Seeds Setup/PurpleBuddy completion preferences | The reference bypasses the first-run setup flow; that is not evidence the underlying services work |

The script also creates a synthetic mobileactivationd data-ark record and its
README describes a target-specific activation branch. This is recorded only as
an upstream limitation/workaround. Project Sweet-10 must not treat that
synthetic state as proof of legitimate activation, device identity, SEP support,
or data-protection readiness; no activation or security bypass is proposed here.

The companion `patch-launchd-plist.py` script can direct selected job
stdout/stderr to `/dev/console` and request framework log mirroring with
`OS_ACTIVITY_DT_MODE` and `CFLOG_FORCE_STDERR`. It also renames the same
private crash-policy key. This is evidence that per-job logging was used to
diagnose launchd services, not a generic launch configuration.

The reference's `sweet-init.S` is a separate early userspace diagnostic:
it is a small static PID 1 used to test exec, the user/kernel boundary, devfs,
and the console. It is not the normal iOS launchd implementation. Keep an
early-init smoke test distinct from the final launchd boot milestone.

## Dependency map: what is known and unknown

| Component | Evidence in the reference | Sweet-10 status |
|---|---|---|
| launchd | Central `System/Library/xpc/launchd.plist` contains LaunchDaemons; helper edits its LaunchDaemons dictionary | Actual 20H392 plist not yet inventoried in this repository |
| backboardd | Reported running on Sunstone; HID/display support is necessary for an interactive UI | No iPhone9,1 match or event-service integration verified |
| SpringBoard | Reported running on Sunstone; reference uses SpringBoard preferences and crash scanning | iPhone 7 Home-button/UI behavior and required providers remain unknown |
| CommCenter / CoreTelephony | Sunstone reports removal of CommCenter jobs to avoid crash loops and Setup's CoreTelephony XPC wait | iPhone7 radio/baseband and CoreTelephony service state not assessed |
| mediaserverd / MediaToolbox | Sunstone reports disabling VirtualAudio and recorder-server prewarm after crashes | iPhone7 audio/graphics providers not assessed |
| wifid / bluetoothd | Sunstone reports bluetoothd crash/relaunch and no Wi-Fi userland interface despite kernel-side WLAN tests | No iPhone9,1 service providers or userland interface verified |
| mobileactivationd | Root-image setup includes a target-specific data-ark record | Activation, identity, SEP and data-protection compatibility remain separate and unverified |
| LaunchServices / dyld | README reports first boot spends time building the LaunchServices database; describes dyld/shared cache before launchd | Exact launch chain and service readiness not independently measured on target |

Do not infer consumer dependencies from a job's `MachServices` dictionary
alone. That dictionary advertises endpoints provided by a job; it does not
identify every client or prove that a service successfully starts. Likewise,
a configured launchd job is not proof that its executable, frameworks,
entitlements, IOKit providers, or hardware dependencies are functional.

## New read-only inventory tool

`tools/inspect_launchd_jobs.py` reads the central
`System/Library/xpc/launchd.plist` from an extracted or mounted root. It emits
JSON containing:

- launchd job labels and executable paths;
- argument counts, not full argument vectors;
- MachServices and socket names advertised by each job;
- KeepAlive mode and condition-key names;
- selected scheduling, identity, and process-type fields;
- environment-variable names, never their values;
- a SHA-256 of the input plist and a provider index for MachServices.

It never executes a daemon, reads executable contents, changes the plist, or
writes into the root filesystem. It covers the central LaunchDaemons dictionary
only; it is not a full inventory of LaunchAgents, XPC bundles, IOKit
personalities, or running processes.

Run it on a local extracted root:

```sh
python3 tools/inspect_launchd_jobs.py /path/to/extracted-ios-root \
  > launchd-inventory.json
```

The resulting report is safe to review as static metadata, but check it before
committing: do not include private environment values, personal identifiers,
or proprietary binary content. The tool intentionally omits environment values
and full ProgramArguments.

Run host tests:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Results from the mounted 20H392 donor image (2026-11-20)

The user ran the read-only inventory against the mounted donor root and supplied
the resulting JSON for review. The report identifies:

- **532** entries in the central `LaunchDaemons` dictionary.
- **1,668** distinct advertised Mach service names.
- Input plist SHA-256:
  `810070302b5c4d7c5f00bdc8df20aaea2dd33cd8342d2402fcdf7ff6397d374c`.
- The filtered focus list includes `backboardd`, `runningboardd`,
  `SpringBoard`, `configd`, `notifyd`, `mediaserverd`, `wifid`,
  `bluetoothd`, `mobileactivationd`, Setup Assistant, and CommCenter
  (including separate cellular and non-cellular entries).

Selected donor-side records:

| Job | Program path | Advertised services | Static launch policy |
|---|---|---:|---|
| `com.apple.backboardd` | `/usr/libexec/backboardd` | 18 | RunAtLoad; KeepAlive always |
| `com.apple.runningboardd` | `/usr/libexec/runningboardd` | 3 | RunAtLoad; KeepAlive always |
| `com.apple.SpringBoard` | `/System/Library/CoreServices/SpringBoard.app/SpringBoard` | 33 | RunAtLoad; KeepAlive always |
| `com.apple.configd` | `/usr/libexec/configd` | 9 | KeepAlive always |
| `com.apple.notifyd` | `/usr/sbin/notifyd` | 1 | KeepAlive unspecified |
| `com.apple.mediaserverd` | `/usr/sbin/mediaserverd` | 87 | KeepAlive always |

The provider index associates the backboard HID, display, touch-delivery, and
IOHID event-system endpoints with `com.apple.backboardd`; SpringBoard advertises
its SpringBoard and FrontBoard-related endpoints; and `com.apple.runningboard`
is advertised by `com.apple.runningboardd`. The provider index also reports
21 service names with more than one provider label, so service-name presence
alone must not be treated as proof of an unambiguous or successful runtime
registration.

**Interpretation boundary:** these are static configuration facts from the
iPhone X donor image. They do not prove that each executable exists in the
mounted root, that a daemon starts successfully, which clients consume each
Mach service, or that any provider works on iPhone 7 `iPhone9,1`. The report
covers only the central LaunchDaemons dictionary; it does not inventory
LaunchAgents, embedded XPC bundles, IOKit personalities, or runtime processes.
The full JSON was reviewed locally and is not committed to this repository.

## Mach-O direct-link inventory for the GUI chain (2026-11-20)

The user also inspected the donor executables with LLVM `llvm-objdump` using
`--macho --dylibs-used` and `--macho --rpaths`. The output reports these
direct load-command dependencies:

| Executable | Direct linked dylibs reported | Notable links |
|---|---:|---|
| `/usr/libexec/backboardd` | 46 | BackBoard HID event foundation/processors and services; IOMobileFramebuffer; IOKit; IOSurface; Metal; CoreGraphics; CoreBrightness; BiometricKit; ButtonResolver; RunningBoardServices |
| `/usr/libexec/runningboardd` | 6 | Foundation; RunningBoard; RunningBoardServices; CoreFoundation; libobjc; libSystem |
| `SpringBoard.app/SpringBoard` | 4 | SpringBoard.framework; Foundation; libobjc; libSystem |

The `backboardd` output marks `/usr/appleinternal/lib/liblinkguard.dylib`
as a weak dependency. The reported runtime search paths are empty for
`backboardd` and `runningboardd`; SpringBoard reports
`@executable_path/Frameworks`.

### Interpretation

- This is the direct dependency list recorded in each Mach-O image, not a
  recursive dependency closure. Frameworks such as SpringBoard.framework and
  BackBoardServices.framework have their own dependencies that still need
  separate inspection.
- A dependency's install name is not proof that its file is present in the
  mounted root, loadable from the donor's split system volume layout, or
  compatible with iPhone9,1.
- The empty `LC_RPATH` result for two binaries does not mean they have no
  dependencies; their output contains absolute install names. SpringBoard's
  executable-relative Frameworks path must be checked against the app bundle.
- The backboard dependency set flags display, HID, graphics, biometric, and
  accessory integration as major areas for later target-specific compatibility
  research. It does not identify the implementation or register interface of
  those drivers on iPhone 7.

**Next static check:** resolve the absolute install names against the mounted
donor root, inspect SpringBoard.app/Frameworks, and separately account for any
system frameworks supplied by the companion SystemOS Cryptex. Missing paths in
the root filesystem alone must not be classified as absent from the complete
donor system.

## M6 status and next evidence needed

**M6 remains in progress.** The actual 20H392 donor root has now been inventoried
locally and reviewed as static metadata. No iPhone9,1 runtime logs or target-side
service matching evidence exist.

The next M6 evidence should:

1. Check whether the selected daemon executable paths are present in the mounted
   donor root, accounting for APFS mount layout and symlinks; do not execute them.
2. Cross-reference the GUI chain (launchd, backboardd, SpringBoard,
   LaunchServices) against embedded XPC bundles and IOKit personality metadata.
3. Keep configured jobs separate from observed runtime processes and successful
   service registration.
4. Compare each donor-side requirement with iPhone9,1-specific DeviceTree and
   stock-firmware evidence; classify it as target-confirmed, donor-reference-only,
   missing, or unverified.
5. Keep Home-button, Touch ID/SEP, audio, cellular, Wi-Fi, Bluetooth, display,
   battery, and power dependencies as distinct target-specific rows.

Until those checks are complete, the 20H392 donor's reported SpringBoard boot
is a compatibility reference, not evidence that SpringBoard will start on
iPhone9,1. No machine configuration, launchd plist, activation state, security
policy, firmware, or device partition is changed by this audit.


## Pinned upstream source files

The reference observations above were checked against these files at
`e0471191ddbfb17fde6674db41320bffa832a85b`:

- [Sunstone README](https://github.com/14sea/ios-sunstone/blob/e0471191ddbfb17fde6674db41320bffa832a85b/README.md)
- [Root-filesystem tweaks](https://github.com/14sea/ios-sunstone/blob/e0471191ddbfb17fde6674db41320bffa832a85b/tools/sweet-root-tweaks.py)
- [launchd logging helper](https://github.com/14sea/ios-sunstone/blob/e0471191ddbfb17fde6674db41320bffa832a85b/tools/patch-launchd-plist.py)
- [Early userspace diagnostic](https://github.com/14sea/ios-sunstone/blob/e0471191ddbfb17fde6674db41320bffa832a85b/tools/sweet-init.S)
- [SpringBoard crash scan patch](https://github.com/14sea/ios-sunstone/blob/e0471191ddbfb17fde6674db41320bffa832a85b/xnu/patches/0053-sweet-crash-scan-springboard.patch)
- [HID event service patch](https://github.com/14sea/ios-sunstone/blob/e0471191ddbfb17fde6674db41320bffa832a85b/xnu/patches/0058-sweet-hid-event-services.patch)

The README's status is the upstream author's report. The helper-script findings
are derived from the pinned source files; neither source category is a Sweet-10
measurement.


## Split dyld shared-cache inventory from the mounted SystemOS Cryptex (2026-11-20)

The user mounted the separate iPhone X 20H392 SystemOS Cryptex and inspected
`System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64` with ipsw
3.1.749 (`a7dfadbcaca8375b424c12a68dae40767e5e07c1`). The command
`ipsw dyld info -l` exited 0 with empty stderr. The cache header reports
magic `dyld_v1   arm64`, platform iOS, OS version 16.7, 2,710 images,
42 subcaches, and UUID `8F970452-C9E3-3E88-B114-FEB1864BC9E0`.

The cache image list includes Foundation, CoreFoundation, CoreGraphics, Metal,
IOKit, IOSurface, AVFoundation, BackBoardServices,
BackBoardHIDEventFoundation, BackBoardHIDEventProcessors, RunningBoardServices,
RunningBoard, SpringBoard, SpringBoardServices, and SpringBoardHome. Versions
and exact image paths are recorded in
[the split dyld cache inventory](20h392-dyld-cache-inventory.md).

This closes the earlier **volume-location** question for those image-list
entries: the relevant framework images are listed by the donor's SystemOS
shared cache even though many ordinary paths were not found in the separately
mounted OS root filesystem. It does not close the recursive dependency graph,
prove every load command resolves at runtime, establish code-signing or closure
validity, inventory all embedded XPC/IOKit requirements, or establish
iPhone9,1 compatibility. The 20H392 image remains an iPhone X donor reference.


## Prebuilt dyld loader records for the GUI chain (2026-11-20)

The user ran ipsw dyld image against the separate iPhone X 20H392 SystemOS
shared cache for backboardd, runningboardd, and SpringBoard. All three
commands exited 0. Each output reported PrebuiltLoaderSet version 4d2b8647
and an app loader with flags
prebuilt|objc|ro-data|never-unload|pre-2022.

The complete Dependents block supplied for backboardd contains 45 regular
dependent install names plus one weak-link record reported as
index 32767 (missing weak image). The weak-link record does not include an
install name in the supplied output, so its identity remains unresolved. The
full ordered list is recorded in
[the dedicated PrebuiltLoaderSet audit](20h392-prebuilt-loader-audit.md).
The earlier terminal excerpt displayed only the first 60 lines, but the later
full Dependents block resolves the inventory count for this record.

The supplied runningboardd record lists six regular dependents: Foundation,
RunningBoard, RunningBoardServices, libobjc, libSystem, and CoreFoundation.
The SpringBoard executable lists four: SpringBoard.framework, Foundation,
libobjc, and libSystem. Their outputs also contain precomputed bind-target
records.

Apple's dyld4 design documentation explains that PrebuiltLoaders contain
precomputed dependent-dylib and bind-target information. These records
therefore improve the donor-side static dependency map beyond ordinary
LC_LOAD_DYLIB strings, but they remain metadata, not observations of a process
launch. See [the dedicated PrebuiltLoaderSet audit](20h392-prebuilt-loader-audit.md)
for the paths and caveats.

The ipsw output also prints implausible section offsets/sizes for several
Swift and Objective-C sections. Those fields are excluded pending independent
parser validation. The complete backboardd dependency list now contains 45
regular paths plus one weak-link record, but the exact weak-link install name
is unresolved. None of these observations establishes iPhone9,1 compatibility,
hardware-provider availability, or a successful iPhone 7 launch. M6 remains
in progress and M7 has not started.


## Next framework-level inspection

The dedicated [BackBoard framework dependency expansion plan](20h392-backboard-framework-dependency-expansion.md)
defines the next donor-cache queries for BackBoardHIDEventFoundation,
BackBoardHIDEventProcessors, BackBoardServices, and IOMobileFramebuffer.
These four images were selected because their install names appear in the
user-supplied backboardd PrebuiltLoaderSet dependents and in the donor cache
inventory. Their individual loader outputs have not yet been collected.
The plan keeps dependent edges, weak-link records, and bind targets separate,
and explicitly requires iPhone9,1 compatibility to be established from
target-specific evidence rather than donor-cache presence.


## BackBoard framework dependent-loader results (2026-11-20)

The user ran `ipsw dyld image` for BackBoardHIDEventFoundation,
BackBoardHIDEventProcessors, BackBoardServices, and IOMobileFramebuffer in
the donor SystemOS cache. All four commands exited 0 and the supplied
terminal output showed no stderr messages. The resulting blocks contain
35 regular dependent rows and one separately typed re-export row; no
weak-link entries appeared in these four blocks.

Notable observed edges include BackBoardHIDEventProcessors depending on
BackBoardHIDEventFoundation, both HID frameworks depending on
BackBoardServices, and IOMobileFramebuffer depending on IOSurface and IOKit.
BackBoardServices reports AssertionServices as a re-export. The complete
ordered rows and interpretation limits are recorded in
[the BackBoard framework dependency results](20h392-backboard-framework-dependency-results.md).

This remains donor-side static metadata. It does not identify API use,
runtime clients, target IOKit providers, or iPhone9,1 compatibility.
M6 remains in progress; M7 has not started.


## Service and graphics framework loader results (2026-11-20)

The user inspected six more donor SystemOS cache loader records:
BoardServices, BaseBoard, GraphicsServices, RunningBoardServices,
AssertionServices, and IOSurface. All six reported exit status 0 in the
supplied terminal excerpt. The dependent rows comprise 44 regular entries,
two weak-link entries naming BaseBoard, and one GraphicsServices entry
printed as `unknown 3`. The pinned ipsw v3.1.749 source assigns 1 to
weak-link and 2 to re-export, then formats kinds using exact matches, so the
combined value 3 displays as unknown. Apple dyld formats weak-link and
re-export attributes independently, making kind 3 a strong candidate for
weak-link + re-export. The raw dependent-kind byte has not yet been inspected,
so the combined interpretation remains qualified.

The records show donor-side relationships including BoardServices to
BaseBoard, BaseBoard to IOSurface/IOKit/CoreGraphics,
RunningBoardServices weak-linking BaseBoard, AssertionServices depending
on RunningBoardServices and weak-linking BaseBoard, and IOSurface depending
on IOKit. Full ordered results and caveats are in
[the service and graphics framework dependency results](20h392-platform-framework-dependency-results.md).

The next bounded donor inspection targets IOKit, CoreGraphics, and the
FontServices image named by the unknown-kind row. These cache records remain
static iPhone X donor evidence, not iPhone9,1 driver or SpringBoard proof.
M6 remains in progress; M7 has not started.


## IOKit, CoreGraphics, and FontServices loader results (2026-11-20)

The user inspected the iPhone X 20H392 donor SystemOS loaders for IOKit,
CoreGraphics, and FontServices `libGSFont.dylib`. All three commands reported
exit status 0 and the pasted output showed no stderr messages. The supplied
blocks contain 25 regular dependency rows, one explicit CoreAnalytics weak
link from CoreGraphics, and three FontServices `unknown 3` entries naming
CoreText, FontServices, and libGSFontCache.

The raw kind-3 classification was checked against the exact ipsw v3.1.749
source commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1` and Apple dyld commit
`fd8d0c4d52320ebf64db34f3cb280310d905c5ae`. ipsw defines weak-link=1 and
re-export=2 but its String method switches on exact values, so combined value
3 prints as `unknown 3`. Apple's `LinkedDylibAttributes` defines weakLink
and reExport as independent bitfields and its formatter appends both flags.
The kind-3 entries are therefore source-mapped to weak-link + re-export; the
original raw ipsw label is retained. This is a parser/source interpretation,
not an independent extraction of the raw byte from the cache.

Complete ordered records are in
[the IOKit and font-framework dependency results](20h392-iokit-font-framework-dependency-results.md).
The next bounded inspection follows libFontParser, FontServices,
libGSFontCache, and CoreText. These remain donor static records and do not
establish iPhone9,1 graphics or font runtime compatibility.


## FontServices/CoreText dependent-loader results (2026-11-20)

The user inspected the 20H392 donor loaders for libFontParser,
FontServices, libGSFontCache, and CoreText. All four commands reported exit
status 0 and the supplied output showed no stderr text. The blocks contain
37 regular dependency rows, one explicit weak-link row from FontServices to
SpringBoardServices, and six raw kind-3 rows (weak-link + re-export) across
libFontParser, FontServices, and CoreText.

The six kind-3 rows retain the ipsw raw display `unknown 3`; the source
mapping follows the exact ipsw v3.1.749 formatter and Apple's one-byte
LinkedDylibAttributes bitfield/formatter, as documented in the earlier
[service and graphics framework audit](20h392-platform-framework-dependency-results.md).
The reciprocal CoreGraphics/libFontParser relationship preserves different
edge types: CoreGraphics lists libFontParser as regular, while libFontParser
lists CoreGraphics as weak-link + re-export. Do not collapse these into
identical strong edges.

The complete ordered lists, derived donor-side edges, and caveats are in
[the FontServices and CoreText dependency results](20h392-fontservices-coretext-dependency-results.md).
The broad donor font chain is now bounded and documented. M6's next priority
is an iPhone9,1 target-native crosswalk, not indiscriminate expansion of
generic donor frameworks. This remains static research only; M7 has not started.


## Selected GUI-chain Program-path presence check (completed 2026-11-21)

The user supplied the generated read-only report from the target and donor
mounted filesystem roots. All nine selected LaunchDaemon `Program` paths
were found as regular filesystem objects in both datasets.

| Dataset | Supplied roots | Found | Matched root | Wrapper depth |
|---|---:|---:|---|---:|
| Target 19H422 | 1 | 9/9 | `target_root_0` | 1 (`root/`) |
| Donor 20H392 | 2 | 9/9 | `donor_root_0` | 2 (`root/root/`) |

All nine target paths matched at wrapper depth 1. All nine donor paths matched
at depth 2 in `donor_root_0`; none matched the tested prefixes in
`donor_root_1`. This is a difference in the supplied mount layouts, not proof
that the second donor volume lacks those files or other services.

The full result and per-job paths are recorded in
[the actual Program-path presence results](launchd-program-path-presence-results.md)
and the machine-readable summary at
[`research/launchd-program-path-presence-results.json`](../research/launchd-program-path-presence-results.json).

Provenance: the supplied report SHA-256 is
`33dbb1e62ded690e0660c4fd76fd7b343e3155afa3ae3053475a17c105a202d9`.
It references target launchd inventory SHA-256
`539ae9992e6fb8395bf0354a2c3feb98cdae85933b40bb1a19a9a3e10c8270e3`
and donor inventory SHA-256
`86c9f900b2e3a02e78631a1bdc10929d493d13beb401183f4b289b93732f1d92`.

**Interpretation boundary:** the scanner used `lstat` component by component,
stopped at symlinks, and did not open, hash, execute, or inspect program
contents. A regular-file result does not validate Mach-O format or architecture,
signature, entitlements, ABI, dependencies, or loadability. It also does not
prove launchd registration, process launch, runtime behavior, kernel
compatibility, or SpringBoard readiness.

The path-presence checklist item is complete. M6 remains in progress. The next
useful static evidence is a target-native dependency crosswalk for
`backboardd`, `runningboardd`, and SpringBoard against the 19H422 system and
shared-cache inventories, while keeping any donor-only framework or provider
requirement explicitly unverified for iPhone9,1. M7 has not started.


## Target iPhone9,1 GUI-chain Mach-O direct dependencies (2026-11-21)

The user supplied the host-side `file`, `llvm-objdump --macho
--dylibs-used`, and `llvm-objdump --macho --rpaths` output for the
three selected target executables. Ubuntu LLVM was version `18.1.3`; all
three executables were identified as Mach-O 64-bit arm64 with flags
`NOUNDEFS|DYLDLINK|TWOLEVEL|PIE`.

| Executable | Target regular direct dependencies | Weak dependencies | Target rpath |
|---|---:|---:|---|
| `backboardd` | 42 | 1 named: `/usr/appleinternal/lib/liblinkguard.dylib` | none printed |
| `runningboardd` | 6 | 0 | none printed |
| `SpringBoard` | 4 | 0 | `@executable_path/Frameworks` |

Compared with the previously recorded 20H392 donor output, the target
`runningboardd` and SpringBoard direct install-name sets match exactly,
including their respective rpath results. Target `backboardd` has 42
regular install names in common with the donor's 45 regular entries. The
three donor-only direct edges are CarKit, SystemWake, and SoftLinking.
The named weak `liblinkguard.dylib` appears in both direct Mach-O
inventories. The separate donor PrebuiltLoaderSet output still has an
unnamed weak index `32767`; its identity is not assumed here.

Full ordered target paths and the source comparison are recorded in
[the target GUI-chain dependency results](iphone91-19h422-gui-macho-dependency-results.md)
and the machine-readable
[`research/iphone91-19h422-gui-macho-dependency-results.json`](../research/iphone91-19h422-gui-macho-dependency-results.json).

This is direct load-command metadata, not a recursive dependency closure.
The `arm64` file identification does not establish iOS 16 ABI compatibility,
dyld resolution, code-signing validity, entitlements, IOKit provider
attachment, or successful launch. M6 remains in progress; M7 has not started.
The next static step is to cross-reference the exact install names against
the target 19H422 dyld image inventory and mounted root, while checking the
SpringBoard app-local rpath separately.


## GUI-chain dependencies cross-referenced against the target dyld image list (2026-11-21)

The archived target cache export contains a complete `dylibs` array with
2,407 records (indexes 1–2,407; 2,407 unique install names). The user-reported
raw file was `$HOME/19H422-dyld-images.json` (132,175,259 bytes). The
archived capture `log.txt` has SHA-256
`d2cb1fb9e75f1d2c477c1cb7c0561cd4ec2b220b19ba96d6828ee267a9a83f3b`.

All **44 unique regular direct dependency paths** from the target
`backboardd`, `runningboardd`, and SpringBoard executables are represented
in the target `dylibs` image array: 42/42 for backboardd, 6/6 for
runningboardd, and 4/4 for SpringBoard. The one additional unique weak
dependency path, `/usr/appleinternal/lib/liblinkguard.dylib`, is not
represented in that image array. This does not establish that the weak path
is absent from the full filesystem or system installation.

Notably, the three donor-only regular direct `backboardd` dependency edges
(CarKit, SystemWake, and SoftLinking) are each present as target cache images.
Thus they are donor-only edges in the executable's direct dependency list,
not cache-image absences in the 19H422 target.

The complete path, index, version, UUID, and consumer cross-reference is in
[the target GUI dependency cache report](iphone91-19h422-gui-dependency-cache-crossref.md)
and its [machine-readable JSON](../research/iphone91-19h422-gui-dependency-cache-crossref.json).

The target-side framework loader capture is now complete for
SpringBoard.framework, RunningBoard.framework, and RunningBoardServices.framework:
all three queries returned exit status 0. The recorded PrebuiltLoader reference
indexes and dependency rows are in the
[target GUI framework loader results](iphone91-19h422-gui-framework-loader-results.md).
The target report keeps PrebuiltLoader reference indexes distinct from cache
image-list indexes and excludes the malformed `Sections` fields from
interpretation.

The matching 20H392 donor captures are now complete for all three exact
framework paths; each query exited with status 0. Comparative findings and
machine-readable rows are in the
[20H392 / 19H422 GUI framework loader comparison](20h392-19h422-gui-framework-loader-comparison-results.md)
and [JSON data](../research/20h392-19h422-gui-framework-loader-comparison.json).

The clearest comparisons are:
- RunningBoard: 20 shared names, two donor-only names, and three shared
  paths whose regular/weak-link kinds change.
- RunningBoardServices: all eight names are shared; Security and BaseBoard
  switch edge kinds.
- SpringBoard.framework: both records have 198 regular and 10 weak-link rows,
  and the ten weak-link paths match; a full regular-path diff is not claimed.

Selected donor paths were also checked against the 2,407-entry target cache
image list. The donor ExtensionFoundation path is under `Frameworks`, while
the target has a same-named image under `PrivateFrameworks`; PrivacyDisclosureCore
has no matching target image-list record. These are cache-list observations,
not filesystem or runtime results.

The target and donor differ in both product generation and OS build, so
observed differences cannot be attributed to hardware alone.

**Interpretation boundary:** cache image-list membership and PrebuiltLoader
metadata do not prove dependency resolution, file-system presence, signatures,
ABI, successful loading, process launch, provider attachment, or SpringBoard
readiness. M6 remains in progress; M7 has not started.
