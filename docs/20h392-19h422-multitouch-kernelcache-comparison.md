# 20H392 donor versus 19H422 target multitouch KernelCache comparison

## Purpose and evidence boundary

This report compares the user's host-side static inspection of two actual
KernelCache components:

- Donor reference: iPhone X, `iPhone10,3` / D22AP / A11-T8015,
  iOS 16.7.16 build 20H392.
- Target hardware reference: iPhone 7, `iPhone9,1` / D10AP / A10-T8010,
  iOS 15.8.8 build 19H422.

The physical iPhone 7 remains on iOS 12.1.4. Neither KernelCache was installed
on the phone. This is a static metadata comparison, not a boot or driver
porting procedure. It does not prove that donor KEXTs can initialize T8010,
that a provider attaches, or that touch works.

## KernelCache identities

| Field | Target reference: 19H422 / iPhone9,1 | Donor reference: 20H392 / iPhone10,3 |
|---|---|---|
| Board / SoC | D10AP / A10-T8010 | D22AP / A11-T8015 |
| Darwin | 21.6.0 | 22.6.0 |
| XNU version string | `xnu-8020.241.44~1` | `xnu-8796.142.1.703.8~1` |
| Kernel build target | `RELEASE_ARM64_T8010` | `RELEASE_ARM64_T8015` |
| SHA-256 | `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee` | `2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221` |
| File identification | Mach-O 64-bit ARM64 executable | Mach-O 64-bit ARM64 executable |
| KEXT listing | 230 entries | Four requested multitouch/HID bundles found |

The donor KernelCache was extracted from
`iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw` with ipsw 3.1.749,
using the `iPhone10,3` device selector. The extracted component path was
`20H392__iPhone10,3/kernelcache.release.iPhone10,3_6`.

The donor version string is an observed kernel identity. It does not prove
that the repository's pinned public XNU candidate `xnu-8796.141.3` is the
exact source revision used to build this KernelCache. Source-to-binary
mapping remains open.

## Bundle and personality comparison

The user supplied the JSON records for
`AppleHIDTransport`, `AppleHIDTransportSPI`,
`AppleMultitouchSPI`, and `AppleMultitouchDriver` from both KernelCaches.

| Item | 19H422 target | 20H392 donor | Static interpretation |
|---|---|---|---|
| `AppleHIDTransportSPI` bundle | Version `5100.32`; nested below `AppleHIDTransport.kext` | Same bundle ID/path; JSON reports SDK `iphoneos16.7.internal`; individual version field not emitted | Bundle identity and hierarchy are consistent; donor version is not available in the supplied JSON |
| SPI HID personality | `AppleHIDTransportDeviceSPI`, provider `AppleARMSPIDevice`, matches `hid-transport,k1` and `hid-transport,spi` | Same class, provider, and two `IONameMatch` values | Exact personality-name metadata is retained in the donor |
| `AppleMultitouchSPI` bundle | Version `5100.27`; filesystem contains nested plugin metadata | Version `6140.3`; same bundle identifier and plugin path | A reported version difference; not a compatibility verdict |
| `AppleMultitouchDriver` bundle | Version `5100.27`; `IOHIDInterface` personalities reference plugin type UUID | Same bundle ID; JSON reports SDK `iphoneos16.7.internal`; individual version field not emitted | Same broad HID/plugin relationship; donor version is not available in the supplied JSON |
| Plugin type UUID in `IOCFPlugInTypes` | `0516B563-B15B-11DA-96EB-0014519758EF` | `0516B563-B15B-11DA-96EB-0014519758EF` | Exact static type-UUID match across the two KernelCache reports |
| `0x0D/0x04` service `parser-options` | `0` | `16` | Concrete personality-property difference; operational effect not established |
| `0x0D/0x04` service `parser-type` | `0` | `0` | Same reported value |
| Vendor usage `0xFF60/0x1002` `IOProbeScore` | `0` | `1500` | Concrete probe-score difference; its runtime selection effect is not established |
| `0x0D/0x20` timestamp sync | `Timestamp Sync = true` | `Timestamp Sync = true` | Same reported property |

