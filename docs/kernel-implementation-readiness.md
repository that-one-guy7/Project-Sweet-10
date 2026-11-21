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
machine configuration (its normal ARM64 allowlist omits T8010), no target
device-tree/boot-argument evidence, and no reproducible iPhoneOS ARM64 baseline build.

The supplied 20H392 BuildManifest supports iPhone10,3 and iPhone10,6 only.
Its four BuildIdentity entries use A11/T8015 chip ID 0x8015 and D22AP/D221AP
board identities. It is a valid donor reference for userland study, not a
target manifest for iPhone9,1.

A source-versus-binary cross-check found that the inspected 20H392 donor
KernelCache reports `RELEASE_ARM64_T8015`, while public
`xnu-8796.141.3` exposes neither a normal T8015 nor T8010 ARM64 machine
profile. Its embedded label (`8796.142.1.703.8~1`) can be an XBS
project/source-version label plus build number, not necessarily a Git tag.
The donor's exact Apple source commit and product-specific build inputs remain
unknown.

An independent downstream UniXNU profile for a OnePlus 13 / SM8750 port now
co-pins the same donor KernelCache SHA-256 with
`xnu-8796.141.3` / commit
`1b191cb58250d0705d8a51287127505aa4bc0789`. Its report records 62 patches
applying to a clean source checkout, but explicitly leaves compilation,
binary ABI, and hardware validation separate. Its rebuilt-kernel path is
`DEVELOPMENT_ARM64_BCM2837`, not T8015 or T8010. This is useful downstream
corroboration for the public candidate, not an Apple source-to-binary
attestation or iPhone9,1 support result. See the
[version-stamp provenance note](xnu-kernel-version-stamp-provenance.md),
[public-source versus shipped-KernelCache comparison](xnu-public-source-vs-shipped-kernel.md),
and [UniXNU 20H392 cross-check](unixnu-20h392-xnu-baseline-crosscheck.md).

## Readiness gates

| Gate | Required evidence | Current status |
|---|---|---|
| G1 — Source identity | Exact XNU source revision tied to the chosen 20H392 kernel component, or a clearly documented candidate with uncertainty | Candidate xnu-8796.141.3 is pinned; an independent downstream UniXNU profile co-pins its commit with the exact 20H392 donor KernelCache SHA and reports 62 clean patch applications. That report excludes compilation, binary ABI and hardware; the profile uses DEVELOPMENT_ARM64_BCM2837, not T8015/T8010. Public version-stamping logic explains why the donor's 8796.142.1.703.8~1 label is not necessarily a Git tag. Exact Apple source provenance and product-specific inputs remain unknown |
| G2 — Historical A10 support | Full dependency and interface review of the old T8010/H9 implementation against the selected baseline | Public source presence/absence is pinned and checked across xnu-7195.121.3, xnu-8019.80.24, and xnu-8796.141.3; the full historical dependency graph and migration remain incomplete |
| G3 — Build environment | Reproducible unmodified iPhoneOS ARM64 baseline build with recorded host, SDK, compiler, generated headers, external dependencies, configuration selections, and logs | Not started; pinned xnu-8796.141.3 normal ARM64 machine allowlist omits T8010; SDK device-map contents and host toolchain are unverified |
| G4 — Target platform evidence | Revisioned iPhone9,1/D10AP evidence for CPU topology/features, memory map, clocks, interrupt/timer topology, storage, and required platform services | Incomplete; the 19H422 KernelCache now confirms an AppleInterruptController KEXT and `aic,1` personality, but IRQ routing, EOI, timer, CPU/memory, storage, and runtime provider contracts remain unresolved |
| G5 — Device-tree contract | Verified target device-tree schema and required properties, with each value tied to reliable source evidence | Incomplete; static `aic,1` DeviceTree / KEXT IONameMatch overlap is confirmed, but cell/property requirements, full interrupt specifiers, timer contract, and runtime-populated values are not established |
| G6 — Entry/handoff contract | Exact XNU entry ABI, boot-argument format/version, execution state, memory ownership, and device-tree handoff requirements for the selected source | Not established |
| G7 — Static and host validation | Reproducible compile/static checks, unit tests for supporting tools, and review of all target-specific patches | Not started for a target-specific kernel |
| G8 — Early platform services | Evidence-backed plans for interrupt controller, timer, console/diagnostics, storage/root discovery, and required security services | Incomplete; target-native `AppleInterruptController` KEXT and `aic,1` personality are identified in 19H422 metadata, but runtime attachment, IRQ mapping/routing, EOI, timer callbacks/frequency, console, storage, and security services remain open |
| G9 — Userland integration | A separately validated compatibility plan for launchd and required iOS 16 services on the target platform | Not started |

## What can be done before the gate is met

