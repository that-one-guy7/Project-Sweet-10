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
6. Keep Home-button, Touch ID/SEP, audio, cellular, Wi-Fi, Bluetooth, display,
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
