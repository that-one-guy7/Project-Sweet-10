# H9/T8010 versus XNU 8796 protection-model source map

## Purpose and scope

This note expands the existing [H9/T8010 migration-risk classification](h9-t8010-migration-risk-classification.md) into a source map for the protection and pmap-related controls that are easy to conflate when comparing the historical T8010/H9 profile with the public XNU 8796 candidate.

The comparison is static and pinned to public source. It does not reconstruct Apple's private 20H392 build inputs, evaluate the actual iPhoneOS preprocessor configuration, identify the exact XNU source commit used for the 20H392 donor, or prove the integrity mode selected by the 19H422 iPhone9,1 kernel. It does not establish page-table state, runtime memory protections, or hardware behavior.

The physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition, security, or boot state was accessed or changed.

## Source identities used

| Source | Ref / identity | File-level cross-check |
|---|---|---|
| Historical T8010/H9 source | Apple XNU `xnu-7195.121.3` | `H9.h` blob `53143c7b6d8efbea630bf2afc32e96fd5ed161fb`; `board_config.h` blob `0990f9885ea9adb9ca453e3a57241f0d0155fa78`; `apple_arm64_common.h` blob `0dc69b246e6258eb784093c61c0d7221016d0768`; `start.s` blob `f783e7538c03f65d7030cc2a6a5585073b66484d` |
| Public iOS 16-generation source candidate | Apple XNU `xnu-8796.141.3`, commit `1b191cb58250d0705d8a51287127505aa4bc0789` | `start.s` blob `e5336e5a1cce791baefa1e96c8dc5ae71c79a605`; `cpu.c` blob `94e91306b14364f720ea80e46d853035aabd78e6`; `arm_vm_init.c` blob `d89b0f19cff72967d8f83d22c75ebd916c14f00a`; `machine_routines_asm.s` blob `2449334f5c970c7678b70a3dbfdecb3f6c4fe94b` |

The XNU 8796 candidate is not asserted to be the exact source used for the donor's embedded `xnu-8796.142.1.703.8~1/RELEASE_ARM64_T8015` version string. The public tag query previously found `xnu-8796.141.3` but no public `xnu-8796.142.1` or `xnu-8796.142.1.703.8` tag. The version-stamp string is not itself a Git tag or a source-to-binary attestation. See [the version-stamp provenance note](xnu-kernel-version-stamp-provenance.md).

## The controls are separate

The central migration mistake to avoid is treating the following names as interchangeable “kernel protection” switches:

| Control | What the reviewed source associates it with | What it does not prove |
|---|---|---|
| `HAS_KTRR` / `KERNEL_INTEGRITY_KTRR` | KTRR-specific integrity mode and KTRR-specific privileged-register helper paths | CTRR support, secure-pmap runtime, or the full page-table layout |
| `HAS_CTRR` / `KERNEL_INTEGRITY_CTRR` | CTRR integrity mode, including CTRR-specific secondary-CPU cluster coordination in XNU 8796 | That T8010 has CTRR or that a T8010 build selects this path |
| `__ARM_KERNEL_PROTECT__` | ARM64 kernel-protection layout and exception-vector/page-table paths | A synonym for KTRR, CTRR, or `XNU_MONITOR` |
| `XNU_MONITOR` | Secure-pmap runtime configuration; XNU 8796 adds PPL segment bookkeeping and mapping paths under this guard | A synonym for the CPU's EL3 monitor state or a generic “KTRR enabled” flag |
| `NO_MONITOR` | H9/H13 header comment explicitly describes absence of an EL3 monitor | The opposite of `XNU_MONITOR`; the names refer to different layers |
| `PMAP_CS` / `PMAP_CS_ENABLE` | Separate board-configuration controls; the historical T8010 block sets them only inside a `DEVELOPMENT || DEBUG` conditional | A release-build value or proof of KTRR/CTRR selection |
| `__ARM_16K_PG__` | 16K-page source configuration | A complete physical memory map, page-table root layout, or matching protection policy |
| `__ARM_PAN_AVAILABLE__` | Generic PAN-related access-control paths | A complete board pmap or kernel-integrity configuration |

