# Boot architecture research

This is a design checklist, not a boot procedure.

## Conceptual stages
1. Entry environment provides a controlled execution context.
2. A platform-specific handoff supplies XNU boot arguments, memory description,
   device tree, and CPU state.
3. Early kernel initializes CPU/platform, memory management, interrupts, timer, and console.
4. Kernel services and IOKit matching become available.
5. Root filesystem is discovered and mounted.
6. launchd and required userland services start.
7. backboardd, SpringBoard, and supporting services become stable.

## A10 questions to answer with evidence
- Which boot-argument ABI does the selected XNU revision require?
- Which Apple Device Tree nodes/properties are consumed?
- What CPU exception level and register state are expected at entry?
- Which memory regions are reserved by firmware and security components?
- Which interrupt controller and timer interfaces are used?
- Which display and HID services are needed for a first visible UI?

## Project Sandcastle boundary

Corellium's public Sandcastle README describes its loader as loading a Linux kernel
and device tree via PongoOS. Its `loader/load-linux.c` is a USB host utility that
transfers a device-tree blob and a Linux image through a PongoOS-specific protocol.
That establishes a useful architectural separation between host transport, early
boot environment, kernel image, and device-tree input.

It does not establish an XNU handoff contract. The Linux image format, USB protocol,
PongoOS command strings, and Sandcastle device-tree assumptions must not be treated as
XNU ABI or iPhone9,1 platform data.

See [the source review](sandcastle-loader-review.md) and
[the handoff evidence checklist](../boot/HANDOFF_REQUIREMENTS.md).

## PongoOS and a custom XNU image

The pinned PongoOS source contains a registered A10/T8010 HAL platform driver, a T8010-specific USB resource provider consumed by the Synopsys OTG driver, and T8010 cases in its AES and Reconfig Engine setup. This makes it a plausible early execution environment to investigate on iPhone9,1, but these source paths have not been validated in a real session on the target. PongoOS's normal KPF path is not a completed Sweet-10 custom-kernel loader. Its `bootr` raw-payload entry point passes through existing boot arguments and the original kernel entry point, while `loadx` copies bytes over the existing KernelCache but leaves `gEntryPoint` adjustment to another component. Neither implements the complete Sweet-10 image/boot-argument contract. See [the T8010 platform-backend audit](pongo-t8010-platform-backend-audit.md), [PongoOS/XNU handoff analysis](pongo-xnu-handoff-analysis.md), and [the raw-payload/copy helper audit](pongo-raw-payload-and-copyx-audit.md).

## Evidence status

The project has not yet verified the exact 20H392 kernel source revision, XNU entry
requirements for the selected revision, or iPhone9,1 device-tree and memory-map values.
All target-specific addresses, interrupt IDs, frequencies, and hardware constants
remain unknown. Do not copy hardware values from ios-sweet: its target is Qualcomm SM7150.
