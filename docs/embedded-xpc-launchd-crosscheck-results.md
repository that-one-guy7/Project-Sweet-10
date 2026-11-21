# Embedded-bundle MachServices versus LaunchDaemon provider cross-check

## Scope and source identity

This report joins the allowlisted MachServices declarations in the uploaded
19H422 and 20H392 embedded-bundle inventories against the provider indexes in
the corresponding central LaunchDaemons inventories. The launchd inputs are
the saved outputs of the read-only launchd inventory collector; the input
plist hashes match the values already recorded in
docs/iphone91-19h422-launchd-inventory-results.md.

- Target: iPhone9,1 / D10AP / A10-T8010, iOS 15.8.8 build 19H422.
- Donor: iPhone10,3 / D22AP / A11-T8015, iOS 16.7.16 build 20H392.

Input JSON SHA-256 values:

| Input | SHA-256 |
|---|---|
| 19H422 embedded-bundle inventory | 689c5a2be1cde058061635f714dad87c465f1154dcd36eb3bafd616f05d352b3 |
| 20H392 embedded-bundle inventory | 56396b37dac5d59c831a41739061bbaf303b98821d25a3ec03f48375568517d9 |
| 19H422 launchd inventory JSON | 539ae9992e6fb8395bf0354a2c3feb98cdae85933b40bb1a19a9a3e10c8270e3 |
| 20H392 launchd inventory JSON | 86c9f900b2e3a02e78631a1bdc10929d493d13beb401183f4b289b93732f1d92 |

The launchd inventories identify these source plist hashes:

| Source | SHA-256 |
|---|---|
| 19H422 central System/Library/xpc/launchd.plist | 34b6a174d2b948035afd71ad0a4fc2d3e4e85ea807a794ee69722054b09d6bbe |
| 20H392 central System/Library/xpc/launchd.plist | 810070302b5c4d7c5f00bdc8df20aaea2dd33cd8342d2402fcdf7ff6397d374c |

## Results

| Measure | 19H422 target | 20H392 donor |
|---|---:|---:|
| Parsed embedded bundles | 715 | 851 |
| Bundle-declared MachServices occurrences | 0 | 2 |
| Unique bundle-declared service names | 0 | 2 |
| Declared names found in central LaunchDaemons index | 0 | 1 |
| Declared names not found in central LaunchDaemons index | 0 | 1 |

The donor bundle declaration records both names under one bundle:

- Bundle identifier: com.apple.audio.toolbox.reporting.service
- Bundle path: System/Library/Frameworks/AudioToolbox.framework/XPCServices/CAReportingService.xpc
- Executable filename: CAReportingService
- Executable filename state: regular-file
- MinimumOSVersion: 16.7
- ServiceType: System

The corresponding target bundle is also present at the equivalent relative path.
It has the same bundle identifier and executable filename, with
MinimumOSVersion 15.8 and executable filename state regular-file, but declares
no MachServices names.

## Per-name cross-reference

| Bundle-declared service name | Present in 19H422 LaunchDaemons index | Present in 20H392 LaunchDaemons index | Static provider label |
|---|---|---|---|
| com.apple.osanalytics.diagnosticmonitor | Yes | Yes | com.apple.osanalytics.osanalyticshelper |
| com.apple.usernotifications.delegate.com.apple.coreaudio.audiocapturer.notification | No | No | None in either index |

For com.apple.osanalytics.diagnosticmonitor, both central launchd inventories
map the name to the same job label and program path:

- Job label: com.apple.osanalytics.osanalyticshelper
- Program: /System/Library/CoreServices/osanalyticshelper
- ProgramArguments count: 2
- RunAtLoad: null
- KeepAlive mode: unspecified

This is a static provider-index match. It does not establish that a process
started or registered the service, or that the CAReportingService bundle
connects to this job. The same service-name string occurring in both
metadata sources is not proof of a client/provider relationship.

The second donor-declared name has no matching entry in either central
LaunchDaemons provider index. That is a bounded negative result for these
two launchd.plist inventories only. It does not establish that the name is
absent from LaunchAgents, another plist, another filesystem volume, a
Cryptex, or runtime state.

## Reproduction

From the repository root on a host with the four saved JSON files:

    python3 tools/crosscheck_embedded_services_launchd.py \
      /path/to/19H422-embedded-services.json \
      /path/to/20H392-embedded-services.json \
      /path/to/19H422-launchd-inventory.json \
      /path/to/20H392-launchd-inventory.json

The utility validates both schema identifiers, validates service/provider
record shapes, preserves multiple bundle occurrences, prints JSON to standard
output, and records SHA-256 hashes for all four input files. Its synthetic
tests cover matches, unmatched names, duplicate bundle records, unparsed
bundles, empty declarations, invalid schemas, and malformed provider entries.

## Evidence limits

This comparison joins static Info.plist declarations to the central
LaunchDaemons provider index only. It does not identify all clients, prove
launchd registration, process launch, successful IPC, executable loadability,
signature validity, ABI compatibility, or SpringBoard readiness. An unmatched
name is not a global absence claim. The target and donor are different
products and different OS releases, so the results are not attributed to
A10/A11 generation alone.

M6 remains in progress. M7/SpringBoard has not started. The physical iPhone 7
remains on iOS 12.1.4; no device, firmware, partition, security, or boot state
was accessed or changed.