These are source-level distinctions. A macro definition in a public header does not prove that a product build selected it; a code path in the source does not prove that the path ran on hardware.

## 1. Historical H9 selects KTRR, not CTRR

The historical `H9.h` defines `HAS_KTRR` and does not define `HAS_CTRR`. It separately defines `__ARM_KERNEL_PROTECT__`, `__ARM_16K_PG__`, and `__ARM_PAN_AVAILABLE__`.

The common ARM64 feature header maps `HAS_CTRR` to `KERNEL_INTEGRITY_CTRR` first, then maps `HAS_KTRR` to `KERNEL_INTEGRITY_KTRR` when CTRR is not defined. This is a compile-time selection rule; it is not evidence that the same configuration was used in a later product build.

In XNU 8796, the source contains both integrity modes, but the guards are not uniform:

- The early `start.s` helper macros for selected writes to VBAR, TCR, TTBR1, and SCTLR use KTRR-specific `pinst_*` helper paths.
- Other startup sections use a combined KTRR-or-CTRR condition for early vector setup, exception-stack selection, and the bootstrap identity-map handling.
- `arm_vm_init.c` contains a KTRR-or-CTRR guarded identity-map replacement routine and integrity-dependent page-table allocation handling.
- `machine_routines_asm.s` has a KTRR-specific TTBR1 update helper path; it separately uses `__ARM_KERNEL_PROTECT__` for EL1 ASID handling.
- `cpu.c` has a CTRR-specific secondary-CPU path that coordinates the first CPU starting within a cluster before locking CTRR state.

The distinction matters: the presence of generic KTRR and CTRR branches in XNU 8796 does not make the modes interchangeable, and the CTRR cluster path is not a substitute for the historical H9 KTRR profile.

## 2. `__ARM_KERNEL_PROTECT__` is a separate layout contract

The XNU 8796 `arm_vm_init.c` source has a compile-time assertion under `__ARM_KERNEL_PROTECT__` requiring enough virtual-address space before the kernel to split the TTBR1-covered range and retain the exception-vector mapping. The same file uses this guard for EL0 mapping preparation and for selected page-table attributes, including not-global bits.

That is a layout and mapping contract, not merely another spelling of KTRR. The H9 header defines `__ARM_KERNEL_PROTECT__`; the reviewed H13 header does not. The 8796 tree still contains the guarded implementation, but that source presence alone does not say which product configuration enables it.

The 8796 `start.s` also uses `__ARM_KERNEL_PROTECT__` for exception-vector setup, independently of the KTRR-specific privileged-register helpers. The assembly source therefore reinforces that the integrity-mode and kernel-layout decisions must be tracked separately.

## 3. `XNU_MONITOR` and PPL are a further, distinct layer

The XNU 8796 `arm_vm_init.c` declares additional PPL text, trampoline, and data segment state under `XNU_MONITOR`. Its segment-protection setup applies page-granular ROX handling to executable segments and RWNX handling to data segments, with separate PPL segment handling when the monitor configuration is enabled. Later initialization also contains monitor-specific allocation and mapping paths.

The T8101/H13 board profile in the reviewed 8796 source selects `XNU_MONITOR`. The historical H9 header's `NO_MONITOR` comment means “No EL3 for this CPU”; it does not negate or define the separate XNU secure-pmap configuration. Do not translate `NO_MONITOR` into `XNU_MONITOR=0` without a documented build rule.

Likewise, the historical T8010 board block's `PMAP_CS=1` and `PMAP_CS_ENABLE=0` assignments appear only under `DEVELOPMENT || DEBUG`. Those lines do not establish the release configuration and must not be used as a proxy for KTRR, CTRR, or `XNU_MONITOR`.

## 4. Page size, PAN, and segment permissions are not a board memory map

H9 and H13 both declare `__ARM_16K_PG__` and `__ARM_PAN_AVAILABLE__`. That establishes shared source-level feature declarations in the compared headers. It does not establish that their physical address maps, kernel virtual-address layouts, page-table roots, or memory ownership rules are the same.

