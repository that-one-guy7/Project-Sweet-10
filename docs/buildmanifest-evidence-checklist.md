# BuildManifest evidence checklist (read-only)

## Purpose

This document defines the metadata needed to identify a specific restore
artifact before drawing any conclusions about its kernel or platform. It is a
static research checklist, not a restore or boot procedure.

The selected reference remains iOS 16.7.16 build `20H392`. The hardware
research target remains `iPhone9,1 / D10AP / T8010`. An iPhone 8/X donor
image must retain its own product and board identity throughout the analysis.

## Why the manifest matters

An IPSW is a container for multiple components. The BuildManifest describes
build identities and component metadata; kernelcache and DeviceTree are
device-specific artifacts rather than generic files selected by build number
alone. The IPSW format reference describes these as distinct components, and
the `idevicerestore` implementation explicitly reads the `BuildIdentities`
array and obtains component paths from a selected identity.

References:
- [The Apple Wiki: IPSW file format](https://theapplewiki.com/wiki/IPSW_File_Format)
- [idevicerestore: BuildManifest identity handling](https://cgit.libimobiledevice.org/idevicerestore.git/tree/src/idevicerestore.c?id=4852a4301af71a99f3ba7e0bc23599a8ea763cc6)
- [Anatomy of an IPSW](https://isitanth.github.io/blog/anatomy-ipsw/)

## Required evidence record

For each candidate donor IPSW, record the following directly from its own
manifest and archive metadata. If a field is absent, record **not present**;
do not infer or fill it from another model's image.

| Evidence item | What to record | Why it matters |
|---|---|---|
| Archive identity | Exact IPSW filename, source page, archive size, and SHA-256 if independently calculated | Prevents confusing similarly named builds or mirrors |
| Product build | `ProductVersion` and `ProductBuildVersion` | Confirms the OS release/build represented by the manifest |
| Build identity | The exact selected `BuildIdentities` array entry/index | A manifest may contain multiple identities |
| Device identity | `Info.DeviceClass`, `SupportedProductTypes`, `ApBoardID`, and `ApChipID`, where present | Ties the identity to its intended device/board/chip |
| Kernel component | `Manifest.KernelCache` metadata, including its `Info.Path` and any recorded digest/size fields | Identifies the exact kernelcache component |
| DeviceTree component | `Manifest.DeviceTree` metadata, including its `Info.Path` and any recorded digest/size fields | Separately identifies the platform tree |
| Provenance | Tool/version used to read the plist and date of inspection | Makes the result repeatable |

Do not assume that every manifest has identical optional fields or that the
first array entry is the desired identity. Preserve the full identity context
when recording a component path.

## Comparison rules for Project Sweet-10

1. A candidate donor must explicitly identify its own product type and board.
2. A `20H392` build-number match is necessary for the chosen userland reference,
   but is not sufficient to identify a compatible kernelcache.
3. Do not copy a donor's `KernelCache`, `DeviceTree`, or `BuildManifest`
   into an `iPhone9,1` target record.
4. Keep the target identity row separate from donor rows. If there is no
   iPhone9,1 / T8010 manifest evidence, mark it **not established**.
5. A matching XNU source tag is only a source candidate. It does not by itself
   prove that the source revision generated a particular released kernelcache.
6. Record hashes as measurements of the exact files examined. A filename,
   download page, or build label is not a substitute for a digest.

## Current evidence status

| Item | Status |
|---|---|
| 20H392 release/build reference | Selected |
| Indexed donor product families | Six iPhone 8/X product types documented in the restore identity audit |
| Exact donor BuildManifest contents | Not yet inspected |
| Exact donor KernelCache path and digest | Not yet inspected |
| Exact donor DeviceTree path and digest | Not yet inspected |
| Apple XNU source-to-kernelcache mapping | Not established |
| iPhone9,1 / T8010 iOS 16 manifest and kernelcache | Not established |
| iPhone9,1 platform or boot compatibility | Not established |

## Conclusion

The next evidence milestone is a per-IPSW manifest record, not a device boot
attempt. Until the exact manifest identity and component metadata are available,
the project must continue to label `20H392` as a userland reference and must
not claim that any donor kernelcache is an iPhone 7 kernel.
