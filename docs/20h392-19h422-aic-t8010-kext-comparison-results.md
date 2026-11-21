# 19H422 target vs 20H392 donor AIC/T8010 KEXT comparison results

## Scope and provenance

This report records the user's read-only comparison output from the exact-ID
KEXT metadata tool, using:

- Target: iPhone 7 `iPhone9,1` / D10AP / iOS 15.8.8 / build `19H422`
- Donor: iPhone X `iPhone10,3` / D22AP / iOS 16.7.16 / build `20H392`

The inputs were the `ipsw kernel kext` JSON inventories, not extracted KEXT
executables. The physical iPhone 7 remains on iOS 12.1.4; neither inventory
represents firmware installed on that phone.

The comparison covers nine exact top-level bundle IDs. It compares selected
bundle metadata, a defined subset of IOKit personality keys, and serialized
`os_bundle_libraries` names/version strings.

## Summary

| Result | Count | Bundle IDs |
|---|---:|---|
| Present in target inventory | 9/9 | All selected IDs |
| Present in donor inventory | 3/9 | AppleInterruptController, AppleARMPlatform, AppleT8010SOCTuner |
| Target-only in these inventories | 6 | AppleT8010, AppleT8010CLPC, AppleT8010PCIe, AppleT8010PMPFirmware, AppleT8010PMGR, AppleT8010SmartIO |
| Donor-only in these inventories | 0 | None |

"Target-only" means no selected top-level record was found in the parsed
20H392 JSON. It does not establish absence from every donor filesystem,
another cache, or runtime source.

## Shared bundle comparison

### AppleInterruptController

Both inventories contain
`com.apple.driver.AppleInterruptController`. The target record reports
version `1.0.0d1`, short version `1.0.0`, minimum OS `15.8`, and
SDK `iphoneos15.8.internal`; the donor record reports SDK
`iphoneos16.7.internal` but omits several of those displayed fields,
including its version.

No differences were printed among the comparator's selected personality
fields. The serialized dependency names are shared, but target version
strings are populated while the donor values are empty:

- `com.apple.driver.AppleARMPlatform`: target `1.0.0`, donor empty
- `com.apple.kpi.bsd`, `iokit`, `libkern`, `mach`, `private`,
  `unsupported`: target `8.0`, donor empty

This is evidence that both exports contain the AIC bundle and corresponding
selected personality metadata. It does not prove binary identity, ABI
compatibility, IOKit attachment, or interrupt-controller operation.

### AppleARMPlatform

Both inventories contain `com.apple.driver.AppleARMPlatform`. The target
record reports version `1.0.2`; the donor record reports short version
`1.0.2` but omits the displayed `version` field and several platform
metadata fields.

Personality-name differences:

- Target-only: `AppleARMCHRPNVRAM`, `AppleARMNORNVRAM`
- Donor-only: `AppleARMNORNVRAM1`, `AppleARMNORNVRAM2`

Selected shared-personality differences:

- `AppleARMBootPerf.IOResourceMatch`: target `IOKit`, donor empty
- `AppleARMLightEmUp.IOProviderClass`: target `IOService`, donor empty
- `AppleARMPE.IOProbeScore`: target `1000`, donor `0`

Dependency names are shared in the displayed set. Target values include
`IOReportFamily=1.0`, `IOSlowAdaptiveClockingFamily=1.0`, and KPI
versions `8.0`; donor `com.apple.kpi.private` is `22.0`, while the
other listed KPI and family versions are empty in the export.

These differences make the target-native AppleARMPlatform metadata important
to preserve separately. They do not by themselves prove that one bundle is
incompatible with the other.

### AppleT8010SOCTuner

This bundle is present in both inventories. The target record reports version
`1`, short version `1.0`, and SDK `iphoneos15.8.internal`; the donor
record reports SDK `iphoneos16.7.internal` but omits the displayed version
fields.

No selected personality fields were printed for either record. Dependency
names are shared; the target reports `AppleARMPlatform=1.0.0`,
`ApplePMGR=1.0`, `IOReportFamily=1.0`, and KPI versions `8.0`,
whereas the donor values are empty in this export.

## Target-only T8010 platform bundle details

The following are the target-side personality declarations and direct
`os_bundle_libraries` records printed by the supplied 19H422 inventory.

### AppleT8010

Personalities:

| Personality | IONameMatch | IOProviderClass |
|---|---|---|
| AppleT8010IO | `arm-io,t8010` | `IOPlatformDevice` |
| AppleT8010MemCacheController | `mcc,t8010` | `AppleARMIODevice` |
| AppleT8010PlatformErrorHandler | `error-handler,t8010` | `AppleARMIODevice` |

