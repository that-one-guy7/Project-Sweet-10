# 19H422 / 20H392 AppleA7IOP and AppleEmbeddedTempSensor recursive metadata diff

## Scope and provenance

This note records the user-supplied recursive JSON diff for two exact-ID
KEXT pairs from the parsed inventories:

- Target: iPhone 7 `iPhone9,1` / D10AP / iOS 15.8.8 / `19H422`
- Donor: iPhone X `iPhone10,3` / D22AP / iOS 16.7.16 / `20H392`

The diff compared complete selected top-level JSON objects recursively.
It reports changed JSON paths, distinguishes an omitted key from an empty
string, and preserves array indexes and JSON types. It did not inspect KEXT
executable bytes or runtime properties.

## Summary

| Pair | Reported differing JSON paths | Most relevant observation |
|---|---:|---|
| AppleA7IOP | 25 | No differences were emitted under `io_kit_personalities`; the target and donor personality trees are identical in this parsed output |
| AppleEmbeddedTempSensor | 45 | T8010 match strings remain the same; most personality differences are exported empty strings for `IOResourceMatch` and `IOProbeScore` |

The counts are the number of distinct paths printed by the supplied diff.
They are not counts of incompatible fields, missing functions, or runtime
problems.

## 1. AppleA7IOP — 25 differing paths

### Personality metadata

**No differences were emitted under `io_kit_personalities`.** In this
comparison, the complete serialized personality subtree was identical
between the target and donor records, including:

- `AppleA7IOPV2-GFX` with `iop-gfx,t8010`
- The other V2 personality matches, including s8000/t8011 variants
- The T8015 V4, V4-GFX, V4-PMP and ASC-ANS2 personality entries
- The displayed `IOClass` and `IOProviderClass` values

This is stronger evidence than a simple keyword hit: the 20H392 parsed
AppleA7IOP record retains the same serialized multi-generation personality
configuration as the 19H422 record. It still does not prove that the donor
executable implements the same code paths or can operate on T8010 hardware.

### Breakdown of the 25 reported paths

| Difference category | Count | Examples |
|---|---:|---|
| Target key absent from donor export | 15 | `version`, `compatible_version`, `minimum_os_version`, `platform_build`, `xcode_build` |
| Load-address field differs | 1 | `executable_load_addr` |
| SDK value differs | 1 | Target `iphoneos15.8.internal`; donor `iphoneos16.7.internal` |
| Dependency version values differ | 6 | AppleARMPlatform, IOSlaveProcessor, and four KPI entries |
| Platform/capability array entry differs | 2 | `supported_platforms[0]`, `ui_required_device_capabilities[0]` |
| **Total** | **25** | |

The six dependency IDs are present by name in both records, but the donor
export serializes their version strings as empty values where the target
contains version strings. This is not a top-level dependency absence.

The target-only metadata fields also include build-machine/build-tool
details, package/platform labels, version strings, and the serialized
signature placeholder `????`. These target fields are not present in the
selected donor JSON record; that absence is not interpreted as a missing
binary feature.

The different `executable_load_addr` values are recorded as a difference
in the parsed metadata. Their meaning for executable layout, relocation, or
runtime mapping has not been independently established.

## 2. AppleEmbeddedTempSensor — 45 differing paths

### Personality metadata retained

The target and donor records preserve the same displayed personality names,
`IOClass` values, `IONameMatch` entries, provider classes, user-client
class values, and numeric platform action values. In particular, both retain
the T8010 match entries:

- `AppleDieTempController`: `dietempctl,t8010`
- `AppleT700XTempSensor`: `tempsensor,t8010`
- `AppleVTempDispatcher`: `vtempctl,t8010`

The donor also retains the T8015-specific personality entries. This
demonstrates that the T8010 match strings survive in the donor's serialized
personality map; it does not prove that the T8010 sensor code remains
operational or that the kernel will attach the personalities.

### Breakdown of the 45 reported paths

| Difference category | Count | Examples |
|---|---:|---|
| Target key absent from donor export | 18 | Build metadata, minimum OS, package/platform fields, `os_bundle_required`, version/tool fields |
| Load-address field differs | 1 | `executable_load_addr` |
| SDK value differs | 1 | Target `iphoneos15.8.internal`; donor `iphoneos16.7.internal` |
| Personality fields differ | 17 | Eight `IOProbeScore` paths and nine `IOResourceMatch` paths |
| Dependency version values differ | 8 | AppleARMPlatform, IOHIDFamily, IOReportFamily, and five KPI entries |
| **Total** | **45** | |

For the 17 personality paths, the target has
`IOResourceMatch=IOKit` and/or `IOProbeScore=100`; the donor JSON
contains empty strings for those corresponding fields. The
`AppleT700XTempSensor.IOProbeScore=100` field is the exception among the
printed probe-score values and matches on both sides. The empty strings
remain serialized export values, not interpreted runtime settings.

All eight dependency names are present on both sides; the donor's serialized
dependency version values are empty. The output does not show those
dependencies missing as top-level records.

## Interpretation

These two comparisons make AppleA7IOP particularly interesting for further
static source and binary-format research: the donor retains the full
T8010-specific personality subtree in the parsed metadata with no
personality-path differences. AppleEmbeddedTempSensor similarly retains its
T8010 personality matches, although the parsed donor export differs in
several selected empty-valued properties.

Neither result proves that the 20H392 binaries are drop-in replacements for
19H422 or compatible with the iPhone 7's XNU, DeviceTree, firmware, private
KPI interfaces, or hardware. In particular:

- Parsed Info.plist/personality equality does not mean executable equality.
- An empty plist-export value is not assumed to be the runtime value.
- An omitted build metadata key is not treated as missing code.
- A differing `executable_load_addr` is not, by itself, an ABI conclusion.
- No driver was loaded and no provider attachment or hardware behavior was
  tested.

## Next bounded step

Use the repository's recursive comparator for the remaining five
cross-generation pairs in the same run:

- AppleT8010 / AppleT8015
- AppleHurricaneErrorHandler / AppleMonsoonErrorHandler
- AppleMobileDispH9P / AppleMobileDispH10P
- AGXG9P / AGXG10P
- AppleH9CameraInterface / AppleH10CameraInterface

Those pairs will complete the selected seven-pair metadata crosswalk. Keep
the platform-specific match strings intact and report exact JSON paths;
do not infer that a T8015 personality or binary is usable on T8010.

## Evidence boundary

- This is parsed JSON metadata only, supplied by the user.
- No executable bytes, private KPI/ABI contracts, kernel symbols, or runtime
  IOKit registry state were inspected.
- No hardware function, driver attachment, kernel boot, launchd start, or
  SpringBoard result is established.
- No device, firmware, partition, or boot state was accessed or changed.
- The physical iPhone 7 remains on iOS 12.1.4; M1 remains in progress and
  M7/SpringBoard has not started.
