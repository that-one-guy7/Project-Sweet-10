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

PongoOS is the proposed early execution environment, but its documented Pongo-plus-KPF path is not the same thing as a Sweet-10 custom-kernel loader. Upstream documents a Pongo shell output and a consolidated PongoOS/KPF output that proceeds to XNU. The KPF source searches and patches existing XNU kernel code. No public source reviewed here establishes that this path loads an arbitrary Sweet-10 kernel or builds the required iPhone9,1 boot arguments. See [PongoOS/XNU handoff analysis](pongo-xnu-handoff-analysis.md).

## Evidence status

The project has not yet verified the exact 20H392 kernel source revision, XNU entry
requirements for the selected revision, or iPhone9,1 device-tree and memory-map values.
All target-specific addresses, interrupt IDs, frequencies, and hardware constants
remain unknown. Do not copy hardware values from ios-sweet: its target is Qualcomm SM7150.
