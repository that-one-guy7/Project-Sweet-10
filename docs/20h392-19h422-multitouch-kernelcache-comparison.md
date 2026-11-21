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

Consequently, the target's compiled plugin image is now confirmed as an
entry in the 19H422 dyld shared-cache inventory (index 1948, version
`5100.27.0.0.0`, UUID
`304953E6-6B67-3CF1-B7CA-E011978210DE`), despite no standalone
`MultitouchHID*` file being returned by the complete filesystem search.
The donor standalone executable remains unlocated in the two searched donor
filesystem roots. The actual Mach-O bytes have not been separately extracted
or compared. The dyld image entry is stronger than plist-only metadata but
is not signature validation or runtime proof. The mere presence of
`CodeResources` does not verify a code signature.

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

## Next bounded host-side comparison

The target and donor plugin Info.plists have now been compared. The donor
plist declares `CFBundleExecutable=MultitouchHID`; its
`CodeResources` plist reports top-level keys `files`, `files2`,
`rules`, and `rules2`, with empty printed `files` and `files2`
entries. No matching donor executable was found in either searched mounted
donor root. The 19H422 dyld image inventory now contains
`/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID`
at index 1948, version `5100.27.0.0.0`, UUID
`304953E6-6B67-3CF1-B7CA-E011978210DE`. The next bounded static task is
to query the separate 20H392 donor SystemOS dyld cache for the corresponding
image path, version, and UUID. A binary comparison remains deferred until
actual cache image bytes are separately obtained and statically inspected.
The `CodeResources` output is not signature verification. Keep donor and
target artifacts separate; metadata does not prove runtime compatibility.

The exact XNU source revision corresponding to the donor KernelCache remains
a separate source-provenance question. No device, firmware, partition,
activation, security, or boot state was accessed or changed. No KernelCache,
filesystem image, KEXT executable, plugin executable, or raw DeviceTree is
committed to the repository.
