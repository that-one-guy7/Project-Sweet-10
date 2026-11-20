# Kernel implementation readiness gate

## Purpose

This document defines when Project Sweet-10 may move from source research into
an iPhone9,1-specific XNU kernel implementation. It distinguishes a source
checkout, a successful generic compilation, a target-configured kernel, and a
kernel that has actually been demonstrated to start on the target. These are
different milestones and must not be described interchangeably.

The target is iPhone 7, product type iPhone9,1, board D10AP, A10/T8010.
The selected iOS 16 userland reference is iOS 16.7.16 build 20H392.

## Current decision

**Not ready to create a bootable iPhone9,1 kernel.** The repository has useful
source and restore-identity research, but no verified iPhone9,1 XNU 8796
machine configuration, no target device-tree/boot-argument evidence, and no
reproducible iPhoneOS ARM64 baseline build.

The supplied 20H392 BuildManifest supports iPhone10,3 and iPhone10,6 only.
Its four BuildIdentity entries use A11/T8015 chip ID 0x8015 and D22AP/D221AP
board identities. It is a valid donor reference for userland study, not a
target manifest for iPhone9,1.

## Readiness gates

| Gate | Required evidence | Current status |
|---|---|---|
| G1 — Source identity | Exact XNU source revision tied to the chosen 20H392 kernel component, or a clearly documented candidate with uncertainty | Candidate xnu-8796.141.3 is pinned; Apple source-to-kernelcache mapping is not established |
| G2 — Historical A10 support | Full dependency and interface review of the old T8010/H9 implementation against the selected baseline | Historical T8010/H9 profile found in xnu-7195.121.3; absent at corresponding paths in xnu-8019.80.24 and xnu-8796.141.3; dependency migration not reviewed completely |
| G3 — Build environment | Reproducible unmodified iPhoneOS ARM64 baseline build with recorded host, SDK, compiler, generated headers, external dependencies, configuration selections, and logs | Not started; toolchain and valid target machine/platform selection are not pinned |
| G4 — Target platform evidence | Revisioned iPhone9,1/D10AP evidence for CPU topology/features, memory map, clocks, interrupt/timer topology, storage, and required platform services | Incomplete; no target-specific values are approved |
| G5 — Device-tree contract | Verified target device-tree schema and required properties, with each value tied to reliable source evidence | Not established; current inventory documents consumers only |
| G6 — Entry/handoff contract | Exact XNU entry ABI, boot-argument format/version, execution state, memory ownership, and device-tree handoff requirements for the selected source | Not established |
| G7 — Static and host validation | Reproducible compile/static checks, unit tests for supporting tools, and review of all target-specific patches | Not started for a target-specific kernel |
| G8 — Early platform services | Evidence-backed plans for interrupt controller, timer, console/diagnostics, storage/root discovery, and required security services | Incomplete |
| G9 — Userland integration | A separately validated compatibility plan for launchd and required iOS 16 services on the target platform | Not started |

## What can be done before the gate is met

The project may continue with read-only source comparisons, build-system
investigation, data provenance, host-side validators, documentation, and
reproducible tests that do not depend on invented hardware values.

The first build milestone, once G1-G3 are resolved, is an unmodified source
baseline build. That result is only a compiler/build-system milestone. It does
not prove iPhone9,1 support.

Target-specific source work must be developed as small, reviewable patches.
Every machine constant, device-tree property, and platform assumption must
have a source and revision recorded. Unknown values remain unknown; no values
are copied from the Qualcomm SWEET port or from the iPhone X donor.

## What "bootable" means in this project

A kernel artifact is not called iPhone9,1-bootable merely because it:
- is an ARM64 Mach-O file;
- compiles successfully;
- uses the 20H392 build number in its notes;
- contains a historical T8010 CPU configuration;
- matches an iPhone X donor KernelCache path or digest; or
- can be loaded by an early boot environment.

The term requires evidence that the selected kernel build, target platform
configuration, device-tree contract, entry state, and required early services
are all consistent for iPhone9,1. A later userland milestone is separately
required before claiming that iOS 16 userland or SpringBoard is functional.

This repository gate authorizes source review and host-side validation only.
It does not describe device boot, exploit execution, firmware installation,
partition writes, or recovery operations.

## Sources and project records

- [XNU baseline selection](xnu-baseline-selection.md)
- [XNU baseline build inputs](xnu-build-inputs.md)
- [XNU configuration selection audit](xnu-config-selection.md)
- [A10/T8010 XNU evidence audit](a10-t8010-xnu-evidence-audit.md)
- [ARM64 platform audit status](platform-audit-status.md)
- [iPhone9,1 device-tree property inventory](../device-tree/PROPERTY_INVENTORY.md)
- [XNU handoff requirements](../boot/HANDOFF_REQUIREMENTS.md)
- [Uploaded 20H392 BuildManifest audit](uploaded-20h392-buildmanifest-audit.md)
