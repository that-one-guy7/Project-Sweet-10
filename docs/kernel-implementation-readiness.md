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
| G2 — Historical A10 support | Full dependency and interface review of the old T8010/H9 implementation against the selected baseline | The read-only source matrix now checks ten public XNU snapshots (7195, 8020, 8019, 8796.101, 8796.141, 12377.1.9, and four 10002 tags); T8010/H9 appears only in xnu-7195.121.3 at the audited machine-selection and board paths. A full-tree textual scan now covers 3,508 XNU 7195 and 3,961 XNU 8796 source/build files for all 12 H9 macros; 23 locally resolvable include files and two resolver gaps were recorded. This completes the textual inventory, not conditional evaluation, private/generated inputs, full dependency closure, or migration review |
| G3 — Build environment | Reproducible unmodified iPhoneOS ARM64 baseline build with recorded host, SDK, compiler, generated headers, external dependencies, configuration selections, and logs | Not started; pinned xnu-8796.141.3 normal ARM64 machine allowlist omits T8010; SDK device-map contents and host toolchain are unverified |
| G4 — Target platform evidence | Revisioned iPhone9,1/D10AP evidence for CPU topology/features, memory map, clocks, interrupt/timer topology, storage, and required platform services | Incomplete. Target 19H422 metadata confirms AppleInterruptController (aic,1), AppleT8010PMGR (pmgr1,t8010), and generic ApplePMGR (pmgr1,bring-up). Corrected generic ApplePMGR executable range: 0xfffffff0065b6000–0xfffffff0065eaa4b (0x34a4c bytes), mapped to __PLK_TEXT_EXEC; target KernelCache SHA-256: 7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee. GOT labels and caller setup strongly support ApplePMGR deriving from IOPMGR with a base subobject at offset zero. The generic prelink header SHA-256 is 4764017feef6d87c1f8a524bf04ec1148817d61fd482639e252325fd0300f43f. Three AArch64 sequences construct the ApplePMGRFunctionEnableCPUCore string VA 0xfffffff00567132c in x1, pass class size 0x38, and call the OSMetaClass constructor stub at 0xfffffff0065ea680. Two load x2 via GOT slot 0x158 (VA 0xfffffff006f18fd8); a third passes x2=x19 and x0=0xfffffff007ae14c0. This is evidence of metaclass initialization/registration for the class, not proof of its callFunction callback, D10AP instantiation, or CPU-start behavior. The filtered output did not show a direct immediate reference to site.ApplePMGRFunctionEnableCPUCore at VA 0xfffffff00567134b. GOT[0x158] now resolves to 0xfffffff0079e4dd0, mapped to writable __PRELINK_DATA.__data at file offset 0x2690dd0; the user's 0x80-byte on-disk dump at that offset is all zero. Its class/superclass identity remains unresolved, and ipsw kernel cpp did not discover classes or inheritance for this KernelCache. See the [EnableCPUCore superclass-slot audit](iphone91-19h422-applepmgr-enablecore-superclass-slot-audit.md). Concrete IOPMGR::enableCPUCore override, secondary-core reset release, IRQ delivery, timer, console, storage, and runtime attachment remain unverified. See the [CPU-function string audit](iphone91-19h422-applepmgr-cpu-function-string-audit.md) and [generic ApplePMGR GOT/stub analysis](iphone91-19h422-applepmgr-got-stub-analysis.md) |
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
- [iPhone9,1 19H422 AppleT8010PMGR prelinked KEXT static audit](iphone91-19h422-applet8010pmgr-binary-audit.md)
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


## Ten-snapshot T8010/H9 matrix update (2026-11-21)

The public-source comparison now checks ten pinned Apple XNU snapshots:
`xnu-7195.121.3`, `xnu-8020.101.4`, `xnu-8019.80.24`,
`xnu-8796.101.5`, `xnu-8796.141.3`, `xnu-12377.1.9`,
`xnu-10002.1.13`, `xnu-10002.41.9`, `xnu-10002.61.3`, and
`xnu-10002.81.5`. At the audited build-selection paths, T8010/H9 is
present only in the historical 7195 snapshot. All four 10002 tags omit the
T8010 board block, the normal ARM64 allowlist entry, and the historical
`H9.h` path; their normal ARM64 machine list is
`BCM2837 T6000 T8101 T8103 VMAPPLE`. The latter three tags share the
same inspected source-file blob hashes, so they are not four independent
revisions of those files.

The read-only matrix workflow passed on PR #136
([run 44938201241](https://github.com/that-one-guy7/Project-Sweet-10/actions/runs/44938201241)):
all ten pinned source checkouts, source-lock checks, synthetic tests, and
the matrix audit completed successfully. The separate pinned XNU/PongoOS
source-check workflow also passed ([run 44938201251](https://github.com/that-one-guy7/Project-Sweet-10/actions/runs/44938201251)).

This remains a bounded comparison of `board_config.h`, `MakeInc.def`,
the `MakeInc.kernel` machine-selection guard, and the exact historical
`H9.h` path. It is not a full-tree audit or a disclosure of Apple's private
product build inputs. It does not establish the exact 20H392 source commit,
a target configuration, compilation, hardware support, ABI compatibility,
runtime behavior, or bootability. G1/G2 remain open; no target-specific
kernel implementation is authorized by this result. The physical iPhone 7
remains on iOS 12.1.4 and M7/SpringBoard has not started.


## Full-tree H9 consumer audit update (2026-11-21)

The read-only scanner inventories all 12 feature macros defined by historical
XNU 7195 `H9.h` across the pinned XNU 7195 and 8796 source trees. The scan
covered 3,508 and 3,961 candidate source/build files respectively, resolved
23 local include files, and retained two unresolved SDK-style include names.
Notable results include persistent generic Hurricane, PMU/AIC, page-size,
PAN, sleep, and kernel-protection references, while
`HAS_MIGSTS`, `HAS_CPMU_L2C_EVENTS`, and
`SINGLE_STEP_RETIRE_ERRATA` had no textual matches in the scanned candidate
files. H13 defines several shared feature macros, but its values are not
substitutes for H9/T8010 values.

This is a textual source inventory, not a preprocessor, linker, or build-input
dependency graph. It does not establish active conditional branches, Apple
product build settings, hardware feature state, ABI compatibility, or target
support. The full-tree scan and its limits are documented in
[the H9/T8010 source audit](h9-source-fulltree-audit.md). The original
workflow passed on PR #82 run
[44864823137](https://github.com/that-one-guy7/Project-Sweet-10/actions/runs/44864823137);
this current-main port reruns the same validation before merge. G2 remains
open pending manual per-feature migration and interface review.
