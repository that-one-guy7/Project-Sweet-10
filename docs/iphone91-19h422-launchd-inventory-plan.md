# Target-side launchd inventory: iPhone9,1 / 19H422

## Purpose

This plan and its collection stage are complete. The exact comparison of the
iPhone 7 / D10AP / iOS 15.8.8 (19H422) target-reference inventory against the
iPhone X / D22AP / iOS 16.7.16 (20H392) donor inventory is recorded in
[the exact results report](iphone91-19h422-launchd-inventory-results.md).

This is a **stock target-reference comparison**, not an iOS 16 target image.
The target reference is one major iOS release older than the 20H392 donor.
Differences may reflect OS-version changes as well as board/product
differences; they must not be attributed to A10 hardware without additional
evidence.

The physical iPhone 7 remains on iOS 12.1.4. This work uses only extracted or
read-only mounted IPSW data and JSON inventory reports. It does not require a
phone connection, firmware installation, boot operation, or device
modification.

## Collection method

The existing `tools/inspect_launchd_jobs.py` reads only
`System/Library/xpc/launchd.plist` below the supplied root directory. It
does not execute daemons, read their binaries, or modify the source tree.
It emits job labels, executable paths, advertised MachServices, socket names,
selected launch-policy fields, provider-label indexes, and a SHA-256 of the
source plist. It intentionally omits full ProgramArguments and
environment-variable values.

The user supplied both complete inventory JSON files, one for each root.
Both files use schema `project-sweet-10.launchd-inventory.v1` and identify
the same relative source plist. Their source hashes and exact counts are
recorded in the results report. The full JSON files are not committed.

The repository's synthetic tool tests remain available at
`tests/test_inspect_launchd_jobs.py`. The inventory command is:

```sh
python3 tools/inspect_launchd_jobs.py /path/to/extracted-ios-root \
  > launchd-inventory.json
```

## Completed comparison

The provider-index comparison found 1,451 common service names, 217
20H392-only names, and 34 19H422-only names. Provider-label lists differ
for 21 names present in both inventories. The inventories contain 532 and
475 LaunchDaemons entries respectively, with 1,668 and 1,485 distinct
provider-index service names.

The results report also records selected GUI/platform daemon comparisons,
duplicate job-label handling, and the target/donor multi-provider counts.
See [the exact results report](iphone91-19h422-launchd-inventory-results.md)
for complete lists and field-level observations.

## Scope and interpretation

A service appearing in a provider list means only that a plist advertises it.
It does not identify clients, prove successful registration, or show that a
daemon starts. A matching label, executable path, service name, or launch
policy does not establish ABI, entitlement, IOKit, hardware-provider, or
runtime compatibility.

The target reference and donor are different iOS releases. Do not describe
19H422 as the target iOS 16 userland, and do not ascribe every difference to
the A10 board. The report is static metadata from two central LaunchDaemons
dictionaries. It does not inventory LaunchAgents, embedded XPC bundles,
executable contents, or running processes.

This work improves M6's target-side service inventory. It does not establish
an iOS 16 launchd configuration for iPhone9,1, does not close readiness gate
G9, and does not show that SpringBoard can start on the device. **M6 remains
in progress; M7 has not started.**
