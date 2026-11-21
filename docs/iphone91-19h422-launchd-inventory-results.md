# iPhone9,1 / 19H422 target-side LaunchDaemons inventory results

## Scope and source identity

This report records a read-only inventory of the central
`System/Library/xpc/launchd.plist` from the stock iPhone 7 target-reference
filesystem: **iPhone9,1 / D10AP / iOS 15.8.8 / build 19H422**.

The comparator is the iPhone X donor reference:
**iPhone10,3 / D22AP / iOS 16.7.16 / build 20H392**. These are different
devices and different major iOS releases. The 19H422 inventory is a stock
target-side reference, not the intended iOS 16 userland for iPhone 7.
Differences cannot be assigned to hardware alone.

The physical iPhone 7 remains on iOS 12.1.4. This analysis uses only the
user-supplied host-side JSON report; no phone connection or device operation
was involved.

## Target inventory result

The existing `tools/inspect_launchd_jobs.py` completed successfully.

| Metric | iPhone9,1 / 19H422 |
|---|---:|
| Central LaunchDaemons entries | 475 |
| Unique job labels | 475 |
| Distinct advertised Mach service names | 1,485 |
| Mach service occurrences across jobs | 1,493 |
| Service names with multiple provider labels | 8 |
| Maximum provider labels for one service | 2 |

Input plist SHA-256:

`34b6a174d2b948035afd71ad0a4fc2d3e4e85ea807a794ee69722054b09d6bbe`

The eight multi-provider names, each advertised by two job labels, are:

| Service name | Provider labels |
|---|---|
| `PurpleSystemAppPort` | `com.apple.checkerboard`, `com.apple.SpringBoard` |
| `com.apple.UIKit.KeyboardManagement.hosted` | `com.apple.checkerboard`, `com.apple.SpringBoard` |
| `com.apple.UIKit.statusbarserver` | `com.apple.checkerboard`, `com.apple.SpringBoard` |
| `com.apple.frontboard.systemappservices` | `com.apple.checkerboard`, `com.apple.SpringBoard` |
| `com.apple.iap2d.ExternalAccessory.distributednotification.server` | `com.apple.accessoryd`, `com.apple.iap2d` |
| `com.apple.iap2d.distributednotification.server` | `com.apple.accessoryd`, `com.apple.iap2d` |
| `com.apple.iap2d.xpc` | `com.apple.accessoryd`, `com.apple.iap2d` |
| `com.apple.proactive.HomeScreenSuggestion.xpc` | `com.apple.duetexpertd`, `com.apple.SpringBoard` |

## Selected GUI/core-service comparison

The existing donor audit records 532 LaunchDaemons entries, 1,668 distinct
advertised Mach service names, and 21 multi-provider service names for 20H392.
The target inventory therefore has 57 fewer job entries and 183 fewer
distinct service names. The different OS releases and device identities mean
these aggregate differences are descriptive only.

The six selected daemon counts below are from the target JSON and the
previously documented donor summary:

| Job label | 19H422 target services | 20H392 donor services | Target program path | Target RunAtLoad | Target KeepAlive |
|---|---:|---:|---|---|---|
| `com.apple.backboardd` | 18 | 18 | `/usr/libexec/backboardd` | true | always |
| `com.apple.runningboardd` | 3 | 3 | `/usr/libexec/runningboardd` | true | always |
| `com.apple.SpringBoard` | 32 | 33 | `/System/Library/CoreServices/SpringBoard.app/SpringBoard` | true | always |
| `com.apple.configd` | 8 | 9 | `/usr/libexec/configd` | null | always |
| `com.apple.notifyd` | 1 | 1 | `/usr/sbin/notifyd` | null | unspecified |
| `com.apple.mediaserverd` | 82 | 87 | `/usr/sbin/mediaserverd` | null | always |

The selected target records also contain:

| Job label | Advertised service names | Target launch policy observation |
|---|---:|---|
| `com.apple.wifid` | 7 | RunAtLoad true; KeepAlive always |
| `com.apple.bluetoothd` | 13 | RunAtLoad true; KeepAlive conditions include `SuccessfulExit` |
| `com.apple.mobileactivationd` | 2 | KeepAlive unspecified |
| `com.apple.CommCenter` | 12 | KeepAlive always |
| `com.apple.CommCenterMobileHelper` | 3 | KeepAlive unspecified |
| `com.apple.CommCenterRootHelper` | 3 | KeepAlive unspecified |
| `com.apple.purplebuddy.budd` | 6 | KeepAlive unspecified |

All six selected GUI/core-service executable paths match those recorded for
the donor. That path match is only a configuration observation; it does not
establish binary equality, dependency equality, or runtime compatibility.

The target `backboardd` plist advertises touch-delivery, HID-service,
display-service, and IOHID event-system names, including
`com.apple.backboard.TouchDeliveryPolicyServer`,
`com.apple.backboard.hid-services.xpc`,
`com.apple.backboard.display.services`, and
`com.apple.iohideventsystem`. The target SpringBoard plist advertises
FrontBoard and SpringBoard service names. These entries show what the plist
declares as providers; they do not show that the services register or that
hardware input is working.

## Exact service-name set comparison still pending

The repository's 20H392 donor note contains aggregate counts and selected
daemon summaries, but the full donor JSON provider index is not committed.
Therefore this update does **not** claim an exact common/donor-only/target-only
Mach service name set comparison. The donor's documented multi-provider
count (21) and the target's computed count (8) are aggregate counts only;
they do not identify which service names overlap.

To finish that specific comparison, the full 20H392 output from the same
read-only inspector must be available alongside this target report. The
generated 19H422 JSON was reviewed locally and is not committed.

## Interpretation limits

This is static metadata from one central plist. It does not inventory
LaunchAgents, embedded XPC bundles, IOKit personalities, executable contents,
or running processes. A plist's MachServices list does not identify clients
or prove successful service registration. Job presence, matching labels,
matching paths, and launch-policy fields do not prove that a daemon starts,
that its frameworks and entitlements are compatible, or that target IOKit
providers and hardware operate.

The inventory does not establish an iOS 16 launchd configuration for
iPhone9,1, does not close readiness gate G9, and does not show that SpringBoard
can start on iPhone 7. **M6 remains in progress; M7 has not started.**
