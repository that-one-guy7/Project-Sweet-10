# M3 — iPhone9,1 A10/XNU handoff specification review

## Decision and scope

**M3 is complete only as a reviewed, source-level handoff specification.** This document consolidates the known XNU 8796 ARM64 contract, the pinned PongoOS behavior, the target's static 19H422 evidence, and every important unknown that prevents treating the specification as operational.

This milestone does **not** mean a valid iPhone9,1 runtime handoff has been captured or implemented. It does not authorize a boot attempt, device interaction, exploit use, firmware change, or kernel replacement. The physical iPhone 7 remains on iOS 12.1.4.

## 1. Kernel identity boundary

| Item | Evidence | Status |
|---|---|---|
| Intended userland reference | iOS 16.7.16 build 20H392, donor iPhone10,3 / D22AP / T8015 | Identified as donor only |
| Public XNU source candidate | `xnu-8796.141.3` | Pinned candidate, not proven exact Apple source for donor KernelCache |
| Donor KernelCache identity | XNU `8796.142.1.703.8~1`, `RELEASE_ARM64_T8015` | Binary metadata recorded; exact source/build inputs unknown |
| Target-native static reference | iPhone9,1 / D10AP / T8010 iOS 15.8.8 build 19H422 | Useful for target hardware inventory, not an iOS 16 kernel |
| Target-specific XNU image | No verified iPhone9,1 XNU 8796 image/build | Open |

The donor's userland build number is not a kernel compatibility declaration for iPhone9,1. The target 19H422 KernelCache is not interchangeable with the donor 20H392 KernelCache.

## 2. ARM64 `boot_args` structure

The pinned XNU 8796 ARM64 header and PongoOS revision `4c9b7541629234147fcc778f0ce4162482aaccef` were compared at source level. PongoOS's iOS13 structure view matches the XNU ARM64 field offsets, command-line length, and total structure size.

| Field | Offset |
|---|---:|
| `Revision` | `0x000` |
| `Version` | `0x002` |
| `virtBase` | `0x008` |
| `physBase` | `0x010` |
| `memSize` | `0x018` |
| `topOfKernelData` | `0x020` |
| `Video` | `0x028` |
| `machineType` | `0x058` |
| `deviceTreeP` | `0x060` |
| `deviceTreeLength` | `0x068` |
| `CommandLine[608]` | `0x06c` |
| `bootFlags` (Pongo iOS13 view) | `0x2d0` |
| `memSizeActual` (Pongo iOS13 view) | `0x2d8` |
| Total structure size | `0x2e0` |

**Interpretation:** the compared declarations do not show a structure-layout mismatch. This says nothing about whether the live structure has the right revision, version, values, address, or relationship to a selected target kernel. No live iPhone9,1 boot-argument block has been captured.

## 3. PongoOS behavior boundary

The reviewed PongoOS source establishes several distinct behaviors:

- The normal XNU path retains the incoming Apple boot arguments and original kernel entry point.
- The raw-payload path branches to an uploaded raw stage while passing the existing boot-argument pointer and original entry point in registers.
- The KernelCache-copy helper copies bytes over an existing in-memory image but leaves entry-point selection to its caller; its source comments identify Mach-O parsing and entry-point selection as unfinished work.
- The pinned source has a T8010 HAL selection path and T8010-specific source components.

These are source facts, not a completed Sweet-10 loader. The raw-payload path does not itself parse/relocate an XNU image, establish its memory layout, construct a new target DeviceTree, or validate the target's handoff values. The copy helper is not a complete image loader. The T8010 backend has not been runtime-tested on the user's phone.

## 4. Target evidence that can and cannot be carried into a handoff design

| Area | Static target evidence | Still unknown |
|---|---|---|
| Device identity | iPhone9,1 / D10AP / T8010 | Whether a chosen XNU build has a valid product configuration |
| CPU topology | 19H422 parsed DeviceTree contains CPU0 running and CPU1 waiting | Final runtime CPU state, online count, startup mechanism, coherency and firmware handoff |
| DeviceTree | Hash-verified 19H422 static tree parsed as 227 nodes; ARM-IO/AIC/timer nodes identified | Final boot-time tree, runtime-populated values, complete property and interrupt contract |
| Memory | Static tree artifact inspected | Usable/reserved physical ranges, ownership, alignment, kernel allocation bounds and lifetimes |
| Clock/timebase | Generic XNU property consumers identified | Valid runtime frequency and counter source |
| Interrupts | Target AppleInterruptController metadata matches `aic,1` | IRQ namespace, specifiers, routing, affinity, acknowledge/EOI and IPI behavior |
| PMGR/secondary CPU | Target KernelCache metadata contains AppleT8010PMGR with `pmgr1,t8010`; XNU generic IOPMGR fallback reviewed | Concrete PMGR executable behavior, firmware reset-vector state and secondary-core startup |
| Console/diagnostics | No verified target handoff channel | Early diagnostic mechanism and failure capture |

The 19H422 tree is a static IPSW component, not a live tree. Zero or absent memory, clock, and panic fields must remain unknown; they must not be replaced with guessed values from a donor or another SoC.

## 5. Handoff requirement disposition

| Requirement | Review disposition |
|---|---|
| Kernel/source identity | Candidate and uncertainty documented; exact source/build correspondence open |
| Entry state | Required topic identified; revision-matched register/exception-level state open |
| Boot-argument structure | Source-level layout cross-check complete |
| Boot-argument values/location | Open; no live target capture |
| DeviceTree format and required properties | Static tree parsed; final runtime contract open |
| Memory map and ownership | Open |
| CPU topology and release | Static topology and generic source reviewed; concrete target behavior open |
| Interrupt/timer | Controller identity and generic consumers recorded; functional contract open |
| Image format/loader | Existing Pongo extension points audited; complete Sweet-10 loader absent |
| Root/storage and early services | Open |
| Security/platform services | Open; security policy must not be weakened as a substitute for missing platform support |

## 6. M3 exit criterion and remaining gates

M3's exit criterion is **a reviewed A10 handoff specification**. That review is now complete because the specification identifies the exact source-level structure match, separates PongoOS's existing behavior from a future custom loader, records target-native static evidence, and labels every unresolved runtime field instead of inventing values.

The following work remains mandatory before any future implementation can be considered:

1. Establish a source/build identity and reproducible target-relevant XNU baseline (M2).
2. Obtain authoritative target runtime evidence for memory, DeviceTree, CPU and early platform services.
3. Define and independently validate any custom image-loading design and its complete entry contract.
4. Perform host-side validation in a safe test environment before considering any hardware validation.

M4's early-kernel test milestone remains not started. M5/M6 subsystem and userland research remains separate. M7/SpringBoard remains a long-term goal and has not been reached.

## Sources already audited in this repository

- `docs/pongo-xnu-handoff-analysis.md`
- `docs/pongo-raw-payload-and-copyx-audit.md`
- `docs/platform-audit-status.md`
- `docs/iphone91-19h422-parsed-devicetree-audit.md`
- `docs/a10-h9-cpu-topology-handoff-audit.md`
- `docs/iphone91-19h422-aic-kext-inventory.md`
- `docs/kernel-implementation-readiness.md`
- `boot/HANDOFF_REQUIREMENTS.md`

No device, firmware, partition, or boot state was accessed or changed while preparing this specification.
