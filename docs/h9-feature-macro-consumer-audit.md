# Historical H9 feature-macro consumer audit

## Scope and method

This is a bounded, read-only source comparison between Apple's public XNU
`xnu-7195.121.3` tree (which contains the historical T8010/H9 profile) and
the selected `xnu-8796.141.3` tree.

The review starts with every feature macro declared in the historical
`pexpert/pexpert/arm64/H9.h`, then checks its direct uses in corresponding
ARM64, ARM, VM, exception, PMU, and platform-expert source files. It is not a
full build, an exhaustive preprocessing/dependency graph, or a proof that a
missing macro has no consumer anywhere in every XNU component.

Pinned source references:
- [XNU 7195.121.3 H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [XNU 7195.121.3 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 H13.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)

## Macro-by-macro findings

| H9 macro | Historical definition / reviewed consumers in XNU 7195 | XNU 8796 comparison | Bounded interpretation |
|---|---|---|---|
| `APPLEHURRICANE` | Defined as the CPU-family selector. Seen in `sleh.c`, `monotonic_arm64.c`, and `start.s`; the startup file applies a Hurricane-specific HID5 snoop-reservation workaround. | The selector remains in `sleh.c`, `proc_reg.h`, and `monotonic_arm64.c`, but the matching `start.s` no longer has the old HID5 block. H13 declares `APPLEFIRESTORM`, not `APPLEHURRICANE`. | Some generic/legacy Hurricane conditionals remain in the newer tree; they do not establish a selected T8010 board profile. |
| `NO_MONITOR` | Defined as 1 with H9 comment “No EL3 for this CPU -- ever”. Used by old ARM64 `kpc.c` and `cpu.c` paths. | `cpu.c` retains a `NO_MONITOR` check. H13 also defines `NO_MONITOR` with the same EL3-specific meaning. The old `osfmk/arm64/kpc.c` path is absent at the same path in 8796. | This macro means no EL3 monitor; it must not be confused with the distinct `XNU_MONITOR` secure-pmap configuration used in newer board profiles. |
| `HAS_MIGSTS` | Defined as 1. In old `sleh.c`, selects a special exception/error-reporting branch that reads `MIGSTS_EL1` and related LLC/MMU error registers. | The matching 8796 `sleh.c` does not contain the `HAS_MIGSTS` branch. | The old reporting path is not present in the reviewed newer exception file. This does not prove the hardware feature is absent or that no replacement exists elsewhere. |
| `HAS_KTRR` | Defined as 1. The old `apple_arm64_common.h` maps it to `KERNEL_INTEGRITY_KTRR`. | The newer common header still understands `HAS_KTRR`, but H13 defines `HAS_CTRR`; the common header maps that to `KERNEL_INTEGRITY_CTRR`. Generic startup code contains KTRR and CTRR branches. | The integrity framework has multiple hardware modes. H9's KTRR declaration cannot be replaced by H13's CTRR declaration or treated as equivalent hardware evidence. |
| `HAS_CPMU_L2C_EVENTS` | Defined as 1 in H9. No direct consumer was located in the selected set of reviewed ARM64/PMU files. | No direct consumer or corresponding H13 declaration was identified in the selected files. | Unresolved. Do not infer that the flag is unused throughout the complete source tree. |
| `CORE_NCTRS` | Defined as 10. Used by `machine_kpc.h` and `monotonic_arm64.c` to size/configure core performance counters. | Both consumer paths remain. H13 also declares `CORE_NCTRS=10`. | The generic counter-count interface remains, and the same count appears in H13; that alone does not prove matching T8010 PMU event semantics or interrupt wiring. |
| `CPMU_AIC_PMI` | Defined as 1. Conditional logic appears in `monotonic.h`, `monotonic_arm64.c`, and `machine_routines.c` for PMU interrupt handling. | Those conditionals remain in 8796. H13 does not declare `CPMU_AIC_PMI` in the reviewed header. | The code retains a configurable path, but the newer H13 profile does not provide the H9 setting. The correct T8010 setting cannot be inferred from H13. |
| `__ARM_16K_PG__` | Defined as 1. Used in `proc_reg.h`, `tlb.h`, VM compressor/kernel VM code, and pmap data handling. | Those generic page-size branches remain. H13 also defines `__ARM_16K_PG__`. | The 16K-page compile-time capability remains represented in modern ARM64 source; this is not a complete memory-layout or board mapping. |
| `__ARM_KERNEL_PROTECT__` | Defined as 1. Used across `proc_reg.h`, `tlb.h`, `start.s`, `cpu.c`, `arm_vm_init.c`, pmap, task, and machine-routine code. | Many guarded source paths remain in 8796, but H13 does not declare this macro in the reviewed header. | A generic optional implementation path remains in source; this audit does not establish that the iPhoneOS build selects it or that it is appropriate for T8010. |
| `__ARM_GLOBAL_SLEEP_BIT__` | Defined as 1. Used by `cpu.c`, `machine_routines_asm.s`, and `arm_init.c` to coordinate the global sleep mechanism. | Matching consumers remain, and H13 also defines the macro. | A shared ARM64 capability exists in the modern tree; its presence in H13 does not independently validate A10-specific power behavior. |
| `__ARM_PAN_AVAILABLE__` | Defined as 1. Used in `copyio.c`, `pcb.c`, `sleh.c`, and platform tests. | Matching consumers remain, and H13 also defines the macro. | The generic PAN path remains available in the newer source; target-specific CPU support still needs its own evidence. |
| `SINGLE_STEP_RETIRE_ERRATA` | Defined as 1. In XNU 7195 `pcb.c`, both `arm_debug_set32()` and `arm_debug_set64()` execute an ISB in the `else` branch after clearing the MDSCR SS bit. | XNU 8796 removes the macro guard, but both corresponding functions execute an unconditional ISB after the full if/else branch and before restoring interrupts. | The barrier remains with broader source-level branch coverage; whether this intentionally replaces the named Hurricane/Zephyr erratum workaround is unresolved. |

## Single-step erratum follow-up

The `SINGLE_STEP_RETIRE_ERRATA` row is refined by the [pinned 7195-to-8796 source comparison](h9-single-step-erratum-followup.md). The newer source does not retain the macro, but it does retain an unconditional ISB after each corresponding MDSCR update branch. This is structural evidence only; it does not establish the newer barrier's intent or the erratum's silicon status.

## Important distinctions

### CPU-family labels can outlive a board profile

The retained `APPLEHURRICANE` checks are examples of why a text search for
“T8010” or “Hurricane” is not enough to establish support. Some CPU-name,
register, or PMU branches can remain in shared source after the corresponding
machine configuration has disappeared. In XNU 8796, the reviewed ARM64
`board_config.h` selects T6000, T8101, T8103, BCM2837, and VMAPPLE profiles;
it has no T8010/H9 profile.

### NO_MONITOR is not XNU_MONITOR

H9 and H13 comment that `NO_MONITOR` means the CPU has no EL3 monitor. The
newer XNU board configuration separately sets `XNU_MONITOR` for certain
platform profiles. These names refer to different mechanisms and must not be
collapsed into a single “monitor enabled/disabled” fact.

### Shared generic code is not a complete SoC implementation

Several H9 feature names are also used by modern generic ARM64 source. That
does not restore the absent H9 header, T8010 build selector, CPU-specific
errata workarounds, PMU wiring, board configuration, device tree, memory map,
or platform services. Conversely, a macro not found in a corresponding file
does not prove the hardware capability is unsupported; the implementation may
have moved or been replaced.

## Decision

The H9 header is not a self-contained porting unit. The consumer map shows a
mixture of:
- shared generic feature paths that remain in XNU 8796;
- H9-specific paths that are absent or changed in the corresponding newer file;
- modern profiles that select different hardware integrity or platform features;
- unresolved flags whose complete consumer set has not been established.

Do not copy H9.h into XNU 8796, enable the old T8010 machine selector, or
substitute H13 feature declarations for H9 values. The evidence needed for a
real port remains a full source dependency review plus authoritative
iPhone9,1-specific platform, device-tree, memory, interrupt, PMU, and handoff
information.

## Source files reviewed

Historical XNU 7195:
- [H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [apple_arm64_common.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/apple_arm64_common.h)
- [sleh.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/sleh.c)
- [proc_reg.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/proc_reg.h)
- [monotonic_arm64.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/monotonic_arm64.c)
- [kpc.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/kpc.c)
- [cpu.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/cpu.c)
- [machine_kpc.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_kpc.h)
- [monotonic.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/monotonic.h)
- [machine_routines.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines.c)
- [tlb.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/tlb.h)
- [start.s](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/start.s)
- [pcb.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/pcb.c)
- [arm_vm_init.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/arm_vm_init.c)
- [copyio.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/copyio.c)
- [machine_routines_asm.s](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines_asm.s)
- [arm_init.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm/arm_init.c)

Selected XNU 8796:
- [H13.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)
- [apple_arm64_common.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/apple_arm64_common.h)
- [board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
- [sleh.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/sleh.c)
- [proc_reg.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/proc_reg.h)
- [monotonic_arm64.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/monotonic_arm64.c)
- [cpu.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c)
- [machine_kpc.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_kpc.h)
- [monotonic.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/monotonic.h)
- [machine_routines.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c)
- [perfmon_arm64.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/perfmon_arm64.c)
- [tlb.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/tlb.h)
- [start.s](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/start.s)
- [pcb.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/pcb.c)
- [arm_vm_init.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/arm_vm_init.c)
- [copyio.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/copyio.c)
- [machine_routines_asm.s](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines_asm.s)
- [arm_init.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm/arm_init.c)

No kernel implementation, device operation, firmware modification, or boot
procedure is included.
