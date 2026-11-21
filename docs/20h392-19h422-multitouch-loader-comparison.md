# 20H392 donor / 19H422 target MultitouchHID loader comparison

## Scope and source records

This report compares the user-supplied output of
`ipsw dyld image <cache> <image>` for the same full cached image path in
two read-only mounted IPSW caches:

```text
/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID
```

- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8 build
  19H422.
- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16 build
  20H392.

The physical iPhone 7 remains on iOS 12.1.4. This is a static cache
metadata comparison only; it does not establish runtime loading, IOKit
attachment, HID event delivery, or cross-board compatibility.

## Cache identity and loader fields

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| Cache image-list index (from JSON inventory) | 1948 | 2557 |
| Source version (from JSON inventory) | `5100.27.0.0.0` | `6140.3.0.0.0` |
| Mach-O UUID (from JSON inventory) | `304953E6-6B67-3CF1-B7CA-E011978210DE` | `78E1FB55-113A-3500-9D2D-1D8E282BED45` |
| Cache load address (from JSON inventory) | `7982772224` | `8757542912` |
| `dyld image` command exit status | 0 | 0 |
| VM Size | `0x2e9f4000` | `0x20e0c000` |
| Loader reference shown by `dyld image` | `index: 1947` | `index: 2556` |
| Loader flags | `prebuilt|in-cache-dylib|objc|never-unload` | `prebuilt|in-cache-dylib|objc|never-unload|ro-objc|pre-2022` |
| Info flags | `initializers|regions=5` | `initializers|overridable|regions=5` |
| Exports trie | offset `0x025fee90`, size `0xf0d0` | offset `0x0b346300`, size `0xfe18` |
| Region count | 5 | 5 |

The image-list indices above come from the JSON image inventory. The loader
reference indices come from the separate PrebuiltLoaderSet output. The
numbers are recorded under their own labels and are not interchangeable.

The target loader output does not itself print the image source version or
Mach-O UUID; those values are taken from the separate target JSON cache
image inventory. The same distinction applies to the donor.

## Dependency comparison

The target record reports 13 dependency rows (10 regular and 3 weak-link).
The donor record reports 14 (11 regular and 3 weak-link).

| Dependency | Target 19H422 | Donor 20H392 |
|---|---|---|
| `WirelessDiagnostics.framework/WirelessDiagnostics` | regular | regular |
| `CoreAccessories.framework/CoreAccessories` | regular | regular |
| `CoreAnalytics.framework/CoreAnalytics` | weak-link | weak-link |
| `Foundation.framework/Foundation` | regular | regular |
| `MultitouchSupport.framework/MultitouchSupport` | regular | regular |
| IOKit framework | regular — `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit` | regular — `/System/Library/Frameworks/IOKit.framework/IOKit` |
| `ProtocolBuffer.framework/ProtocolBuffer` | weak-link | weak-link |
| `SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter` | Not listed as a direct edge; target cache image exists at index `1455` | regular |
| `libMobileGestalt.dylib` | weak-link | weak-link |
| `libIOReport.dylib` | regular | regular |
| `libc++.1.dylib` | regular | regular |
| `libSystem.B.dylib` | regular | regular |
| `CoreFoundation.framework/CoreFoundation` | regular | regular |
| `libobjc.A.dylib` | regular | regular |

The target output lists all 13 dependency families also shown by the donor,
except that the donor has one additional printed row:
`SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter`.
The IOKit paths differ in their printed form. No symlink resolution or
path normalization is claimed here.

The target PrebuiltLoaderSet output does not list
`SymptomDiagnosticReporter` as a direct dependency, but the separate target
JSON image inventory does contain it at index `1455`, version
`174.140.2.0.0`, UUID
`ED77A600-C0BE-3240-9693-BF5238095816`. This is a donor-only direct
dependency edge in the two compared loader records, not a framework-absence
finding. The image-list entry does not prove runtime dependency resolution
or a standalone file in the mounted root filesystem. See the [target
dependency image inventory](iphone91-19h422-multitouch-dependency-image-inventory.md)
for the seven queried target image records.

## Region metadata

Both records report five regions, with the same permission sequence:
`r-x`, `rw-`, `rw-`, `rw-`, `r--`. All five rows on each side
report `Zero Fill=false` and `RO Data=false`.

Target 19H422:

| Region | File offset | File size | VM offset | Permissions |
|---:|---:|---:|---:|---|
| 1 | `0x1bbbf000` | `0x0004e000` | `0x00000000` | `r-x` |
| 2 | `0x071f6340` | `0x00009630` | `0x17267340` | `rw-` |
| 3 | `0x0c006408` | `0x00000e20` | `0x1e077408` | `rw-` |
| 4 | `0x08162138` | `0x000000c8` | `0x1a1d3138` | `rw-` |
| 5 | `0x002ec000` | `0x0b9e0f19` | `0x23011000` | `r--` |

Donor 20H392:

| Region | File offset | File size | VM offset | Permissions |
|---:|---:|---:|---:|---|
| 1 | `0x024cc000` | `0x00058000` | `0x00000000` | `r-x` |
| 2 | `0x027f0138` | `0x00009f38` | `0x05664138` | `rw-` |
| 3 | `0x04ac9ab0` | `0x00000c00` | `0x0993dab0` | `rw-` |
| 4 | `0x06106638` | `0x000000c8` | `0x0af7a638` | `rw-` |
| 5 | `0x0005c000` | `0x13da4000` | `0x0d068000` | `r--` |

The region offsets belong to two different shared-cache layouts. They
must not be treated as offsets into two standalone Mach-O files or used
for direct byte-offset comparison.

## Parser-output caveat

Both user-supplied records contain a `Sections` block whose decoded
offsets/sizes are implausibly large and include values resembling ASCII
fragments. Those section rows are deliberately excluded from interpretation
pending independent parser validation. Their presence is not evidence
that either cache image is corrupt.

The other fields in this report are limited to those printed by the
successful commands and the separate JSON image inventories. No
code-signature validation is claimed from loader metadata.

## Interpretation

The target and donor loader records have many similarities: the same full
image path, five regions, the same broad permission sequence, and a largely
matching set of 13 dependency families. They also have concrete record
differences:

- The target record lists 13 dependencies; the donor lists 14.
- The donor additionally lists a regular direct dependency edge to
  `SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter`; the
  target cache image list nevertheless contains that framework (index 1455).
- The IOKit framework path is printed differently.
- The loader and info flags differ.
- VM size and cache-region offsets/sizes differ.

These differences are static metadata only. They do not identify the
cause of the version or UUID difference, prove a missing target framework,
or demonstrate compatibility or incompatibility on T8010.

## Next bounded check

The selected target dependency-name lookup is complete. Its seven
relevant cache image records, including target
`SymptomDiagnosticReporter`, are recorded in the [target dependency image
inventory](iphone91-19h422-multitouch-dependency-image-inventory.md).
The next bounded check is the equivalent read-only lookup against the
already-generated donor JSON inventory `$HOME/20H392-dyld-images.json`, so
the target and donor framework versions/UUIDs can be compared. Cache image
presence does not establish runtime dependency resolution.

No binary, cache, filesystem image, or firmware file is added to the
repository. No device, partition, activation, security, boot, or restore
state was accessed or changed.
