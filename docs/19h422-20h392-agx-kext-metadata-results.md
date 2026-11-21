# iPhone9,1 19H422 / iPhone10,3 20H392 graphics KEXT metadata results

## Scope and provenance

This report records the user-supplied output of
`tools/inspect_graphics_kext_metadata.py` for three exact top-level KEXT
record pairs:

- Target reference: iPhone 7 `iPhone9,1` / D10AP / A10-T8010,
  iOS 15.8.8 build `19H422`.
- Donor reference: iPhone X `iPhone10,3` / D22AP / A11-T8015,
  iOS 16.7.16 build `20H392`.

All three selected records are reported PRESENT in both parsed JSON
inventories. The source is the selected metadata output pasted by the user;
this report does not independently re-read the local inventory files.

The physical iPhone 7 remains on iOS 12.1.4. The 19H422 IPSW and 20H392
IPSW/cache files are host-side reference artifacts only. This is parsed
KEXT metadata, not an executable, ABI, dyld runtime, IOKit attachment,
GPU initialization, rendered-output, kernel boot, or SpringBoard test.

## Summary

| Record pair | Target 19H422 | Donor 20H392 | Main observation |
|---|---|---|---|
| GPU accelerator | `com.apple.AGXG9P` | `com.apple.AGXG10P` | Different SoC matches, accelerator classes, and Metal plugin labels |
| GPU framework family | `com.apple.iokit.IOGPUFamily`, version `35.29` | Same ID, version `65.60.1` | Same selected dependency-ID set; different version and SDK metadata |
| Graphics I/O processor | `com.apple.driver.AppleA7IOP` | Same ID | Displayed personality maps match, including `iop-gfx,t8010` |

## 1. AGX accelerator: target AGXG9P versus donor AGXG10P

Both selected top-level records are present, but they describe different
accelerator generations and hardware matches.

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| Bundle ID | `com.apple.AGXG9P` | `com.apple.AGXG10P` |
| Bundle path | `/System/Library/Extensions/AGXG9P.kext` | `/System/Library/Extensions/AGXG10P.kext` |
| Reported executable field | `AGXG9P` | Not present in supplied selected output |
| Personality names | `AGXG9P_A0`, `AGXG9P_B0` | `AGXG10P_A0`, `AGXG10P_B0` |
| Accelerator classes | `AGXAcceleratorG9P_A0/B0` | `AGXAcceleratorG10P_A0/B0` |
| `IONameMatch` | `gpu,t8010` | `gpu,t8015` |
| Provider class | `AppleARMIODevice` | `AppleARMIODevice` |
| `IOGLESBundleName` | `AppleMetalGLRenderer` | `AppleMetalGLRenderer` |
| `IOMatchCategory` | `IOAcceleratorES` | `IOAcceleratorES` |
| Metal plugin label(s) | `AGXMetalA10` on A0 and B0 | A0: `AGXMetalG10A0`; B0: `AGXMetalA11` |
| `IOSourceVersion` | `190.23` on A0 and B0 | Empty strings |
| Record version | `190.23` | Not present in supplied selected output |
| Minimum OS | `15.8` | Not present in supplied selected output |
| SDK | `iphoneos15.8.internal` | `iphoneos16.7.internal` |

The records share some high-level personality properties, including the
provider class, GL renderer bundle label, and match category. The
hardware-specific parts are different: the target record matches
`gpu,t8010` and names `AGXMetalA10`; the donor record matches
`gpu,t8015` and names two different Metal plugin labels.

### AGX dependency identities

The selected `os_bundle_libraries` maps contain the same 14 dependency
IDs in the target and donor exports:

- `com.apple.driver.AppleARMPlatform`
- `com.apple.driver.AppleMobileFileIntegrity`
- `com.apple.driver.RTBuddy`
- `com.apple.iokit.CoreAnalyticsFamily`
- `com.apple.iokit.IOGPUFamily`
- `com.apple.iokit.IOReportFamily`
- `com.apple.iokit.IOSurface`
- `com.apple.kec.Libm`
- `com.apple.kpi.bsd`
- `com.apple.kpi.iokit`
- `com.apple.kpi.libkern`
- `com.apple.kpi.mach`
- `com.apple.kpi.private`
- `com.apple.kpi.unsupported`

The target export supplies version strings for these dependencies. The
donor export serializes all 14 values as empty strings. This is a difference
in the supplied JSON metadata; it is not evidence that a donor dependency
is absent at runtime or that its ABI is incompatible.

**Assessment:** the donor AGXG10P record is not shown matching the
T8010 GPU node. The shared renderer/category fields and dependency-ID set
are useful inventory observations, but they do not bridge the explicit
T8010/T8015 accelerator-class and Metal-plugin differences. Do not treat
AGXG10P as a drop-in AGXG9P implementation.

## 2. IOGPUFamily: same bundle ID, different build metadata

Both inventories contain `com.apple.iokit.IOGPUFamily` at
`/System/Library/Extensions/IOGPUFamily.kext`, with executable field
`IOGPUFamily`.

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| Version | `35.29` | `65.60.1` |
| Compatible version | `2.0.0` | Not present in supplied selected output |
| Minimum OS | `15.8` | Not present in supplied selected output |
| SDK | `iphoneos15.8.internal` | `iphoneos16.7.internal` |

