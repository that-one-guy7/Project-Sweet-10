# Target-side launchd inventory plan: iPhone9,1 / 19H422

## Purpose

The repository has a detailed static LaunchDaemons inventory for the iPhone X
20H392 donor (532 jobs and 1,668 advertised Mach service names), but no
equivalent inventory for the iPhone 7 / D10AP target reference. The next
useful M6 step is to run the existing read-only inspector against the
already-audited iPhone9,1 / iOS 15.8.8 (19H422) root filesystem.

This is a **stock target-reference comparison**, not an iOS 16 target image.
The target reference is one major iOS release older than the 20H392 donor.
Differences may reflect OS-version changes as well as board/product
differences; they must not be attributed to A10 hardware without additional
evidence.

The physical iPhone 7 remains on iOS 12.1.4. This plan uses only an extracted
or read-only mounted IPSW filesystem on the host. It does not require a phone
connection, firmware installation, boot operation, or device modification.

## Existing tool

Use the existing
[`tools/inspect_launchd_jobs.py`](../tools/inspect_launchd_jobs.py).
It reads only:

`System/Library/xpc/launchd.plist`

under the supplied root directory. It does not execute daemons, read their
binaries, or modify the source tree. It reports job labels, executable paths,
advertised MachServices, socket names, selected launch-policy fields, and a
SHA-256 of the source plist. It intentionally omits full ProgramArguments
and environment-variable values.

The tool has synthetic tests in
[`tests/test_inspect_launchd_jobs.py`](../tests/test_inspect_launchd_jobs.py).

## Host-side collection

Use a local directory that already contains the extracted 19H422 root, or a
read-only mount of that root. The path must be the directory whose immediate
contents include `System/Library/xpc/launchd.plist`.

Run:

```sh
python3 tools/inspect_launchd_jobs.py /path/to/19H422-root \
  > 19H422-launchd-inventory.json
```

The command writes the report to the current working directory; the input
root is read only. If the tool reports that the plist is missing or malformed,
stop and record the exact error. Do not substitute the donor plist or infer
that the target has no launchd configuration.

Run the repository's host-side tests separately:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Comparison checklist

Compare the 19H422 report with the existing 20H392 donor inventory for these
GUI and platform jobs when present:

- `com.apple.backboardd`
- `com.apple.runningboardd`
- `com.apple.SpringBoard`
- `com.apple.configd`
- `com.apple.notifyd`
- `com.apple.mediaserverd`
- `com.apple.wifid`
- `com.apple.bluetoothd`
- `com.apple.mobileactivationd`
- Setup Assistant / PurpleBuddy and CommCenter-related jobs

For each matching label, compare only fields that are actually present:
program path, advertised MachServices, socket names, RunAtLoad, KeepAlive
mode/condition-key names, and process type. Preserve absent, null, and
different values as distinct states.

For MachServices, record:
- services advertised by both versions;
- donor-only and target-only advertised names;
- services with multiple provider labels in either report.

A service appearing in a provider list means only that a plist advertises it.
It does not identify clients, prove successful registration, or show that a
daemon starts. A matching label or executable path does not establish ABI,
entitlement, IOKit, hardware-provider, or runtime compatibility.

## Reporting and privacy

Do not commit the complete generated JSON by default. It contains a broad
inventory of system service names and paths. Report only the selected GUI
records, aggregate counts, the source plist SHA-256, and the specific
differences needed for the M6 analysis. Exclude personal identifiers,
device-specific values, environment-variable values, and unrelated service
records.

Record the source as **iPhone9,1 / D10AP / iOS 15.8.8 / build 19H422** and
the comparator as **iPhone10,3 / D22AP / iOS 16.7.16 / build 20H392**.
Do not describe 19H422 as the target iOS 16 userland.

## Acceptance criteria

This audit is complete only when:

1. The target plist was read successfully and its SHA-256 is recorded.
2. The target job and service counts are recorded.
3. The selected GUI/platform labels are compared using exact labels and
   explicitly preserved missing entries.
4. Donor-only and target-only service names are counted and listed in a
   bounded report.
5. The report states that this is static plist metadata from different
   iOS releases, not runtime or compatibility evidence.

The result will improve M6's target-side service inventory. It will not close
G9, establish an iOS 16 launchd configuration for iPhone9,1, or show that
SpringBoard can start on the device.
