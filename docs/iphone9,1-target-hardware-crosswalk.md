# iPhone9,1 target-native hardware and service crosswalk

## Purpose and scope

This document compares the iPhone X iOS 16.7.16 (20H392) donor's GUI-related
framework requirements with hardware evidence from the iPhone 7
`iPhone9,1` / D10AP / A10-T8010 target.

The phone itself remains on its existing iOS 12.1.4 installation. The
target-side hardware reference used here is a separately inspected iPhone 7
iOS 15.8.8 (19H422) IPSW. That static IPSW is useful evidence about the target
board; it is not installed on the phone, is not the donor userland, and does
not prove that 20H392 can run on iPhone9,1.

This is a host-side static evidence crosswalk. It does not include device
operations, kernel implementation, firmware modification, or a boot claim.

## Evidence sources

### Donor: iPhone X 20H392

The separate OS root filesystem and SystemOS Cryptex were mounted and inspected.
The selected SystemOS cache reports:

- Magic: `dyld_v1   arm64`
- Platform: iOS
- OS version: 16.7
- Images: 2,710
- Subcaches: 42
- Cache UUID: `8F970452-C9E3-3E88-B114-FEB1864BC9E0`

The donor cache and PrebuiltLoaderSet records include the framework families
used by the donor GUI chain: IOMobileFramebuffer, BackBoard HID event
frameworks, BackBoardServices, IOKit, CoreGraphics, Metal, IOSurface,
RunningBoard, and SpringBoard. These are donor-side image and loader records,
not evidence of target provider matches.

See [the 20H392 cache inventory](20h392-dyld-cache-inventory.md) and the
[BackBoard framework dependency results](20h392-backboard-framework-dependency-results.md).

### Target: iPhone 7 19H422 static DeviceTree

The target reference is the verified iPhone9,1 / D10AP iOS 15.8.8 (19H422)
DeviceTree component. The component was independently decompressed and parsed
as 227 nodes including root, with all 160,572 input bytes consumed and no
trailing bytes. The raw tree is intentionally not committed because it contains
device-specific information.

The root identifies `D10AP` and `iPhone9,1`; `/arm-io` identifies
`arm-io,t8010` and `t8010-io`. The tree is a static IPSW component, not
the final runtime DeviceTree that a boot environment might provide.

See the [parsed 19H422 DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md)
and [property inventory](../device-tree/PROPERTY_INVENTORY.md).

## Crosswalk

| Requirement area | 20H392 donor evidence | iPhone9,1 target evidence from 19H422 | Assessment |
|---|---|---|---|
| Board / SoC identity | Donor is iPhone X, D22AP, A11/T8015 | Root identifies iPhone9,1 / D10AP; `/arm-io` identifies T8010 | **Target-confirmed identity**; donor is a different board and SoC |
| Display subsystem | Donor cache/loader records include IOMobileFramebuffer, CoreGraphics, Metal, and IOSurface | `/arm-io/disp0` is `disp0,t8010`; `AppleMobileDispH9P` personality matches `disp0,t8010` through `AppleARMIODevice` | **Exact static name match confirmed**; runtime attachment and display operation unverified |
| Touch / HID | Donor cache includes BackBoardHIDEventFoundation and BackBoardHIDEventProcessors | `AppleSamsungSPI` matches `spi-1,samsung`; `AppleHIDTransportSPI` matches `hid-transport,k1`; `AppleMultitouchDriver` has `IOHIDInterface` personalities whose plugin-type UUID matches the extracted `MultitouchHID.plugin` `CFPlugInTypes` UUID | **Exact static SPI/K1 name match and plugin type-UUID linkage**; runtime provider attachment, plugin loading, and touch delivery remain unverified |
| Backlight | Donor GUI/graphics inventory does not identify a target backlight provider | `AppleLMBacklight` personality matches `backlight,lm3539` through `AppleARMIICDevice` | **Exact static name match confirmed**; runtime attachment and backlight operation unverified |
| IOKit provider matching | Donor contains the IOKit framework and framework dependencies | Target 19H422 JSON personality data has exact `IONameMatch` overlaps for display, Synopsys MIPI-DSI, Pinot LCD, Samsung SPI, K1 SPI HID transport, and LM3539 backlight | **Six static personality/compatible overlaps confirmed**; runtime service matching and attachment unverified |
| BackBoard / RunningBoard services | Donor contains BackBoardServices, RunningBoardServices, RunningBoard, and SpringBoard images | No target-native provider or service equivalence follows from the DeviceTree node names | **Donor-only service evidence**; target service compatibility is unverified |
| CPU / memory / early platform | Donor is A11/T8015; its cache does not supply D10AP platform values | 19H422 static tree identifies two CPU nodes and T8010; static CPU clock values are zero, memory/PRAM/VRAM ranges are zero, and panic-log size is absent | **Target-confirmed static identity/structure**; runtime clock, memory, and panic handoff values remain unknown |
| XNU machine configuration | Candidate XNU 8796 is relevant to the iOS 16 generation | Reviewed XNU 8796 ARM64 machine allowlist and board header omit T8010; historical T8010/H9 source exists in older XNU 7195, not as a ready 8796 profile | **Known source/build blocker**; historical profile presence does not prove a compatible backport |

### Important DeviceTree parsing limit