The vendor-usage personality's target metadata reports
`IOProbeScore = 0`, while the donor reports `1500`. The donor's
`Manufacturer` field is empty for some personalities for which the target
output reports `Apple`. These are recorded as raw metadata differences only;
they are not interpreted as proof of which service will match a real device.

### Fields not available in the donor JSON

For `AppleHIDTransport`, `AppleHIDTransportSPI`, and
`AppleMultitouchDriver`, the supplied donor JSON did not emit an individual
KEXT `version` field or a `minimum_os_version` field. The records do report
SDK `iphoneos16.7.internal`. An omitted field or empty string in this
KernelCache JSON must not be treated as numeric zero, an explicit minimum OS,
or proof that the underlying bundle plist lacks the field.

The donor `AppleMultitouchSPI` record did emit version `6140.3`. Its
`io_kit_personalities` field was not present in the supplied JSON, consistent
with the already documented ipsw JSON serialization boundary; no absence
claim is made about filesystem plugins or related services.

## Plugin type-UUID cross-reference

The 19H422 target filesystem's extracted
`AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/Info.plist` declares:

- Bundle ID: `com.apple.iokit.plugin.MultitouchHID`.
- Version: `5100.27`.
- Minimum OS: `15.8`.
- Platform: `iPhoneOS`.
- Plug-in type UUID: `0516B563-B15B-11DA-96EB-0014519758EF`.
- Factory UUID: `0CB0FBB9-15EA-11DB-A93C-001451D47183`.
- Factory function: `IOHIDPlugInFactory`.

Both target and donor `AppleMultitouchDriver` KernelCache personality
records reference the same plug-in type UUID in their
`IOCFPlugInTypes` dictionaries. The donor's own filesystem plugin
`Info.plist` has now also been inspected. It independently confirms bundle
`com.apple.iokit.plugin.MultitouchHID`, version `6140.3`, minimum OS
`16.7`, platform `iPhoneOS`, the same type UUID, factory UUID, and
`IOHIDPlugInFactory` function as the target's 19H422 plugin. The donor
plist is 1,126 bytes with SHA-256
`6700b351288f1420754edcc8107a118b935d7ce250653f737ff448f9ddb7f3b1`.
The target plugin is version `5100.27` with minimum OS `15.8`. See the
[donor plugin audit](20h392-multitouch-plugin-audit.md) for the field-by-field
comparison.



## Plugin executable availability

A subsequent user-side directory check found no file or symlink named
`MultitouchHID*` anywhere under either searched 20H392 donor mount root:
`$HOME/20H392/mnt/root/root` and
`$HOME/20H392/systemos-mnt/root/root`. The donor plugin directory itself
contains only `Info.plist` and
`_CodeSignature/CodeResources`. A follow-up plist inspection confirmed
`CFBundleExecutable=MultitouchHID`. Its `CodeResources` plist has top-level
keys `files`, `files2`, `rules`, and `rules2`; the printed `files` and
`files2` entries were both empty. This is a manifest-structure observation,
not code-signature verification. The complete 19H422 target filesystem DMG was subsequently mounted
read-only at `$HOME/19H422-full-fs-mount`. The user verified
`root/System/Library/Extensions` exists and searched the complete mount
for regular files and symlinks whose case-insensitive names match
`MultitouchHID*`. No paths were returned. This closes the full-filesystem
search for that filename pattern within the mounted 19H422 filesystem DMG;
it does not cover other IPSW components or unmounted/shared-cache images.

Consequently, both compiled plugin images are confirmed as
entries in their respective dyld shared-cache inventories, despite no
standalone `MultitouchHID*` file being returned by the searched filesystem
mounts:

| Field | 19H422 target | 20H392 donor |
|---|---|---|
| Image-list index | 1948 | 2557 |
| Source version | `5100.27.0.0.0` | `6140.3.0.0.0` |
| Mach-O UUID | `304953E6-6B67-3CF1-B7CA-E011978210DE` | `78E1FB55-113A-3500-9D2D-1D8E282BED45` |
| Load address | `7982772224` | `8757542912` |

