# Reference study: ios-qemu and the 20H392 userland

## Executive summary

The public `lgrachov/ios-qemu` project reports running the unmodified iPhone X
iOS 16.7.16 userland, build `20H392`, in QEMU on Apple Silicon. It uses a rebuilt
XNU kernel from the iOS 16-era `xnu-8796` source family, a project-specific patch
series, and emulated QEMU devices.

This is a valuable compatibility reference because the userland build selected by
Project Sweet-10 is the same. It is not an iPhone 7 port and does not demonstrate
A10/T8010 support.

Reference reviewed: repository README, XNU build workflow, and patch inventory on
2026-11-20. Upstream is an active project; re-check its current revision before
relying on implementation details.

## What the project reports

| Area | Upstream-reported behavior |
|---|---|
| Userland | Unmodified iPhone X iOS 16.7.16 (20H392) userland |
| Kernel | Rebuilt from Apple's open-source XNU 8796 generation with a project patch series |
| Execution environment | QEMU `virt` machine on Apple Silicon using host virtualization |
| Boot description | A small virtual-machine boot stub and generated Apple Device Tree hand off to XNU |
| Storage | iOS root on an HFS+ volume presented through an emulated UFS controller |
| Display | QEMU ram framebuffer; CPU-rendered CoreAnimation |
| Input | Virtual tablet events surfaced as HID digitizer input |
| Device identity | iPhone X (`iPhone10,3` / `D22AP`), gesture navigation |
| GUI | README reports lock screen, SpringBoard, Settings, and Safari |

These are claims from the upstream README, not tests performed by Project Sweet-10.

## Reported limitations

The upstream README explicitly lists no GPU, Secure Enclave, microphone, camera,
Bluetooth, cellular, location, or Face ID. It also describes its security model as
disabled or incomplete, including permissive code-signing and sandbox behavior.

Those limitations are important. Project Sweet-10 must not adopt weakened security
settings, stub security services, or disabled policy enforcement as a shortcut to
SpringBoard. The upstream project is an experimental research environment, not a
secure or usable phone operating system.

## Why this does not solve the iPhone 7 target

The QEMU project uses a virtual board and virtual peripherals. Its generated device
tree describes that emulated environment, not an iPhone 7 board. The guest identity
is iPhone X, not `iPhone9,1`. Its display, input, storage, timer, networking, and
other device interfaces are emulated.

Project Sweet-10 targets iPhone 7 (`iPhone9,1`, A10/T8010). Therefore:

- QEMU machine configuration is not an A10 machine configuration.
- Virtual device drivers are not iPhone 7 hardware drivers.
- The generated QEMU device tree is not an iPhone 7 device tree.
- An iPhone X userland boot in QEMU does not prove iPhone 7 board support.
- The reported result does not establish a direct boot path through Project Sandcastle.

## What Project Sweet-10 can learn safely

1. Keep source revision, patch series, build environment, and artifacts independently
   pinned and recorded.
2. Separate generic XNU build compatibility from platform-specific device support.
3. Treat device-tree generation and the boot environment as explicit interfaces.
4. Track each subsystem's evidence and observed status instead of treating a GUI boot
   as proof that all hardware is supported.
5. Use a virtualized reference as a separate research track for understanding
   userland dependencies, not as a substitute for A10 platform evidence.

## Patch-series classification

The upstream patch inventory shows several distinct categories:

- compiler and toolchain compatibility;
- machine configuration and generic virtual-machine support;
- early framebuffer and serial diagnostics;
- memory-map and page-table compatibility;
- missing public-header or symbol gaps;
- QEMU-specific device and service support.

This categorization is useful for organizing our own future patch review. The patches
must not be copied wholesale: their assumptions are tied to the upstream QEMU and
previous SWEET environments. Any Project Sweet-10 patch would need an independently
documented reason, a source-level review, and target-specific evidence.

## Recommended project decision

Keep `ios-qemu` as a **20H392 userland compatibility reference**. Do not make QEMU
support a prerequisite for the physical iPhone 7 port, and do not treat a QEMU boot
as evidence of A10 support.

The immediate Project Sweet-10 gates remain:

1. Verify the exact XNU kernel metadata associated with the selected 20H392 reference.
2. Reproduce a clean, unmodified public XNU source build in a documented host environment.
3. Identify the iPhone9,1 platform configuration and required hardware interfaces from
   reliable target-specific evidence.
4. Only then assess which parts of the boot architecture can be shared with Sandcastle.

## Sources

- [ios-qemu repository](https://github.com/lgrachov/ios-qemu)
- [ios-qemu README](https://github.com/lgrachov/ios-qemu/blob/main/README.md)
- [ios-qemu XNU build workflow](https://github.com/lgrachov/ios-qemu/blob/main/.github/workflows/xnu.yml)
- [ios-qemu XNU patch inventory](https://github.com/lgrachov/ios-qemu/tree/main/xnu/patches)
- [Project Sweet-10 XNU baseline lock](../xnu/BASELINE.lock.json)
- [Project Sweet-10 kernel/userland match status](kernel-userland-match.md)
