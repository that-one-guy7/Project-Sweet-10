# Project Sandcastle loader: source review

## Scope and source basis

This is a read-only review of Corellium's public `projectsandcastle` repository,
specifically its README and `loader/load-linux.c`. It is not a porting guide or a
procedure for loading an image onto a phone.

Reviewed source:
- Repository: https://github.com/corellium/projectsandcastle
- Branch: `master`
- Reviewed tree: `03db9c6ae04141eb940f3b9f56d446f50d57fadf`
- Files: `README.md`, `loader/load-linux.c`, `loader/Makefile`

The repository README describes the project as Android/Linux for iPhone and says its
loader loads a kernel and device tree via PongoOS. The loader source is explicitly
named and structured around a Linux image (`linux.bin`).

## What the source establishes

At a high level, the loader implements a host-to-device handoff protocol over USB:
it locates a device using USB descriptors, opens an interface, transfers a device-tree
blob, signals that the tree has been received, transfers a Linux kernel image, and
then sends a boot request.

The source uses vendor-specific USB control transfers and bulk transfers. The protocol
strings and endpoint details belong to this particular PongoOS/Sandcastle environment;
they are not an XNU boot ABI and should not be copied into Project Sweet-10 as though
they were one.

The README also identifies separate Sandcastle utilities for syscfg extraction and
touch support. These are Linux project components. Their existence does not establish
that the same interfaces, drivers, or userspace services are available to an iOS/XNU
kernel.

## What it does not establish

The reviewed source does not demonstrate:
- an XNU-compatible boot handoff;
- the correct boot arguments for XNU 8796;
- an iPhone9,1 device tree or A10 platform configuration;
- the required CPU exception-level or register state for an XNU entry point;
- XNU-compatible memory-map reservations;
- A10 interrupt-controller, timer, storage, display, or HID initialization;
- an iOS root filesystem or launchd startup path.

A loader that can transfer and start a Linux kernel is therefore a useful example of
a boot-environment boundary, but it is not a ready-made XNU loader.

## Engineering observations from the source

The source is a small, target-specific utility rather than a reusable boot framework.
Its USB identity checks, transfer framing, command strings, and assumptions about the
PongoOS endpoint are tightly coupled to that environment. The code also performs
minimal validation of the supplied device-tree and kernel payloads. Those observations
are reasons to treat it as historical architecture reference, not production-quality
code to reuse.

## Project Sweet-10 decision

Use Sandcastle only as a conceptual reference for separating:
1. a host-side transport tool;
2. an early boot environment;
3. a kernel image;
4. a device-tree description;
5. a kernel-specific handoff contract.

Project Sweet-10 must independently establish the XNU 8796 entry contract and
iPhone9,1 platform data. No Sandcastle loader code, USB protocol, Linux device tree,
or Qualcomm/Sandcastle hardware values are imported by this change.

## Next evidence gate

Before an A10 boot design can be considered, the project needs authoritative,
revision-matched evidence for XNU entry requirements and iPhone9,1 platform metadata.
The current property inventory deliberately leaves all target-specific addresses,
interrupts, frequencies, and ranges unknown.

No device interaction, boot attempt, firmware modification, or partition write was
performed for this review.