The donor UUID record came from the user's successful
`ipsw dyld info --dylibs --json` query. The preceding
`ipsw dyld image -V` command returned a PrebuiltLoaderSet record rather
than the image UUID. The different UUIDs establish different Mach-O build
identifiers, not a compatibility verdict. The actual Mach-O bytes have not
been separately extracted or compared. A dyld image entry is stronger
than plist-only metadata but is not signature validation or runtime proof.
The mere presence of `CodeResources` does not verify a code signature.

## Interpretation

The comparison establishes three useful facts:

1. The donor and target KernelCaches both include the same named HID/SPI and
   multitouch KEXT families, and the SPI transport personality reports the
   same `hid-transport,k1` and `hid-transport,spi` name matches.
2. The `AppleMultitouchDriver` plugin-type UUID is identical in the target
   and donor KernelCache personality metadata, and it matches the type UUID
   declared by the already extracted 19H422 plugin Info.plist.
3. The bundles are not metadata-identical: the target
   `AppleMultitouchSPI` reports `5100.27`, the donor reports `6140.3`,
   and selected multitouch personality properties differ, including
   `parser-options` and vendor-usage `IOProbeScore`.

These facts do not establish source or binary compatibility. The donor is
A11/T8015 and its KernelCache reports XNU 8796.142.1.703.8; the target is
A10/T8010 and its stock reference KernelCache reports XNU 8020.241.44.
The repository's separate public-XNU review found that the pinned XNU
8796.141.3 ARM64 machine allowlist omits T8010. A matching plugin UUID cannot
resolve that platform gap or prove that the donor kernel can provide the
target's SPI device, clocks, interrupts, DMA, power, or HID service graph.

No driver is described here as drop-in or interchangeable. Runtime matching,
plugin loading, touch-event delivery, and display operation remain untested.

## Target-native loader dependency comparison

The target and donor caches both returned a PrebuiltLoaderSet record for
the same full `MultitouchHID` install path. The user supplied both outputs.
The command status for the 19H422 target was `0`.

| Field | 19H422 target (iPhone9,1 / T8010) | 20H392 donor (iPhone10,3 / T8015) |
|---|---|---|
| Cache image-list index | 1948 | 2557 |
| Source version | `5100.27.0.0.0` | `6140.3.0.0.0` |
| Image Mach-O UUID | `304953E6-6B67-3CF1-B7CA-E011978210DE` | `78E1FB55-113A-3500-9D2D-1D8E282BED45` |
| Loader reference index | 1947 | 2556 |
| VM Size | `0x2e9f4000` | `0x20e0c000` |
| Loader flags | `prebuilt|in-cache-dylib|objc|never-unload` | `prebuilt|in-cache-dylib|objc|never-unload|ro-objc|pre-2022` |
| Info flags | `initializers|regions=5` | `initializers|overridable|regions=5` |
| Exports trie | off `0x025fee90`, size `0xf0d0` | off `0x0b346300`, size `0xfe18` |
| Regions | 5 | 5 |
| Reported dependencies | 13 (10 regular, 3 weak-link) | 14 (11 regular, 3 weak-link) |

The two loader reference indices are reported separately from the cache
image-list indices. In each cache the displayed loader reference index is
one less than the corresponding one-based image-list index, but this
comparison does not assign those separate fields a shared semantic meaning.

### Dependency paths