The XNU 8796 VM code includes page-granular ROX and RWNX segment handling. These generic permission-setting routines are not, by themselves, evidence that a target's KTRR/CTRR or PPL mechanism is correctly selected or operational. A valid T8010 mapping review would still need target-specific memory ranges, segment boundaries, page granule, kernel-protection configuration, and any secure-pmap/PPL contract.

## 5. Consequences for the H9 migration review

| Question | Static source result | Migration status |
|---|---|---|
| Can H13's CTRR profile replace H9's KTRR declaration? | No. The source maps them to different integrity modes and uses different guarded startup/CPU paths. | Critical unresolved |
| Can `__ARM_KERNEL_PROTECT__` be inferred from KTRR? | No. It has separate layout, exception-vector, and page-table consumers. | Critical unresolved |
| Can `NO_MONITOR` be treated as `XNU_MONITOR=0`? | No. H9's comment describes EL3; `XNU_MONITOR` selects the secure-pmap runtime layer in the newer source. | Critical unresolved |
| Does `PMAP_CS=1` in the old T8010 block prove release code-signing policy? | No. The assignment is inside a development/debug conditional and `PMAP_CS_ENABLE` is set to zero there. | Unresolved |
| Do matching 16K-page and PAN macros prove equivalent pmap behavior? | No. They are only two feature declarations among several independent mapping and security contracts. | High risk |
| Does the 20H392 donor's T8015 build string establish a T8010 integrity mode? | No. It identifies the donor kernel's reported build configuration, not the target's product flags or hardware state. | Critical unresolved |

The current evidence supports a **no-transplant** disposition: do not copy H9 or H13 security macros into XNU 8796 as a bundle, and do not enable a protection path based only on the CPU family name, a DeviceTree compatible string, or a donor build string.

## Remaining evidence needed

1. An authoritative Apple source/build record tying 20H392 to an exact XNU source revision and product configuration.
2. The actual target 19H422 and donor 20H392 kernel build selections for KTRR/CTRR, `__ARM_KERNEL_PROTECT__`, `XNU_MONITOR`, and related pmap settings. Public source headers do not provide those product flags.
3. Target-specific physical/virtual memory ranges, segment layout, page-table geometry, and ownership data sufficient to evaluate the `__ARM_KERNEL_PROTECT__` and integrity-mode contracts.
4. A target-specific explanation of the T8010 integrity and pmap mechanisms, including the relationship between the historical KTRR source profile and the 19H422 shipped artifact.
5. Authoritative T8010 CPU stepping/errata information before deciding whether historical H9 workarounds remain necessary.

Until those inputs exist, the protection/pmap migration remains a critical blocker. This note does not close M2, establish a build, or claim runtime protection behavior.

## Pinned source references

Historical XNU 7195:
- [H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [T8010 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/board_config.h)
- [ARM64 common feature mapping](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/apple_arm64_common.h)
- [ARM64 startup](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/start.s)
- [CPU startup](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/cpu.c)

XNU 8796:
- [H13.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)
- [T8101 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
- [ARM64 common feature mapping](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/apple_arm64_common.h)
- [CPU startup and CTRR cluster state](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c)
- [ARM64 startup](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/start.s)
- [VM and pmap initialization](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/arm_vm_init.c)
- [ARM64 machine assembly routines](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines_asm.s)
- [PMU implementation](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/monotonic_arm64.c)
- [PMU machine-routine registration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c)

Related Sweet-10 evidence:
- [H9/T8010 migration-risk classification](h9-t8010-migration-risk-classification.md)
- [Full-tree H9 source consumer audit](h9-source-fulltree-audit.md)
- [Interrupt and timer interface audit](interrupt-timer-interface-audit.md)
- [20H392 XNU version-stamp provenance](xnu-kernel-version-stamp-provenance.md)
- [XNU baseline lock](../xnu/BASELINE.lock.json)

This is source documentation only. It does not establish a T8010 product build, ABI compatibility, page-table state, hardware protection behavior, kernel boot, or SpringBoard.
