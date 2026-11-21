# 19H422 / 20H392 embedded XPC-service and app-extension comparison

## Scope and inputs

This report records the uploaded outputs from
\`tools/inspect_embedded_services.py\` for the iPhone 7 target reference
(iPhone9,1 / D10AP / A10-T8010, iOS 15.8.8 build \`19H422\`) and the
iPhone X donor reference (iPhone10,3 / D22AP / A11-T8015, iOS 16.7.16
build \`20H392\`). These are two separate OS releases and two different
products. Differences cannot be attributed to SoC generation alone.

The target report was generated from the supplied 19H422 filesystem root.
The donor report was generated with the donor OS root and SystemOS root
passed separately. The collector labels these as \`root_0\` and \`root_1\`;
the donor output contains 847 candidates from \`root_0\` and eight from
\`root_1\`. All eight second-root candidates are XPC bundles in the supplied
report.

Input SHA-256 values:

| Input | SHA-256 |
|---|---|
| 19H422 inventory JSON | \`689c5a2be1cde058061635f714dad87c465f1154dcd36eb3bafd616f05d352b3\` |
| 20H392 inventory JSON | \`56396b37dac5d59c831a41739061bbaf303b98821d25a3ec03f48375568517d9\` |

## Collection quality

| Measure | 19H422 target | 20H392 donor |
|---|---:|---:|
| Candidate bundle directories | 719 | 855 |
| Parsed Info.plists | 715 | 851 |
| Missing Info.plists | 4 | 4 |
| Scan errors | 0 | 0 |
| \`.appex\` candidates | 527 | 629 |
| \`.xpc\` candidates | 192 | 226 |
| Records with bundle identifiers | 715 | 851 |
| Unique bundle identifiers | 633 | 745 |
| Identifiers with multiple inventory records | 82 | 106 |

All records with an identifier were parsed. The four missing-Info.plist
records in each report have no bundle identifier and are retained as
collection gaps rather than being interpreted as empty bundles.

## Identifier comparison

| Identifier result | Count |
|---|---:|
| Present in both inventories | 598 |
| Target-only | 35 |
| Donor-only | 147 |
| Total unique identifiers in the union | 780 |

The duplicate-aware multiset comparison has 677 matching occurrences;
38 additional target occurrences and 174 additional donor occurrences
remain after matching by identifier. Twelve shared identifiers have
different occurrence counts between the two reports. Several donor
duplicates arise from the same app extension appearing under both an
AppPlaceholder and a staged system-app path. These rows must not be
mistaken for separate bundle identities or independent service processes.

The common identifier \`com.apple.weather.appremoval\` is an example of
the opposite count direction: it appears twice in the target inventory
and once in the donor inventory, at different observed paths.

## Metadata differences for shared identifiers

The comparator groups records by bundle identifier and compares the set of
distinct allowlisted metadata values. Repeated copies of the same metadata
do not by themselves create a metadata difference.

| Field | Shared identifiers with a difference |
|---|---:|
| \`MinimumOSVersion\` | 598 |
| Executable file-presence state | 11 |
| \`NSExtension\` selected metadata | 9 |
| \`CFBundleExecutable\` | 3 |
| Package type | 1 |
| Declared \`MachServices\` | 1 |

All 598 shared identifiers report \`MinimumOSVersion=15.8\` in the 19H422
inventory and \`MinimumOSVersion=16.7\` in the 20H392 inventory. This is
consistent with comparing the two different OS releases; it is not ABI or
runtime-compatibility evidence.

The 11 executable-state differences correspond to shared app-extension
identifiers for which the donor report contains both staged-app and
AppPlaceholder records. The staged copy reports the executable filename
as present while the placeholder copy reports it as not found. The
collector only checks the named file's presence/type; it does not validate
the Mach-O or its signature.

The nine extension-metadata differences include selected extension point,
principal-class, and allowlisted attribute-key changes. Three identifiers
have a different executable filename. The package-type difference is
\`com.apple.accessibility.HearingMLHelperService\` (\`XPC!\` in the target
record and \`BNDL\` in the donor record).

## MachServices declarations

The target inventory contains zero bundle-declared MachService names and
zero provider-index entries. The donor inventory contains two declared
names and two provider-index entries, both associated with the same
\`com.apple.audio.toolbox.reporting.service\` bundle at
\`AudioToolbox.framework/XPCServices/CAReportingService.xpc\`:

- \`com.apple.osanalytics.diagnosticmonitor\`
- \`com.apple.usernotifications.delegate.com.apple.coreaudio.audiocapturer.notification\`

These are declarations parsed from bundle metadata. They do not prove
that launchd registers the names, that the service launches, or that any
client connects to it. The target's zero declarations do not prove that
the names or services are absent from other unscanned sources or runtime
state.

## Reproduction

From the repository root on the host, run:

\`\`\`sh
python3 tools/compare_embedded_services.py \\
  /path/to/19H422-embedded-services.json \\
  /path/to/20H392-embedded-services.json \\
  --csv-out /path/to/19H422-20H392-embedded-service-identifiers.csv
\`\`\`

The tool prints a JSON summary to standard output and writes one CSV row
per unique bundle identifier when \`--csv-out\` is supplied. It reads only
the two sanitized JSON files; it does not mount filesystems, inspect
executables, or access a device. Ten synthetic tests cover identifier
presence, duplicates, metadata changes, missing identifiers, CSV output,
schema validation, and MachServices declaration accounting.

## Evidence boundary and next bounded question

This comparison extends the M6 static userland inventory. It does not
establish service registration, launch order, process creation, client
relationships, app-extension activation, ABI compatibility, dyld
resolution, kernel behavior, boot, or SpringBoard stability. The input
inventories cover only the selected mounted roots and \`.xpc\`/\`.appex\`
directory suffixes; absence from these reports is not global absence.

A sensible next host-only research question is to cross-reference the
declared service names from the bundle inventories against the already
collected launchd \`MachServices\` names, preserving provider declarations,
configured jobs, and runtime claims as separate evidence classes.

M6 remains in progress. M7/SpringBoard has not started. The physical
iPhone 7 remains on iOS 12.1.4; no device, firmware, partition, security,
or boot state was accessed or changed.