| Dependency family | Target 19H422 | Donor 20H392 |
|---|---|---|
| WirelessDiagnostics | regular — `WirelessDiagnostics.framework/WirelessDiagnostics` | regular — same path |
| CoreAccessories | regular — `CoreAccessories.framework/CoreAccessories` | regular — same path |
| CoreAnalytics | weak-link — `CoreAnalytics.framework/CoreAnalytics` | weak-link — same path |
| Foundation | regular — `Foundation.framework/Foundation` | regular — same path |
| MultitouchSupport | regular — `MultitouchSupport.framework/MultitouchSupport` | regular — same path |
| IOKit | regular — `IOKit.framework/Versions/A/IOKit` | regular — `IOKit.framework/IOKit` |
| ProtocolBuffer | weak-link — `ProtocolBuffer.framework/ProtocolBuffer` | weak-link — same path |
| SymptomDiagnosticReporter | **Not listed** | regular — `SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter` |
| libMobileGestalt | weak-link — `libMobileGestalt.dylib` | weak-link — same path |
| libIOReport | regular — `libIOReport.dylib` | regular — same path |
| libc++ | regular — `libc++.1.dylib` | regular — same path |
| libSystem | regular — `libSystem.B.dylib` | regular — same path |
| CoreFoundation | regular — `CoreFoundation.framework/CoreFoundation` | regular — same path |
| libobjc | regular — `libobjc.A.dylib` | regular — same path |

The target has 13 dependency rows versus 14 for the donor. Every target
dependency family is also represented in the donor output. The donor has
one additional printed dependency, regular
`SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter`.
The IOKit family appears on both sides with different printed path forms;
the path strings are retained exactly as supplied and are not declared
equivalent by this report.

This is a comparison of the dependency rows emitted for these two
PrebuiltLoaderSet records. It does **not** prove that the donor-only
framework is absent from the target filesystem or cache, that any image is
successfully resolved at runtime, or that the plugin is loaded. A separate
target cache inventory lookup is needed to establish whether a
`SymptomDiagnosticReporter` image record exists elsewhere in the target
cache.

### Region records

Both records report five regions and the same permission pattern
(`r-x`, three `rw-`, and `r--`). They also report `Zero Fill=false`
and `RO Data=false` for all five rows.

Target 19H422 regions:

| Region | File offset | File size | VM offset | Perms |
|---:|---:|---:|---:|---|
| 1 | `0x1bbbf000` | `0x0004e000` | `0x00000000` | `r-x` |
| 2 | `0x071f6340` | `0x00009630` | `0x17267340` | `rw-` |
| 3 | `0x0c006408` | `0x00000e20` | `0x1e077408` | `rw-` |
| 4 | `0x08162138` | `0x000000c8` | `0x1a1d3138` | `rw-` |
| 5 | `0x002ec000` | `0x0b9e0f19` | `0x23011000` | `r--` |

Donor 20H392 regions:

| Region | File offset | File size | VM offset | Perms |
|---:|---:|---:|---:|---|
| 1 | `0x024cc000` | `0x00058000` | `0x00000000` | `r-x` |
| 2 | `0x027f0138` | `0x00009f38` | `0x05664138` | `rw-` |
| 3 | `0x04ac9ab0` | `0x00000c00` | `0x0993dab0` | `rw-` |
| 4 | `0x06106638` | `0x000000c8` | `0x0af7a638` | `rw-` |
| 5 | `0x0005c000` | `0x13da4000` | `0x0d068000` | `r--` |

These offsets and sizes are cache-specific mappings and must not be
compared as though they were file offsets in standalone Mach-O files.
The same region count and permission pattern do not establish identical
memory contents or runtime behavior.

### Parser caveat

Both target and donor outputs contain a `Sections` block with extremely
large values and offset fragments that resemble ASCII text. Those decoded
section rows are excluded from interpretation pending independent parser
validation. The user supplied successful exit codes and plausible
PrebuiltLoaderSet headers/regions/dependency rows; the odd section output
is not treated as proof of cache corruption.

### Interpretation and next check

The printed dependency sets are very similar: 13 target dependency families
overlap with 13 donor dependency families, with the IOKit path-form
difference noted above. The target output does not list the donor's
`SymptomDiagnosticReporter` dependency. This is a concrete metadata
difference in the loader records, not proof of a missing OS component or
runtime failure.

Next, search the existing target JSON cache image inventory for the
reported dependency image names—especially
`SymptomDiagnosticReporter`—and capture any target cache image paths,
versions, and UUIDs. This is a bounded host-side lookup using the already
generated JSON report; no device-side action is involved.