Direct library declarations: `AppleARMPlatform=1.0.0`,
`AppleHurricaneErrorHandler=1.0`, `IOReportFamily=1.0`, plus
`com.apple.kpi.bsd`, `iokit`, `libkern`, `mach`, `private`, and
`unsupported` at `8.0`.

### AppleT8010CLPC

Personality:

| Personality | IONameMatch | IOProviderClass |
|---|---|---|
| AppleT8010CLPC | `clpc,t8010` | `ApplePMGRNub` |

The personality also reports bundle identifier
`com.apple.driver.AppleT8010CLPC` and match category
`IODefaultMatchCategory`.

Direct library declarations: `AppleARMPlatform=1.0.0`,
`ApplePMGR=1.0`, `IOReportFamily=1.0`, `IOSurface=52.6.0`,
`Libm=1.0.0`, and the six listed KPI libraries at `8.0`.

### AppleT8010PCIe

Personalities:

| Personality | IONameMatch | IOProviderClass |
|---|---|---|
| AppleNVMeMMU | `nvme-mmu,t8010` | `AppleARMIODevice` |
| AppleT8010PCIe | `apcie,t8010` | `AppleARMIODevice` |

Direct library declarations: `AppleARMPlatform=1.0.0`,
`AppleEmbeddedPCIE=1.0.0`, `IOPCIFamily=2.7`,
`IOReportFamily=1.0`, and the six listed KPI libraries at `8.0`.

### AppleT8010PMPFirmware

Personality:

| Personality | IOMatchCategory | IOPropertyMatch | IOProviderClass |
|---|---|---|---|
| AppleT8010PMPFirmware | `RTBuddyFirmwareService` | `role=PMP` | `RTBuddy` |

The personality also reports bundle identifier
`com.apple.driver.AppleT8010PMPFirmware`.

Direct library declarations: `AppleA7IOP=1.0`,
`AppleARMPlatform=1.0.0`, `IOSlaveProcessor=1.0.0`,
`RTBuddy=1.0.0`, `com.apple.kpi.iokit=8.0`, and
`com.apple.kpi.libkern=8.0`.

### AppleT8010PMGR

Personality:

| Personality | IONameMatch | IOProviderClass |
|---|---|---|
| AppleT8010PMGR | `pmgr1,t8010` | `AppleARMIODevice` |

Direct library declarations: `AppleARMPlatform=1.0.0`,
`ApplePMGR=1.0`, `Libm=1.0.0`, and the six listed KPI libraries
at `8.0`.

### AppleT8010SmartIO

Personalities:

| Personality | IOClass | IONameMatch | IOProviderClass |
|---|---|---|---|
| AppleSmartIO | AppleSmartIO | `iop-nub,sio` | `AppleA7IOPNub` |
| AppleSmartIODMA | AppleSmartIODMAController | — | `AppleSmartIODMANub` |

The DMA personality also reports `IOMatchCategory=DMA`.

Direct library declarations: `AppleA7IOP=1.0.0`,
`IOSlaveProcessor=1.0.0`, `IOCryptoAcceleratorFamily=1.0.0`,
and KPI libraries `bsd`, `iokit`, `libkern`, `mach`, and
`private` at `8.0`. The supplied record does not list
`com.apple.kpi.unsupported` for this bundle.

## Interpretation and next research boundary

The target metadata exposes a platform dependency cluster involving
`AppleARMPlatform`, `ApplePMGR`, `AppleA7IOP`,
`IOSlaveProcessor`, `RTBuddy`, `AppleEmbeddedPCIE`,
`IOPCIFamily`, `IOSurface`, `IOCryptoAcceleratorFamily`,
`IOReportFamily`, and KPI libraries. These are serialized direct dependency
declarations, not a proven load order or transitive dependency graph.

The next useful host-side evidence is a separate exact-ID inventory of the
supporting KEXTs named above, in both 19H422 and 20H392. That will establish
which supporting bundle records and personalities each JSON export contains.
It still will not establish executable ABI compatibility or runtime provider
attachment.

Caveats:

- Empty donor dependency version strings are not treated as missing
  dependencies or ABI mismatches.
- Omitted donor bundle fields are not treated as zero or as proof of
  incompatibility.
- Version and personality metadata do not establish binary equivalence.
- No proprietary KEXT implementation, private KPI contract, runtime
  IOKit attachment, hardware function, interrupt behavior, or bootability
  is established by this report.
- No device, firmware, partition, or boot state was accessed or modified.

## Supporting dependency comparison results (20 selected IDs)

The user ran the expanded comparator after PR #89. The supplied terminal
output reports:

