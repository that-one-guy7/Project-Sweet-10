# 20H392 donor dyld shared-cache multitouch image audit

## Purpose and evidence boundary

This report records the user's read-only inspection of the iPhone X
`iPhone10,3` / D22AP / A11-T8015 iOS 16.7.16 (20H392) SystemOS
dyld shared cache and compares the image-path/version records with the
iPhone 7 `iPhone9,1` / D10AP / A10-T8010 iOS 15.8.8 (19H422) target
reference.

The physical iPhone 7 remains on iOS 12.1.4. Both caches were inspected
from host-side mounted firmware filesystems. This report records dyld
image-list metadata only. It does not establish runtime image loading,
plugin factory execution, IOKit attachment, HID event delivery, or
cross-board compatibility.

## Donor cache and command

The donor cache path used by the user was:

```text
/home/hey/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

The user ran `ipsw dyld info --dylibs` against that cache and saved the
text output as:

```text
/home/hey/20H392-multitouch-cache-list.txt
```

The saved report size was 293,678 bytes. The user supplied the grep output
for the four multitouch/HID image names. The result contained the
`MultitouchHID` image at the exact install path previously found in the
19H422 target cache.

## Direct image-list comparison

The following rows compare the user-supplied donor output with the
previously recorded 19H422 target image inventory.

| Image | 20H392 donor entry | Donor version | 19H422 target entry | Target version |
|---|---:|---|---:|---|
| `MultitouchHID` | 2557 | `6140.3.0.0.0` | 1948 | `5100.27.0.0.0` |
| `AppleHIDTransportSupport` | 1499 | `6140.1.0.0.0` | 2067 | `5100.32.0.0.0` |
| `MultitouchSupport` | 1648 | `6140.3.0.0.0` | 1249 | `5100.27.0.0.0` |
| `MultitouchSessionFilterSupport` | 2140 | `6140.3.0.0.0` | 2221 | `5100.27.0.0.0` |

The full `MultitouchHID` install path reported in the donor cache is:

```text
/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID
```

The target cache inventory reports the same full path. The donor image
indices and target image indices belong to separate cache inventories;
their numerical difference does not imply load order, priority, or
compatibility.

## PrebuiltLoaderSet record and dependency inventory

The user queried the exact image path with:

```text
ipsw dyld image "$DONOR_CACHE" "$IMAGE" -V
```

The supplied output resolved the same `MultitouchHID` path and returned
this PrebuiltLoaderSet record:

| Field | Donor output |
|---|---|
| Path | `/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID` |
| VM Size | `0x20e0c000` |
| Loader flags | `prebuilt|in-cache-dylib|objc|never-unload|ro-objc|pre-2022` |
| Loader reference | `index: 2556` |
| Info flags | `initializers|overridable|regions=5` |
| Exports trie | Offset `0x0b346300`, size `0xfe18` |
| Regions | Five regions reported, with `r-x`, `rw-`, and `r--` permissions |

The command also reported 14 dependencies:

| Kind | Dependency |
|---|---|
| regular | `WirelessDiagnostics.framework/WirelessDiagnostics` |
| regular | `CoreAccessories.framework/CoreAccessories` |
| weak-link | `CoreAnalytics.framework/CoreAnalytics` |
| regular | `Foundation.framework/Foundation` |
| regular | `MultitouchSupport.framework/MultitouchSupport` |
| regular | `IOKit.framework/IOKit` |
| weak-link | `ProtocolBuffer.framework/ProtocolBuffer` |
| regular | `SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter` |
| weak-link | `libMobileGestalt.dylib` |
| regular | `libIOReport.dylib` |
| regular | `libc++.1.dylib` |
| regular | `libSystem.B.dylib` |
| regular | `CoreFoundation.framework/CoreFoundation` |
| regular | `libobjc.A.dylib` |

This records the donor image's static loader/dependency metadata. It does
not prove that these dependencies are installed or usable on iPhone9,1,
that the plugin loads at runtime, or that a HID provider attaches.

The output's `Sections` block contains implausibly large decoded offsets
and sizes, including values that resemble ASCII fragments. Those section
rows are excluded from interpretation pending independent parser
validation. This is not evidence that the cache image itself is corrupt.

The loader reference index `2556` is recorded separately from the
one-based donor `dyld info --dylibs` image-list entry `2557`. Their
relationship has not been established, so they are not treated as
interchangeable identifiers.

## UUID status and corrected lookup method

The supplied `ipsw dyld image ... -V` output does **not** contain a
Mach-O UUID. The earlier generic expectation that this command would
print an image UUID does not apply to the path taken for this iOS 16
cache. Source review of the pinned ipsw 3.1.749 implementation explains
the difference: `dyld image` first tries to resolve a PrebuiltLoaderSet
entry and prints the loader record when that succeeds. Its older
image-array fallback prints a cache-image record instead.

For this donor cache, the source-backed UUID method was
`ipsw dyld info --dylibs --json`. The user successfully ran that
inventory query and supplied one exact matching record:

| Field | 20H392 donor |
|---|---|
| Image-list index | `2557` |
| Full install path | `/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID` |
| Source version | `6140.3.0.0.0` |
| Mach-O UUID | `78E1FB55-113A-3500-9D2D-1D8E282BED45` |
| Load address | `8757542912` (`0x20a000000`) |

The corresponding 19H422 target record is index `1948`, version
`5100.27.0.0.0`, UUID
`304953E6-6B67-3CF1-B7CA-E011978210DE`, and load address
`7982772224`. The different UUIDs show that the donor and target cache
images do not share the same Mach-O build identifier. They do not by
themselves establish source-level differences, semantic differences,
byte-for-byte inequality, or incompatibility. No raw Mach-O extraction
or byte comparison has been performed.

The pinned ipsw 3.1.749 source documents why the earlier
`ipsw dyld image ... -V` query returned a PrebuiltLoaderSet record
instead: that command prefers the loader-set path when it is available.
The JSON inventory emits the per-image `index`, `name`, `version`,
`uuid`, and `load_address` fields from the cached image's partial
Mach-O.


Pinned source references:
- [ipsw 3.1.749 dyld image command](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/dyld/dyld_image.go)
- [ipsw 3.1.749 DSC JSON inventory](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/internal/commands/dsc/dsc.go)

## Interpretation

The supplied cache inventories establish that:

1. Both the 20H392 donor and 19H422 target cache image lists contain the
   `MultitouchHID` image at the same full install path.
2. The donor image-list version is `6140.3.0.0.0`, while the target
   image-list version is `5100.27.0.0.0`.
3. The three related donor multitouch/HID userland images listed above
   also have later version strings than their corresponding target
   records.
4. The donor and target are different hardware generations:
   A11/T8015 on iPhone10,3 versus A10/T8010 on iPhone9,1.

This is stronger than plist-only evidence because both cache inventories
list compiled image records for the plugin path. It remains metadata-level
evidence: no raw Mach-O bytes have been separately extracted or compared, and no
signature verification or runtime test is claimed. The donor PrebuiltLoaderSet dependency list is static closure
metadata only and does not establish target-side dependency resolution. The shared install path and previously observed matching plugin
type/factory UUID declarations do not establish binary compatibility,
provider attachment, or cross-board support.

The donor's later image-list versions must not be treated as a reason to
substitute donor files into the target filesystem. The target-native
19H422 image records remain the appropriate static reference for the
iPhone9,1 hardware identity.

## Evidence status

| Claim | Status |
|---|---|
| Donor 20H392 cache path | Supplied by user |
| Donor `MultitouchHID` path and image-list version | Confirmed in supplied grep output |
| Donor related multitouch/HID image paths and versions | Confirmed in supplied grep output |
| Target 19H422 corresponding paths and versions | Confirmed in the previously recorded target cache inventory |
| Donor `MultitouchHID` Mach-O UUID | Confirmed: `78E1FB55-113A-3500-9D2D-1D8E282BED45` (image-list index 2557) |
| Raw donor/target Mach-O byte comparison | Not performed; UUIDs differ, but raw bytes have not been extracted |
| Signature validation | Not performed |
| Runtime plugin loading or IOKit attachment | Not tested |
| Touch-event delivery on iPhone9,1 | Not tested |
| A11/T8015 donor binary compatibility with A10/T8010 target | Not established |

No proprietary binary, shared-cache file, filesystem image, KernelCache,
or raw DeviceTree is committed to this repository. No device, firmware,
partition, activation, security, or boot state was accessed or changed.


## Selected dependency image records from donor inventory

The user supplied a read-only lookup from
`$HOME/20H392-dyld-images.json` for the seven selected dependency image
names used in the MultitouchHID loader comparison:

| Image | Donor image-list index | Version | UUID |
|---|---:|---|---|
| SymptomDiagnosticReporter | 928 | `229.120.4.0.0` | `AD5E6BA8-ED20-3AF7-BD79-274FEBAC7ABD` |
| WirelessDiagnostics | 600 | `980.0.0.0.0` | `B6D6A466-6317-3243-A8E7-D0C25575F981` |
| CoreAccessories | 312 | `793.140.4.0.0` | `82233556-8941-3465-A570-F8529F3BCD1E` |
| CoreAnalytics | 226 | `264.140.2.0.0` | `A973AEA3-3A5D-3AAF-985D-29E7B13AE91C` |
| MultitouchSupport | 1648 | `6140.3.0.0.0` | `1B6ABB86-B8A9-3941-A66A-EC9715F6B034` |
| IOKit | 30 | `2022.140.2.701.1` | `BCAE5DD8-45F9-3877-92CB-44190C3BAD70` |
| ProtocolBuffer | 239 | `294.30.6.7.2` | `54255241-0540-398C-BD54-B2F185C6D23C` |

The full donor/target side-by-side table is in
[the dependency image comparison](20h392-19h422-multitouch-dependency-image-comparison.md).
All seven selected image families also appear in the target 19H422 cache
inventory, but every corresponding version string and UUID differs.

These records identify different cache image builds; they do not show
whether the differences cause runtime behavior, nor do they justify copying
donor binaries into the target. The image-list indexes are cache-local and
are not comparable as stable IDs.
