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
| Touch / HID | Donor cache includes BackBoardHIDEventFoundation and BackBoardHIDEventProcessors | `AppleSamsungSPI` matches `spi-1,samsung`; `AppleHIDTransportSPI` matches `hid-transport,k1`; `AppleMultitouchDriver` advertises `IOHIDInterface` personalities and references the `AppleMultitouchSPI` plugin | **Exact static name matches for SPI and K1 transport**; multitouch service chain and runtime touch remain unverified |
| Backlight | Donor GUI/graphics inventory does not identify a target backlight provider | `AppleLMBacklight` personality matches `backlight,lm3539` through `AppleARMIICDevice` | **Exact static name match confirmed**; runtime attachment and backlight operation unverified |
| IOKit provider matching | Donor contains the IOKit framework and framework dependencies | Target 19H422 JSON personality data has exact `IONameMatch` overlaps for display, Pinot LCD, Samsung SPI, K1 SPI HID transport, and LM3539 backlight | **Static personality/compatible overlap confirmed**; runtime service matching and attachment unverified |
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

The user inspected the target 19H422 KernelCache's JSON KEXT metadata. Five
target DeviceTree compatible strings have exact `IONameMatch` overlaps in
target-native personalities:

- `disp0,t8010` — `AppleMobileDispH9P`, provider class
  `AppleARMIODevice`.
- `lcd,pinot` — `ApplePinotLCD`, provider class
  `AppleARMMIPIDSIDevice`.
- `spi-1,samsung` — `AppleSamsungSPI`, provider class
  `AppleARMIODevice`.
- `hid-transport,k1` — `AppleHIDTransportSPI`, provider class
  `AppleARMSPIDevice`.
- `backlight,lm3539` — `AppleLMBacklight`, provider class
  `AppleARMIICDevice`.

The `AppleMultitouchDriver` personalities match `IOHIDInterface`
usage pairs and reference the `AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin`
path. The `AppleMultitouchSPI` JSON entry did not contain its own
`io_kit_personalities` field. The MIPI-DSI controller personality expects
`mipi-dsim-1,synopsys`, but the checked-in allowlist summary does not include
the parent node's compatible value. The display personality's
`BacklightMatching` dictionary requires `backlight-control = true`, a
target property not yet verified from the allowlist summary.

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
five relevant target nodes. It does not prove that any KEXT attaches to a live
IOKit provider. No display, touch, or backlight operation has been validated
on the target.

The XNU 8796 T8010 machine-profile gap, static DeviceTree runtime-value gaps,
and custom kernel handoff requirements remain separate blockers. See the
[kernel implementation readiness gate](kernel-implementation-readiness.md).

## Next host-side evidence

The next bounded task is to resolve the two metadata gaps identified in the
personality audit, then keep runtime/provider claims explicitly separate. The
remaining work is to:

1. Use the existing 19H422 IPSW on the analysis computer; do not connect,
   restore, update, or alter the phone.
2. Confirm the `/arm-io/mipi-dsim` parent compatible value and the target
   display node's `backlight-control` property using allowlist-only output.
3. Inspect the nested `MultitouchHID.plugin` metadata if the host-side parser
   exposes it as a separate object.
4. Keep any live provider attachment, working display/touch/backlight, and
   20H392 userland compatibility claims **unverified**.
5. Commit only sanitized names, bundle identifiers, hashes, and conclusions;
   do not add firmware binaries, device-specific identifiers, or raw DeviceTree
   data to the repository.

The `ipsw` CLI documents JSON KEXT output with each bundle's IOKit personality
metadata. This is offline file analysis; it is not a device operation.

## Status

M6 remains in progress. The donor framework inventory is substantially
expanded and the target static DeviceTree, target-native 19H422 KEXT inventory, and static
IOKit personality crosswalk are recorded. Runtime provider attachment and
20H392 userland service compatibility are not established. M7 (SpringBoard on
iPhone9,1) has **not started**.