The target `/arm-io/spi2/multi-touch` node has a 32-byte `reg`
property. Its parent advertises `#address-cells = 1` and
`#size-cells = 7`. Do not reinterpret this field as a conventional 16-byte
64-bit address/size pair or use a fixed-width register-summary heuristic.
The parsed audit records this as a format caveat, not as a decoded hardware
resource.

## Target IOKit personality crosswalk

The user inspected the target 19H422 KernelCache's JSON KEXT metadata. Six
target DeviceTree compatible strings have exact `IONameMatch` overlaps in
target-native personalities:

- `disp0,t8010` — `AppleMobileDispH9P`, provider class
  `AppleARMIODevice`.
- `mipi-dsim-1,synopsys` — `AppleSynopsysMIPIDSI`, provider class
  `AppleARMIODevice`.
- `lcd,pinot` — `ApplePinotLCD`, provider class
  `AppleARMMIPIDSIDevice`.
- `spi-1,samsung` — `AppleSamsungSPI`, provider class
  `AppleARMIODevice`.
- `hid-transport,k1` — `AppleHIDTransportSPI`, provider class
  `AppleARMSPIDevice`.
- `backlight,lm3539` — `AppleLMBacklight`, provider class
  `AppleARMIICDevice`.

The `AppleMultitouchDriver` personalities match `IOHIDInterface` usage pairs
and reference the `AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin` path.
The extracted target plugin `Info.plist` declares type UUID
`0516B563-B15B-11DA-96EB-0014519758EF`, exactly matching the key in the
parent personality's `IOCFPlugInTypes` map; the plugin maps that type to its
`IOHIDPlugInFactory` factory UUID. The `AppleMultitouchSPI` JSON entry still
does not contain its own `io_kit_personalities` field, which must not be read
as proof that the plugin is absent. The updated target DeviceTree inspection
also confirmed `/arm-io/mipi-dsim` compatible `mipi-dsim-1,synopsys`, matching
`AppleSynopsysMIPIDSI`. The display personality's separate
`BacklightMatching` dictionary requires `backlight-control = true`, which was
not reported for `/arm-io/disp0` in the allowlist-only output.

See the [full target IOKit personality crosswalk](iphone91-19h422-iokit-personality-crosswalk.md).
These are static metadata matches, not proof of runtime IOKit attachment or
working hardware.

## Target 19H422 KernelCache evidence

The extracted iPhone9,1 KernelCache is reported as Darwin 21.6.0,
`xnu-8020.241.44~1/RELEASE_ARM64_T8010`, with 230 KEXT entries. Its SHA-256 is
`7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`.
The inventory includes target-side candidates for the display, LCD, MIPI-DSI,
Samsung SPI, HID transport, SPI multitouch, and backlight subsystems. Exact
bundle IDs, versions, and evidence limits are recorded in the
[19H422 KernelCache KEXT inventory](iphone91-19h422-kernelcache-kext-inventory.md).

This target kernel evidence is from iOS 15.8.8, not the iPhone X 20H392 donor.
Its `RELEASE_ARM64_T8010` build string does not establish that the separate
XNU 8796.141.3 donor kernel has a compatible T8010 machine profile.

The crosswalk now has exact static personality/compatible-string overlap for
six relevant target nodes. It also records the separate plugin type-UUID link
between the target `AppleMultitouchDriver` personality and extracted plugin
metadata. None of this proves that a KEXT attaches to a live IOKit provider or
that the plugin loads. No display, touch, or backlight operation has been
validated on the target.

The XNU 8796 T8010 machine-profile gap, static DeviceTree runtime-value gaps,
and custom kernel handoff requirements remain separate blockers. See the
[kernel implementation readiness gate](kernel-implementation-readiness.md).

## Next host-side evidence

The next bounded M6 task is to compare the target-native 19H422 multitouch
metadata with the actual iOS 16.7.16 (20H392) donor KernelCache, while keeping
the two hardware identities separate.

1. The uploaded 20H392 BuildManifest audit records the donor KernelCache
   component name as `kernelcache.release.iphone10b` and its manifest digest.
   The supplied standalone BuildManifest does not include the KernelCache
   bytes, so the actual donor component's version string and KEXT records are
   not yet verified in this repository.
2. If the matching 20H392 IPSW is already available on the analysis computer,
   inspect that component as a host-side file and compare the donor versions
   and personality metadata for `AppleHIDTransport`,
   `AppleHIDTransportSPI`, `AppleMultitouchSPI`, and
   `AppleMultitouchDriver` against the 19H422 target report.
3. Record differences as donor/target metadata only. The 20H392 donor is
   iPhone X / D22AP / A11-T8015; the 19H422 target reference is
   iPhone 7 / D10AP / A10-T8010. Similar bundle names or matching UUIDs do not
   establish cross-board compatibility or justify copying drivers.
4. Keep all device, firmware, and boot state unchanged. Do not install the
   donor IPSW on the iPhone 7; this step requires only local file inspection.

The next comparison is blocked only on access to the actual 20H392
KernelCache artifact or its verified extracted path. The uploaded manifest
alone is not enough to validate its contents.

## Status

M6 remains in progress. The donor framework inventory is substantially
expanded and the target static DeviceTree, target-native 19H422 KEXT inventory, and static
IOKit personality crosswalk are recorded. Runtime provider attachment and
20H392 userland service compatibility are not established. M7 (SpringBoard on
iPhone9,1) has **not started**.