Both selected `os_bundle_libraries` maps contain the same 10 IDs:

- `com.apple.driver.AppleARMPlatform`
- `com.apple.driver.AppleMobileFileIntegrity`
- `com.apple.iokit.IOReportFamily`
- `com.apple.iokit.IOSurface`
- `com.apple.kpi.bsd`
- `com.apple.kpi.iokit`
- `com.apple.kpi.libkern`
- `com.apple.kpi.mach`
- `com.apple.kpi.private`
- `com.apple.kpi.unsupported`

The target values are populated. All 10 donor values are empty strings
in the supplied JSON. The matching dependency-ID set is not proof of
matching binary interfaces or dependency versions.

**Assessment:** IOGPUFamily is a shared bundle family across the two
inventories, but the reported build versions differ and the exports are
from different iOS releases. No API/export or binary comparison has yet
been performed for this KEXT.

## 3. AppleA7IOP: donor retains the T8010 graphics-IO personality

Both inventories contain `com.apple.driver.AppleA7IOP` at
`/System/Library/Extensions/AppleA7IOP.kext`. The target reports version
`1.0.2`; the donor's selected output does not contain a version field.
The target SDK is `iphoneos15.8.internal`; the donor SDK is
`iphoneos16.7.internal`.

The supplied target and donor JSON show the same 17 displayed personality
names and matching `IOClass`, `IONameMatch`, and
`IOProviderClass=AppleARMIODevice` values. The graphics-related entry is:

| Personality | IOClass | IONameMatch |
|---|---|---|
| `AppleA7IOPV2-GFX` | `AppleA7IOPV2GFX` | `iop-gfx,s8000`, `iop-gfx,t8010`, `iop-gfx,t8011` |

Both exports also retain the T8015-generation `AppleA7IOPV4-GFX`
personality with `IONameMatch=iop-gfx,t8015`, alongside other V4/ASC
personalities.

The six selected dependency IDs are identical in both exports:

- `com.apple.driver.AppleARMPlatform`
- `com.apple.driver.IOSlaveProcessor`
- `com.apple.kpi.bsd`
- `com.apple.kpi.iokit`
- `com.apple.kpi.libkern`
- `com.apple.kpi.mach`

The target export has populated version strings; all six donor values
are empty strings.

**Assessment:** this is a positive cross-generation metadata observation:
the donor AppleA7IOP record retains the T8010 `iop-gfx` personality.
However, AppleA7IOP is a separate graphics-I/O-processor KEXT. Its
`iop-gfx,t8010` match is not the AGX accelerator's `gpu,t8010`
match, and it does not override the donor AGXG10P record's
`gpu,t8015` requirement. The personality does not establish that the
donor executable contains a functional T8010 path or is compatible with
the target XNU and firmware interfaces.

## Overall interpretation

1. **Target-specific AGX evidence remains decisive.** The target has an
   AGXG9P/T8010 record with `AGXMetalA10`; the donor has an
   AGXG10P/T8015 record with `AGXMetalG10A0` / `AGXMetalA11`.
2. **AppleA7IOP is the strongest shared metadata lead.** Its donor record
   retains the target's displayed T8010 graphics-IO personality. This is
   distinct from the AGX GPU accelerator and is not proof of GPU support.
3. **IOGPUFamily is a shared bundle family, not a demonstrated compatible
   build.** Its selected version strings differ (`35.29` versus
   `65.60.1`), and the target/donor SDKs differ.
4. **Matching dependency IDs are not compatibility evidence.** Empty
   donor dependency values are preserved as export values and are not
   interpreted as missing runtime dependencies.

## Next bounded static work

Use the [AGX and Metal userland audit plan](19h422-20h392-agx-metal-userland-audit-plan.md)
to inventory the exact target and donor dyld cache image paths for Metal,
CoreGraphics, IOSurface, IOKit, IOMobileFramebuffer, IOGPU-related images,
and any AGX Metal plugin images actually listed by each cache. Then inspect
the corresponding PrebuiltLoaderSet records where the parser exposes them.

The next comparison should record exact install paths, image-list versions
and Mach-O UUIDs, loader dependency paths and kinds, and query status.
Do not infer a dyld install path from a `MetalPluginName` string. Keep
image-list indexes separate from loader reference indexes, and preserve
weak-link/re-export distinctions.

## Evidence boundaries

- This report is based on the user's supplied selected KEXT JSON output.
- A top-level record being present in an inventory does not prove its
  executable was loaded or attached to a live provider.
- Personality matches are metadata, not runtime IOKit registry results.
- Shared dependency IDs do not prove private KPI/ABI compatibility.
- Empty strings and omitted fields are observations about the JSON export,
  not proof of runtime absence.
- No KEXT executable, dyld cache binary, IPSW/DMG, or device was modified.
- No device, firmware, partition, activation/security, or boot state was
  accessed or changed.
- The physical iPhone 7 remains on iOS 12.1.4.
- M6 remains in progress; M7/SpringBoard has not started.
