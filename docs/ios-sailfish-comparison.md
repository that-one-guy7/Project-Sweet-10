# ios-sailfish: cross-port research review

## Scope

This note summarizes the public README of [SavoryBanana/ios-sailfish](https://github.com/SavoryBanana/ios-sailfish). It records upstream-reported status and architecture boundaries; it does not copy code, boot instructions, firmware, or hardware constants.

## What the upstream README reports

The README describes an experimental iOS 16.7.16 (20H392) userland running on a Google Pixel 1 (codename `sailfish`, Snapdragon 821). It identifies the kernel as the XNU 8796 generation and says the project descends from dipa-studio/ios-sweet.

The README's dated status section reports a lock screen, SpringBoard-era UI components, touch, physical buttons, battery reporting, brightness/sleep behavior, Wi-Fi, and Adreno 530 acceleration through Mesa/freedreno. It describes a custom shim, generated Apple Device Tree, kernel payload, UFS-backed HFS+ root, and persistent diagnostics.

These are statements from the upstream project's own README, not independently reproduced results by Project Sweet-10.

## Important differences from Project Sweet-10

| Dimension | ios-sailfish reference | Project Sweet-10 |
|---|---|---|
| Physical target | Google Pixel 1 / Snapdragon 821 | iPhone 7 / A10 / T8010 |
| Userland source | iPhone 8, 20H392 | iPhone X, 20H392 |
| Kernel family | XNU 8796 | Candidate XNU 8796.141.3 |
| Device identity | iPhone 8 / Home-button UI | Must be researched for iPhone 7 |
| Platform drivers | Pixel/Qualcomm-specific | Not implemented |
| Reported UI milestone | Lock screen and stock apps | Not started |

The common build number does not make the iPhone 8 and iPhone X userland images interchangeable, and neither image establishes iPhone9,1 support.

## Reusable engineering lessons

1. Keep the boot shim, kernel, Apple Device Tree, payload format, root filesystem, and userland changes as separate, reviewable components.
2. Maintain persistent diagnostics because early boot failures may occur before ordinary logging is available.
3. Treat CPU, interrupt/timer, memory, storage, display, touch, networking, and power as separate bring-up areas.
4. Record which results are measured on hardware and which are only build-time or source-level claims.
5. Track security limitations explicitly. The upstream README describes permissive code-signing/sandbox behavior and missing security hardware; this is not a suitable production configuration.

## Non-portable implementation

The Pixel 1's Snapdragon 821, Adreno 530, display pipeline, touch controller, PMIC, storage topology, interrupt configuration, and board memory map are not iPhone 7 hardware. No Pixel-specific addresses, register values, drivers, or device-tree entries should be copied into the A10 project.

## Project decision

Use ios-sailfish as a later-stage process and subsystem reference, not as an A10 implementation source. Its iPhone 8 20H392 userland is an additional comparison point; Project Sweet-10 retains iPhone X 20H392 as its selected userland reference.

## Evidence still needed

- Exact XNU revision matching the selected iPhone X 20H392 image.
- Authoritative iPhone9,1 device-tree and platform metadata.
- A reproducible unmodified XNU build for the selected toolchain.
- A separate evidence-backed A10 analysis for CPU startup, interrupts/timers, memory map, storage, display, HID, and power.

No device interaction, firmware modification, boot attempt, or partition write was performed for this review.
