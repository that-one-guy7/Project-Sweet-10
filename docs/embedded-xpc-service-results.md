# Embedded XPC-service and app-extension inventory results

## Scope

This report records the first actual output from
`tools/inspect_embedded_services.py` for the two reference filesystems:

- **Target:** iPhone 7, `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8,
  build `19H422`.
- **Donor:** iPhone X, `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16,
  build `20H392`.

The reports were generated from the user's already-mounted host-side roots.
The target used one root. The donor used its OS root and SystemOS root as
separate inputs. No filesystem was mounted or modified by the inventory tool.
The physical iPhone 7 remains on iOS 12.1.4; neither reference image was
installed on it.

## Collection integrity and totals

Both JSON files parse successfully and conform to
`project-sweet-10.embedded-service-inventory.v1`. The accompanying
`embedded-services-results.tar.gz` contains exactly the two JSON reports;
each archived file is byte-for-byte identical to its separately uploaded
counterpart. Both reports have an empty `scan_errors` list.

| Measure | 19H422 target | 20H392 donor |
|---|---:|---:|
| Input roots | 1 | 2 |
| Candidate bundles | 719 | 855 |
| `.appex` candidates | 527 | 629 |
| `.xpc` candidates | 192 | 226 |
| Parsed Info.plists | 715 | 851 |
| Missing Info.plists | 4 | 4 |
| Scan errors | 0 | 0 |
| Unique bundle identifiers among parsed records | 633 | 745 |
| Repeated identifier groups | 82 | 106 |

The donor's first input root (`root_0`) contributed 847 candidates
(629 `.appex`, 218 `.xpc`). Its second input root (`root_1`) contributed
eight additional `.xpc` candidates. Keeping those roots separately is
important: a bundle not found in one root is not thereby absent from the
other root or from the combined system.

### Missing Info.plists

These four candidates in each report were retained with status
`missing-info-plist`; they were not treated as parsed bundles with empty
metadata.

**19H422 target**
- `root/System/Library/AppPlaceholders/Books.app/XPCServices/XPCUbiquityDisableService.xpc`
- `root/System/Library/AppPlaceholders/Music.app/Frameworks/MusicApplication.framework/XPCServices/MusicScriptUpdateService.xpc`
- `root/System/Library/AppPlaceholders/Weather.app/PlugIns/com.apple.weather.appremoval.xpc`
- `root/System/Library/PrivateFrameworks/SmartChargingWidget.framework/PlugIns/SmartChargingWidget.appex`

**20H392 donor**
- `root/root/System/Library/AppPlaceholders/Books.app/XPCServices/XPCUbiquityDisableService.xpc`
- `root/root/System/Library/AppPlaceholders/Health.app/Frameworks/HealthAppSupport.framework/PlugIns/HealthFollowUpExtension.appex`
- `root/root/System/Library/AppPlaceholders/Music.app/Frameworks/MusicApplication.framework/XPCServices/MusicScriptUpdateService.xpc`
- `root/root/System/Library/PrivateFrameworks/SmartChargingWidget.framework/PlugIns/SmartChargingWidget.appex`

## Target/donor comparison

### Matching method

A bundle identifier alone is not a unique record key in these filesystems.
The target has 82 identifiers that occur twice; the donor has 106. In 79 of
the target repeated-ID groups and 102 of the donor repeated-ID groups, the
copies span an AppPlaceholders location and an installed-application or
staged-application location.

For this comparison only, the key is the relative bundle path plus bundle
suffix, after removing repeated leading `root/` wrapper components from the
path. This compensates for differing extraction/mount wrapper depth in the
two reports. The original paths and `source_root` labels remain unchanged in
the uploaded JSON. The normalized key is unique within each report; no
ambiguous path matches were found.

| Path-level result | Count |
|---|---:|
| Common normalized bundle paths | 659 |
| Target-only normalized paths | 60 |
| Donor-only normalized paths | 196 |

### Differences on the 659 common paths

| Metadata field | Difference |
|---|---|
| `MinimumOSVersion` | 656 entries change from `15.8` (target) to `16.7` (donor) |
| `CFBundlePackageType` | `HearingMLHelperService.xpc`: `XPC!` (target) to `BNDL` (donor) |
| `MachServices` | `CAReportingService.xpc`: no declared names in target; donor declares two |
| `NSExtensionPointIdentifier` | `Diagnostic-8381.appex`: `com.apple.diagnostics-ui-service` to `com.apple.diagnostics-restricted-ui-service` |
| `NSExtensionPrincipalClass` | Two changes: GameCenter dashboard adds `GKDashboardExtensionViewController`; iCloud quota changes `ICQFollowupViewController` to `ICQFollowupViewController_iOS` |

The two MachServices names declared by the donor's
`CAReportingService.xpc` are:

- `com.apple.osanalytics.diagnosticmonitor`
- `com.apple.usernotifications.delegate.com.apple.coreaudio.audiocapturer.notification`

No target bundle in this report declares a MachServices name. The comparison
found no changed bundle identifier, executable filename, executable
presence-state, or supported-platform list on the 659 common paths.

## Interpretation limits

- `MinimumOSVersion` is a bundle declaration, not proof that an image is
  compatible with a different OS build or device.
- A present executable filename means only that a regular file with that name
  was present during the host-side scan. It does not validate its Mach-O
  structure, code signature, entitlements, ABI, or loadability.
- A `MachServices` dictionary is a declaration in a plist. It does not prove
  that launchd registered the name, that the service launched, or that a
  client uses it.
- A missing `.xpc` or `.appex` candidate in this scan does not prove absence
  from other volumes, Cryptexes, shared caches, or runtime-loaded content.
- The target and donor are different product generations and different iOS
  releases. The differences cannot be attributed to A10 versus A11 alone.
- This inventory does not establish which services are required by
  SpringBoard, whether dependencies resolve at runtime, or whether the
  desired system can boot.

The evidence is static, allowlisted Info.plist metadata only. The tool did not
read or execute bundle binaries and did not change the source files, device,
firmware, partitions, security state, or boot state. M6 remains in progress;
M7/SpringBoard has not started.

## Uploaded report hashes

SHA-256 values below identify the exact uploaded evidence files:

| File | SHA-256 |
|---|---|
| `19H422-embedded-services.json` | `689c5a2be1cde058061635f714dad87c465f1154dcd36eb3bafd616f05d352b3` |
| `20H392-embedded-services.json` | `56396b37dac5d59c831a41739061bbaf303b98821d25a3ec03f48375568517d9` |
| `embedded-services-results.tar.gz` | `9916d36a08f6cd12218d3acd0e52d44d6e2c8f42050bd103e2cc4ca9c9b46a74` |
