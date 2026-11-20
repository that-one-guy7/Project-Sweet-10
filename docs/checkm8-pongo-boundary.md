# checkm8 and PongoOS: architecture boundary

## Purpose and safety scope

This is a conceptual, read-only architecture note for Project Sweet-10. It explains where checkm8 and PongoOS sit in the boot architecture; it is not a runbook. It intentionally contains no device-entry sequence, exploit invocation, DFU procedure, payload-transfer commands, or instructions for modifying or booting a phone.

**Project rule:** keep all current work to source review and host-side validation. Do not use this note as authorization to interact with a device or attempt a boot.

## Terms

- **checkm8** is a BootROM-level exploit associated with a family of Apple devices. Its role is to establish an early execution foothold; it does not itself provide an iOS 16 kernel, an iPhone9,1 device tree, or a working platform port.
- **PongoOS** is described by its upstream project as a pre-boot execution environment for Apple boards built on top of checkra1n. It is a separate execution stage before the main operating system.
- **XNU** is the kernel Sweet-10 is researching. A PongoOS environment and an XNU kernel are different components with different responsibilities and interfaces.
- **A boot handoff** is the contract between the pre-boot environment and the kernel: CPU state, memory description, device tree, boot arguments, and other platform-specific inputs.

Primary references:
- [checkra1n/PongoOS README](https://github.com/checkra1n/PongoOS): upstream description of PongoOS, its components, and its relationship to checkra1n.
- [Corellium Project Sandcastle](https://github.com/corellium/projectsandcastle): an example of a Linux-oriented project using PongoOS; it is not an XNU loader.
- [Project Sweet-10 boot architecture note](boot-architecture.md): the kernel handoff evidence still missing for this target.

## What PongoOS does not prove

Reaching a pre-boot shell would establish only that an earlier stage executed. It would not establish any of the following:

1. that the selected iOS 16.7.16 (20H392) kernel is the right kernel for the target;
2. that XNU `xnu-8796.141.3` has a verified iPhone9,1 platform configuration;
3. that the required A10 memory map, device tree, interrupt/timer setup, or CPU entry state is known;
4. that storage, display, touch, audio, baseband, SEP, or other device services are supported;
5. that launchd, SpringBoard, or the rest of the iOS userland can start and remain stable.

At the inspected upstream revision `4c9b7541629234147fcc778f0ce4162482aaccef`, the PongoOS README lists Pongo-only and Pongo-plus-KPF outputs. It describes the Pongo-only image as reaching the Pongo shell and the consolidated Pongo/KPF image as automatically running KPF before proceeding to XNU. The KPF source contains callbacks that search and patch existing kernel instruction streams (including dyld, AMFI/trust-cache, and root-mount paths). This does not document a general loader for an arbitrary custom XNU image. See [the source-based Pongo/XNU handoff analysis](pongo-xnu-handoff-analysis.md).

## Relevance to iPhone 7 / T8010

The iPhone 7 is an A10-generation device. The pinned PongoOS source goes beyond generic SoC recognition: it registers an Apple A10 (T8010) HAL platform driver, provides USB resource values consumed by the Synopsys OTG driver, and includes T8010 AES and Reconfig Engine setup paths. The backend is selected using the SoC number derived from the incoming DeviceTree, not an independent CPID fuse read. This is meaningful source-level PongoOS support, making it a plausible pre-boot environment to investigate on iPhone9,1. It is not proof that this exact build runs on the user's phone or that the USB controller works at runtime. See the [T8010 backend audit](pongo-t8010-platform-backend-audit.md). Exploit-family compatibility, PongoOS runtime compatibility, XNU source compatibility, and iOS userland compatibility remain separate gates.

A search result showing the string `T8010` in an XNU test source file must not be treated as proof of platform bring-up. In particular, test-only references or code-signing test tables do not establish a complete CPU/platform implementation.

## Project decision

- Keep PongoOS documented as a possible pre-boot architecture reference, not as the Sweet-10 kernel or a completed XNU loader.
- Keep Sandcastle's Linux handoff separate from XNU requirements.
- Do not import device-specific values from other ports.
- Require revision-matched XNU source evidence and independently sourced iPhone9,1 platform metadata before making any support claim.
- Keep all verification in the repository to static inspection, documentation checks, and host-side tests.

## Current status

- [x] PongoOS role distinguished from XNU and iOS userland.
- [x] Sandcastle's Linux-specific boundary already documented.
- [ ] Exact 20H392 kernel metadata independently established.
- [ ] iPhone9,1 XNU platform support established from authoritative source.
- [ ] A10-specific handoff contract established from reliable evidence.
- [x] PongoOS T8010 source backend identified (HAL/USB/AES/Recfg); runtime validation on iPhone9,1 remains not started.
- [ ] Custom Sweet-10 XNU image-loading contract separated from PongoOS's documented KPF-assisted XNU path.
- [ ] Any controlled hardware validation: not started and outside this documentation milestone.

No device was connected or changed for this review. No firmware, boot payload, exploit tool, device data, or proprietary image is included.
