# iOS 16 device compatibility and 20H392 identity matrix

## Purpose

This note separates Apple's official iOS 16 compatibility list from experimental ports that reuse iOS 16 userland on non-Apple hardware. It also records why the same build number does not mean that every device-specific image or hardware configuration is interchangeable.

Reviewed: 2026-11-19.

## Apple's official compatibility boundary

Apple's iOS 16 compatibility page lists iPhone 8, iPhone 8 Plus, iPhone X, and newer supported models, plus iPhone SE (2nd and 3rd generation). It does not list iPhone 7.

Source: [Apple Support — iOS 16 and iPadOS 16 compatible devices](https://support.apple.com/en-jo/103267).

Therefore, iPhone 7 (`iPhone9,1`) is outside Apple's official iOS 16 support matrix. This is a platform-porting research target, not an officially supported iOS 16 configuration. The absence from Apple's list does not, by itself, prove that a research port is technically impossible; it means there is no official iOS 16 support claim to rely on.

## The 20H392 reference is not a single generic board image

The public reference projects report different source-device identities while using iOS 16.7.16 (20H392):

| Project | Physical test platform | Reported iOS source identity | What its result can establish |
|---|---|---|---|
| Project Sweet-10 | Intended target: iPhone 7 / `iPhone9,1` | Selected reference: iPhone X / `iPhone10,3` / D22AP | Nothing yet about actual A10 support |
| ios-alioth | POCO F3 / Qualcomm SM8250 | README describes iPhone X 20H392 userland | Upstream's reported status on its Qualcomm target only |
| ios-sailfish | Google Pixel 1 / Snapdragon 821 | README describes iPhone 8 20H392 userland | Upstream's reported status on its Pixel target only |

Sources:
- [ios-alioth README](https://github.com/furretmaster290/ios-alioth)
- [ios-sailfish README](https://github.com/SavoryBanana/ios-sailfish)

The same marketing version and build number are useful compatibility clues, but they do not identify every IPSW component, board identity, device tree, kernel build, or hardware dependency. The source device identity and the exact build manifest must be tracked alongside the build number.

## Implications for Project Sweet-10

1. Keep the selected iPhone X 20H392 userland reference explicit; do not silently substitute the iPhone 8 reference used by ios-sailfish.
2. Record source-device identity separately from the physical test board. An upstream port running an iPhone 8 or iPhone X userland on Qualcomm hardware is not evidence of an iPhone 7 port.
3. Treat Apple’s official compatibility list as the supported-device boundary, not as a substitute for XNU source analysis.
4. Keep device-specific UI, hardware services, device-tree properties, and kernel matching as separate evidence questions.
5. Do not infer an exact XNU source revision from the `xnu-8796` family label alone.

## Current project status

- iPhone 7 / `iPhone9,1` remains the intended experimental hardware target.
- iPhone X / `iPhone10,3` 20H392 remains the selected userland reference.
- Exact XNU/kernel match remains unverified.
- No A10 platform support, device-tree values, or boot compatibility is established by this matrix.

This is documentation only. No firmware, proprietary system image, device data, boot procedure, or device-writing utility is included.
