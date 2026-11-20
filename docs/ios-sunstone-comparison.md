# Cross-project comparison: ios-sunstone

## Why this reference matters

The public `14sea/ios-sunstone` project is a later-stage reference built on the same
XNU generation and selected iOS userland as Project Sweet-10:

- XNU family: `xnu-8796`.
- Userland: iPhone X iOS 16.7.16, build `20H392`.
- Reported GUI milestone: launchd, backboardd, and SpringBoard.
- Reference hardware: Redmi Note 12 5G (`sunstone`), Qualcomm SM4375 / Snapdragon 4 Gen 1.

The repository README and engineering handoff report that this device reaches SpringBoard
with touch, keys, battery reporting, display support, and eight CPU cores. The project
also reports that several subsystems remain unavailable or kernel-only. These are
upstream project claims, not tests performed by Project Sweet-10.

## What it demonstrates

1. The iPhone X 20H392 userland can be made to run on hardware other than the original
   iPhone X when a substantial platform layer is supplied.
2. Reaching SpringBoard requires far more than compiling XNU: boot handoff, CPU startup,
   memory management, storage/root, display, HID, and userland-facing services all matter.
3. The upstream project evolved through a long, ordered patch series and separate
   boot-shim, tooling, and diagnostic components.
4. Its build workflow pins a specific helper-builder revision and selects a macOS/Xcode
   environment; build reproducibility is treated as an explicit engineering concern.
5. A subsystem can work in the kernel without being integrated into iOS. The README
   reports WLAN and sensor functionality in the kernel while their iOS interfaces remain
   incomplete.

## Why its platform code is not an A10 port

The reference device is Qualcomm SM4375, with Cortex-A55/A78 CPU clusters, GICv3,
PSCI-based CPU startup, Adreno graphics, Qualcomm storage and power components, and
a different device-tree and peripheral layout.

Project Sweet-10 targets iPhone 7 `iPhone9,1` with A10/T8010 hardware. The SM4375
machine configuration, interrupt topology, memory map, CPU provider, boot shim,
display, touch, storage, power, and GPU code must therefore be treated as
hardware-specific. Do not cherry-pick those implementations into this repository.

The userland identity is another important mismatch: ios-sunstone reports an iPhone X
identity (`iPhone10,3` / `D22AP`) and gesture-based navigation without a Home button.
The iPhone 7 has a physical Home button and Touch ID. SpringBoard behavior and
Home-button/HID integration need separate investigation; matching the userland build
does not make the device identity or interaction model identical.

## Patch-series lessons

The ios-sunstone tree groups work into a long ordered patch series. At a high level its
later patches cover:
- early framebuffer and CPU topology;
- input and physical keys;
- display presentation and page flipping;
- battery, panel brightness and real-time clock;
- GPU user-client and recovery work;
- modem/WLAN and ADSP/sensor support;
- debugging and test instrumentation.

These areas are a useful subsystem checklist. The actual register values, drivers,
interrupts, DMA assumptions, memory addresses, device-tree nodes, and CPU behavior are
specific to sunstone and are not portable implementation material.

## Security and stability caveats

The upstream README explicitly describes the port as experimental and not a usable phone
OS. It reports missing services and a permissive or stubbed security configuration.
Project Sweet-10 must not copy security-disabling changes as a shortcut to SpringBoard.
Security, activation, SEP/Touch ID, data protection, and service dependencies remain
separate research gates.

The upstream README also describes destructive device operations for its own target.
Those operations are not part of this comparison and are not instructions for Project
Sweet-10. This repository's current work remains source review and host-side validation.

## Project Sweet-10 decisions

| Area | Decision |
|---|---|
| XNU 8796 source generation | Keep as a candidate baseline; exact 20H392 kernel commit still needs independent evidence |
| 20H392 userland | Keep as selected reference |
| Generic build/CI structure | Study and independently reproduce |
| Ordered patch discipline | Adopt as a project process |
| Qualcomm machine/platform patches | Do not port |
| Boot shim and hardware drivers | Require independent iPhone9,1 evidence and design |
| iPhone X device identity | Do not assume suitable for iPhone7 UI/input |
| Security stubs or bypasses | Do not adopt as a shortcut |
| SpringBoard milestone | Retain as long-term goal; require stable lower-level gates first |

## Sources

- [ios-sunstone repository](https://github.com/14sea/ios-sunstone)
- [ios-sunstone README](https://github.com/14sea/ios-sunstone/blob/sunstone/README.md)
- [ios-sunstone engineering handoff](https://github.com/14sea/ios-sunstone/blob/sunstone/SUNSTONE.md)
- [ios-sunstone XNU build workflow](https://github.com/14sea/ios-sunstone/blob/sunstone/.github/workflows/xnu.yml)
- [ios-sunstone XNU build notes](https://github.com/14sea/ios-sunstone/blob/sunstone/xnu/README.md)

Reviewed reference revision: `e0471191ddbfb17fde6674db41320bffa832a85b`
(2026-10-22). This is the reference repository revision checked for this note.