| Result | Count |
|---|---:|
| Core AIC/T8010 IDs selected | 9 |
| Supporting dependency IDs selected | 11 |
| Total selected IDs | 20 |
| Present in target 19H422 JSON | 20/20 |
| Present in donor 20H392 JSON | 13/20 |

Because the original nine core IDs contain 9 target records and 3 donor
records, all 11 supporting IDs are present in the target JSON and 10 of
the 11 are present in the donor JSON. The follow-up status output identifies
`com.apple.driver.AppleHurricaneErrorHandler` as the sole supporting ID
reported absent from the selected donor top-level JSON inventory.

| Supporting bundle ID | Target 19H422 | Donor 20H392 |
|---|---|---|
| `com.apple.driver.ApplePMGR` | Present | Present |
| `com.apple.driver.AppleA7IOP` | Present | Present |
| `com.apple.driver.IOSlaveProcessor` | Present | Present |
| `com.apple.driver.RTBuddy` | Present | Present |
| `com.apple.driver.AppleEmbeddedPCIE` | Present | Present |
| `com.apple.driver.AppleHurricaneErrorHandler` | Present | Absent from this JSON inventory |
| `com.apple.iokit.IOPCIFamily` | Present | Present |
| `com.apple.iokit.IOSurface` | Present | Present |
| `com.apple.kec.Libm` | Present | Present |
| `com.apple.iokit.IOCryptoAcceleratorFamily` | Present | Present |
| `com.apple.iokit.IOReportFamily` | Present | Present |

The supplied status listing repeats the AppleHurricaneErrorHandler heading
and also prints `unavailable (no selected top-level record)`. This is
recorded as the same top-level inventory limitation, not as a second missing
dependency. The earlier detailed excerpt still provides full metadata
comparisons for only Libm, IOCryptoAcceleratorFamily, and IOReportFamily;
the other eight supporting sections have presence status but are not
transcribed in this appendix.

“Absent from this JSON inventory” means no selected top-level record was
found by this exact-ID comparison. It does not establish that the donor
filesystem contains no equivalent implementation, that the functionality
is absent, or that no renamed/repackaged component exists.

### Libm

Both inventories contain `com.apple.kec.Libm` at
`/System/Library/Extensions/Libm.kext`. The target record reports
`name=Libm.kext`, `executable=Libm`, `version=1`,
`short_version_string=1.0`, and `compatible_version=1.0.0d0`.
The donor record also reports `name=Libm.kext` and the same
`compatible_version=1.0.0d0`; several other displayed fields are
omitted from the donor export. No selected IOKit personality differences
were printed. The dependency name `com.apple.kpi.libkern` is present on
both sides, with target value `8.0.0d0` and empty donor value.

### IOCryptoAcceleratorFamily

Both inventories contain `com.apple.iokit.IOCryptoAcceleratorFamily`.
The target reports version and short version `1.0.1`, compatible
version `1.0b1`, and minimum OS `15.8`; the donor reports short
version `1.0.1` and the same compatible version `1.0b1`, while
several other displayed fields are omitted. No selected IOKit personality
differences were printed. The dependency names are shared in the displayed
set; the donor values are empty where the target reports KPI versions
`8.0`.

### IOReportFamily

Both inventories contain `com.apple.iokit.IOReportFamily`. The target
reports version `47`, short version `1.0`, compatible version
`1.0`, and minimum OS `15.8`; the donor reports version `47`,
while several other displayed fields are omitted.

The shared `IOReportHub` personality differs in two selected fields:

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| `IOProviderClass` | `IOResources` | empty string |
| `IOResourceMatch` | `IOKit` | empty string |

The other selected fields printed for this personality match. The target
dependency map reports KPI versions `8.0`; the donor names are present
with empty version values in the serialized export.

### Interpretation

These three examples illustrate why an empty donor field must not be
translated into a negative compatibility conclusion. The Libm compatible
version is identical in both exports; IOCryptoAcceleratorFamily has matching
short/compatible versions; and IOReportHub retains the same class, match
category, and user-client class while the donor export leaves two provider/
resource-match fields empty.

An empty string in this JSON comparison is recorded as an empty string, not
as proof of a missing dependency or a zero-valued property. Likewise,
omitted bundle fields are not treated as values. The differences merit
target-side preservation and further static inspection, but do not establish
a behavioral or binary incompatibility.

The follow-up presence listing resolves the donor-side selected
top-level omission as `com.apple.driver.AppleHurricaneErrorHandler`.
Detailed metadata for the other eight supporting-bundle sections remains
untranscribed; only their target/donor presence status is recorded here.
The selected-inventory finding is not a filesystem-wide absence claim.
