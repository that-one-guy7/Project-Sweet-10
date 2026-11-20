# iOS 16 device compatibility and 20H392 identity matrix

## Purpose

This note separates Apple's official iOS 16 compatibility boundary from experimental ports that reuse an iOS 16 userland on non-Apple hardware. It also records why a shared build number does not make device-specific restore images, kernel caches, or board data interchangeable.

Reviewed: 2026-11-19.

## Apple's official compatibility boundary

Apple's iOS 16 compatibility page lists iPhone 8, iPhone 8 Plus, iPhone X, and newer supported models, plus iPhone SE (2nd and 3rd generation). It does not list iPhone 7.

Source: [Apple Support — iOS 16 and iPadOS 16 compatible devices](https://support.apple.com/en-jo/103267).

Therefore, iPhone 7 (`iPhone9,1`) is outside Apple's official iOS 16 support matrix. This is an experimental platform-porting target, not an officially supported iOS 16 configuration. Its absence from Apple's list does not by itself prove that a research port is impossible.

## 20H392 is shared by multiple device families

The iOS 16.7.16 build number `20H392` is listed for more than one supported iPhone family:

| Device family | Example product identity | Relevance |
|---|---|---|
| iPhone X | `iPhone10,3` / D22AP (GSM model family) | Project Sweet-10's selected userland reference |
| iPhone 8 | iPhone 8 restore-image family | Separate source-device image; also referenced by ios-sailfish |
| iPhone 8 Plus | iPhone 8 Plus restore-image family | Separate source-device image |

Sources:
- [IPSW Downloads — iOS 16.7.16 device list](https://ipsw.me/16.7.16/)
- [The Apple Wiki — iOS 16.7.16 OTA device records](https://theapplewiki.com/wiki/OTA_Updates/iPhone/16.7.16)
- [Apple Developer — iOS 16.7.16 (20H392)](https://developer.apple.com/news/releases/?id=05112026j)

The build number identifies a software release, not one universal device image. Product identifier, board/device class, BuildManifest, DeviceTree, kernelcache and other restore-image members remain device-specific inputs.

## Public port references

| Project | Physical test platform | Reported iOS source identity | What its result can establish |
|---|---|---|---|
| Project Sweet-10 | Intended target: iPhone 7 / `iPhone9,1` | Selected reference: iPhone X / `iPhone10,3` / D22AP | Nothing yet about actual A10 support |
| ios-alioth | POCO F3 / Qualcomm SM8250 | README describes iPhone X 20H392 userland | Upstream-reported status on its Qualcomm target only |
| ios-sailfish | Google Pixel 1 / Snapdragon 821 | README describes iPhone 8 20H392 userland | Upstream-reported status on its Pixel target only |

Sources:
- [ios-alioth README](https://github.com/furretmaster290/ios-alioth)
- [ios-sailfish README](https://github.com/SavoryBanana/ios-sailfish)

The same version/build label does not identify every IPSW component, board identity, device tree, kernel build, or hardware dependency. Always record source-device identity and image metadata alongside the build number.

## Implications for Project Sweet-10

1. Keep the selected iPhone X 20H392 reference explicit; do not silently substitute the iPhone 8 image used by ios-sailfish.
2. Record source-device identity separately from the physical test board.
3. Treat Apple's official compatibility list as the supported-device boundary, not as a substitute for XNU source analysis.
4. Keep device-specific UI, hardware services, device-tree properties, and kernel matching as separate evidence questions.
5. Do not infer an exact XNU source revision from the `xnu-8796` family label alone.

## Current project status

- iPhone 7 / `iPhone9,1` remains the intended experimental hardware target.
- iPhone X / `iPhone10,3` D22AP 20H392 remains the selected userland reference.
- XNU `xnu-8796.141.3` is now corroborated by a downstream 20H392 profile report, but an Apple-published build-to-source mapping has not been independently established.
- No A10 platform support, device-tree values, or boot compatibility is established by this matrix.

This is documentation only. No firmware, proprietary system image, device data, boot procedure, or device-writing utility is included.