The project may continue with read-only source comparisons, build-system
investigation, data provenance, host-side validators, documentation, and
reproducible tests that do not depend on invented hardware values. PongoOS
source review must keep its documented KPF-assisted XNU path separate from a
custom Sweet-10 XNU image loader; the latter requires an independently verified
image format, entry contract, boot_args, memory map, and target DeviceTree.
See [PongoOS/XNU handoff analysis](pongo-xnu-handoff-analysis.md).

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
- [Historical T8010 XNU profile CI verification](xnu-machine-history-ci.md)
- [A10/T8010 XNU evidence audit](a10-t8010-xnu-evidence-audit.md)
- [Public XNU source versus shipped KernelCache identities](xnu-public-source-vs-shipped-kernel.md)
- [20H392 XNU kernel version-stamp provenance](xnu-kernel-version-stamp-provenance.md)
- [Independent UniXNU 20H392 XNU baseline cross-check](unixnu-20h392-xnu-baseline-crosscheck.md)
- [ARM64 platform audit status](platform-audit-status.md)
- [iPhone9,1 device-tree property inventory](../device-tree/PROPERTY_INVENTORY.md)
- [XNU handoff requirements](../boot/HANDOFF_REQUIREMENTS.md)
- [Uploaded 20H392 BuildManifest audit](uploaded-20h392-buildmanifest-audit.md)


## Additional build-system finding

A versioned audit of Apple's `makedefs/MakeInc.def` found T8010 in
the normal ARM64 machine allowlist for `xnu-7195.121.3`, but not in
`xnu-8019.80.24` or `xnu-8796.141.3`. The pinned
`xnu-8796.141.3` kernel make rules validate the selected machine config
against that allowlist. Its `MakeInc.top` can optionally derive
product-to-KernelPlatform mappings from an embedded-device-map database
inside the selected SDK platform bundle, but the contents of the relevant SDK
database have not been inspected.

The shipped-binary cross-check adds an important qualification: the 20H392
donor KernelCache reports `RELEASE_ARM64_T8015`, even though public
`xnu-8796.141.3` also omits T8015 from its normal ARM64 list and board
configuration. The public 8796 snapshot therefore does not, by itself,
reproduce all machine-selection inputs represented by the donor KernelCache.
This is evidence of incomplete public-source/build-input correspondence,
not proof that an internal Apple source tree lacked T8015 or that later XNU
cannot support T8010. The donor version string
(`8796.142.1.703.8~1`) is not an exact match for the candidate public tag
(`xnu-8796.141.3`).

This narrows the blocker: it is not enough to find a historical T8010 header
or to copy the visible machine-selection name. The selected public baseline
does not expose a T8010 profile, and its exact mapping to the shipped donor
kernel and product-specific inputs remains unresolved. Do not bypass that
selection check, copy H9 wholesale, or claim that a VMAPPLE build is an
iPhone7 build. See the
[public-source versus shipped-KernelCache comparison](xnu-public-source-vs-shipped-kernel.md).


## Expanded public-source comparison and implementation gate (2026-11-20)

The source-history audit has been expanded to six pinned public XNU
snapshots. Historical `xnu-7195.121.3` includes T8010/H9, while public
`xnu-8020.101.4`, `xnu-8019.80.24`, `xnu-8796.101.5`,
`xnu-8796.141.3`, and `xnu-12377.1.9` omit the T8010/H9 profile at the
audited ARM64 machine-selection and board-configuration paths. The later
source matrix is checked by `tools/audit_xnu_public_source_matrix.py`;
pinned commits and tag-object identities are stored under `xnu/history/`.

This finding must be read alongside both shipped KernelCache identities:
the iPhone7 19H422 target reports `8020.241.44~1/RELEASE_ARM64_T8010`,
and the iPhoneX 20H392 donor reports
`8796.142.1.703.8~1/RELEASE_ARM64_T8015`. The public comparison tags
`xnu-8020.101.4` and `xnu-8796.141.3` are not exact source attestations
for those shipped binaries. Exact Apple source revisions and
product-specific build inputs remain unknown. The missing public T8010
profile is a source-provenance and porting blocker; it does not prove that
the shipped target kernel lacked T8010 support.

Apple's official iOS 16 compatibility list does not include iPhone7; the
list starts at iPhone8. Apple's security-release table lists iOS 15.8.8 for
iPhone7 and iOS 16.7.16 for iPhone8, iPhone8 Plus, and iPhoneX. The project's
20H392 userland is consequently a donor reference, not an official iPhone7
build. See [the kernel and driver implementation roadmap](driver-kernel-implementation-roadmap.md).

The implementation threshold is explicit: do not start target-specific
XNU platform or driver code until G1-G6 have evidence-backed answers and
G7 host verification is in place. The first hardware driver cannot be
selected until the actual D10AP interrupt-controller and timer DeviceTree
contracts are resolved. Do not assume AIC or copy donor/Qualcomm register
values. The next highest-value source task is the full transitive T8010/H9
dependency and conditional-consumer closure, beyond the existing direct
feature-macro scan.
