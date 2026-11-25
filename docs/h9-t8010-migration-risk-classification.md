# H9/T8010 migration-risk classification against XNU 8796

## Purpose and evidence boundary

This note turns the existing H9 macro inventory into a per-subsystem
migration-risk classification. It compares the historical public XNU
`xnu-7195.121.3` T8010/H9 configuration with the pinned public candidate
`xnu-8796.141.3`, and uses the latter's H13/T8101 profile only as a
contrast case.

The source comparison is static. It does not reconstruct Apple's private
20H392 build inputs, run the C preprocessor with Apple's product settings,
prove the selected code paths in the shipped kernel, or establish that
iPhone9,1 hardware behaves like any newer H13 platform. H13 is **not** a
replacement profile for H9. No target code or device state is changed.

## Executive classification

| Area | Direct source finding | Migration risk | Current disposition |
|---|---|---:|---|
| CPU startup and topology | H9's T8010 board block specifies 3 CPUs / 1 cluster; XNU 8796's T8101/H13 board block specifies 8 CPUs / 2 clusters. XNU 8796 has CTRR cluster-lock coordination in `cpu_start`; the historical Hurricane HID5 workaround is absent from the reviewed 8796 `start.s`. | Critical | **Unresolved platform contract.** Do not infer topology or startup behavior from either profile. |
| Kernel integrity and pmap | H9 selects KTRR through `HAS_KTRR`; H13 selects CTRR through `HAS_CTRR`. The common header maps them to different `KERNEL_INTEGRITY_*` modes. XNU 8796 contains distinct KTRR-only and KTRR-or-CTRR paths. | Critical | **Not interchangeable.** Needs target-specific security and page-table evidence plus exact build configuration. |
| PMU / AIC PMI | H9 explicitly sets `CPMU_AIC_PMI=1`; the shared PMU code then selects AIC interrupt generation and the machine-routine layer supplies the AIC PMI handler. H13 does not declare this macro in its reviewed profile header. | High | **Interrupt topology unresolved.** A counter count match is not enough to select the PMI route. |
| Page size and PAN | H9 and H13 both declare 16K pages and PAN. H9 declares `__ARM_KERNEL_PROTECT__`; H13's profile instead has other protection-related configuration, including secure-pmap settings in the T8101 board block. | High | **Partial shared capability only.** Page-size agreement does not supply pmap/security policy or memory layout. |
| Sleep / power / timebase | Both H9 and H13 declare `__ARM_GLOBAL_SLEEP_BIT__`; XNU 8796's generic sleep path remains, but H13 adds separate retention, continuous-clock, cluster and power-management feature declarations. The timebase implementation also changed between 7195 and 8796. | High | **Hardware semantics unresolved.** Do not import H13 power assumptions or XNU 8796 fallback clock values. |
| H9-specific exception / debug errata | The 7195 H9 profile selects `HAS_MIGSTS` exception reporting and a guarded `SINGLE_STEP_RETIRE_ERRATA` ISB. In 8796, the reviewed `sleh.c` lacks the `HAS_MIGSTS` branch, while both corresponding `pcb.c` debug-state routines retain an unconditional ISB after their MDSCR update branches. | High | **Mixed result.** The exception-reporting replacement remains unresolved; the single-step barrier is structurally retained with changed/broader placement, but its relationship to Radar 20619637 is unproven. |
| L2 PMU events | H9 declares `HAS_CPMU_L2C_EVENTS`; no direct consumer was found in the selected source set. | Unknown | **No conclusion.** Full conditional and product-build dependency closure remains open. |

## 1. CPU startup, CPU count, and cluster topology

Historical XNU 7195's T8010 board block includes H9.h and sets
`MAX_CPUS=3`, `MAX_CPU_CLUSTERS=1`, and `MAX_L2_CLINE=7`.
Its H9 profile selects `APPLEHURRICANE`. The reviewed XNU 8796 T8101
board block instead includes H13.h and sets `MAX_CPUS=8`,
`MAX_CPU_CLUSTERS=2`, `PMAP_CS=1`, `PMAP_CS_ENABLE=1`, and
`XNU_MONITOR=1`.

In XNU 8796 `cpu.c`, the CTRR build path maintains per-cluster lock state
during secondary CPU startup. That code is conditional on the CTRR integrity
configuration and indexes the state by the CPU's cluster ID. This is concrete
evidence that the newer profile's multi-cluster/CTRR startup contract includes
coordination that is not described by the old single-cluster H9 board block.

The historical H9-specific Hurricane HID5 snoop-reservation workaround in
7195 `start.s` is not present in the corresponding reviewed 8796 startup
file. The `APPLEHURRICANE` name still appears in selected generic/legacy
8796 source, but that does not reinstate the old T8010 machine profile.

**Classification:** CPU startup is a critical unresolved contract. The old
3-CPU/1-cluster constants are historical configuration evidence, not
validated values for a new 8796-based build. The H13 8-CPU/2-cluster model is
also not applicable evidence for T8010.

## 2. KTRR, CTRR, and page/pmap protection

The historical H9 header defines `HAS_KTRR`. Its common ARM64 header maps
that to `KERNEL_INTEGRITY_KTRR`. The XNU 8796 H13 header defines
`HAS_CTRR`, and the same common-header logic maps that to
`KERNEL_INTEGRITY_CTRR`. These are separate hardware integrity modes,
not two spellings of a generic “kernel protection enabled” switch.

The reviewed XNU 8796 source demonstrates why the distinction matters:

- `arm_vm_init.c` permits static read-only page-table allocation when
  either KTRR or CTRR integrity mode is selected.
- `start.s` has KTRR-specific privileged-instruction helper paths for
  selected system-register writes, while its early vector setup recognizes
  both KTRR and CTRR as integrity modes.
- `machine_routines_asm.s` has KTRR-specific paths for selected translation
  table operations, but uses a KTRR-or-CTRR condition for the protected
  exception-stack selection path.
- `cpu.c` has CTRR-specific cluster state and secondary-CPU coordination.

This is intentionally not summarized as “CTRR is KTRR with a different
macro”: the source uses different guards and different supporting mechanisms.
A source tree that contains both code paths does not prove that an iPhoneOS
product build selects either one for a given board.

The page-size flags also need separation from integrity mode. Both H9 and H13
declare `__ARM_16K_PG__`, but H9 declares `__ARM_KERNEL_PROTECT__` while
H13's reviewed header does not. The newer T8101 board block separately
enables secure-pmap configuration through `XNU_MONITOR` and PMAP settings.
Also, H9's `NO_MONITOR` means “no EL3 monitor”; it is not the same setting
as `XNU_MONITOR`.

**Classification:** critical security/pmap blocker. A macro substitution or
copy of the old H9 board block would not establish the right protection
mechanism, privileged-register access model, pmap policy, or page-table
layout for T8010.

## 3. PMU counter interrupts and AIC coupling

H9 explicitly sets `CORE_NCTRS=10` and `CPMU_AIC_PMI=1`. The H13 header
also sets `CORE_NCTRS=10`, but it does not declare
`CPMU_AIC_PMI` in the reviewed header. H13's PMU declarations include
additional capabilities (including uncore/UPMU features), so the matching
core-counter count must not be mistaken for matching PMU hardware semantics.

In both reviewed 7195 and 8796 `monotonic_arm64.c`, the
`CPMU_AIC_PMI` conditional selects AIC as the PMU interrupt generator when
true and FIQ when false. The corresponding `machine_routines.c` conditional
registers `mt_cpmu_aic_pmi` as the PMI handler only when the flag and
MONOTONIC are enabled. The header `monotonic.h` also derives
`MONOTONIC_FIQ` when MONOTONIC is enabled and `CPMU_AIC_PMI` is false.

In the reviewed H13 header and 8796 board configuration, no explicit
`CPMU_AIC_PMI` definition was found. Unless an external product/build
definition supplies it, the source-level false branch selects FIQ, not AIC.
This is a statement about the reviewed public source inputs; the exact
Apple product build flags are not available here.

**Classification:** high-risk interrupt-coupling blocker. The historical H9
AIC-PMI setting affects both the PMU's interrupt-generation mode and handler
registration. It cannot be enabled merely because the target DeviceTree has
an AIC-related node or because H13 has ten core counters. Target interrupt
routing and the actual PMU event/interrupt contract remain unknown.

The H9 `HAS_CPMU_L2C_EVENTS` declaration remains unresolved: no direct
consumer was located in the selected audit set. This note does not classify
it as unused or supported.

## 4. Sleep, power, and timebase behavior

Both H9 and H13 declare `__ARM_GLOBAL_SLEEP_BIT__`. The XNU 8796
`cpu.c` and `machine_routines_asm.s` still contain the corresponding
generic sleep coordination paths, including `arm64_stall_sleep` and
deep-sleep control. That shared macro therefore identifies a common source
capability, not a complete matching power implementation.

H13 declares additional features that are not in the H9 header, including
continuous hardware clock, architectural retention state, cluster support,
and several power/retention features. Those declarations describe a
different CPU generation and cannot be treated as A10 capabilities.

The separate interrupt/timer audit records a meaningful implementation
change: XNU 7195 reads `CNTVCT_EL0` with an ISB and adds the per-CPU timebase
base; XNU 8796 uses a nonspeculative counter-selection helper and retries
the combined clock/base read across a sleep/wake race. The H13 header declares
`HAS_ACNTVCT`; H9 does not. XNU 8796 fallback clock frequencies are source
defaults, not measured iPhone9,1 values.

**Classification:** high-risk power/timekeeping blocker. The global sleep
flag alone does not establish sleep entry/exit register semantics, timer
continuity, wake-state restoration, or the correct timebase source/frequency
for T8010.

## 5. Exception reporting and CPU errata

The 7195 H9 header defines `HAS_MIGSTS`; the historical `sleh.c` uses it
to select a special exception/error-reporting path involving migration and
LLC/MMU status registers. The corresponding reviewed 8796 `sleh.c` does
not contain that branch.

The 7195 H9 header also defines `SINGLE_STEP_RETIRE_ERRATA` and
comments that Hurricane and Zephyr require the workaround for Radar
20619637. In the reviewed 7195 `pcb.c`, both `arm_debug_set32()` and
`arm_debug_set64()` execute an ISB under that macro in the `else` branch
after clearing the MDSCR single-step bit.

The corresponding 8796 `pcb.c` routines no longer contain the macro
conditional, but both execute an unconditional ISB after the full
MDSCR-update if/else branch and before restoring interrupts. Thus the
instruction barrier is not absent from the newer source: its placement is
broader at these two call sites. The available source does not attribute
the newer unconditional barrier to Radar 20619637 or establish that it
covers the same hardware erratum on T8010.

See the [pinned single-step erratum source comparison](h9-single-step-erratum-followup.md)
for commit/blob identities and line-level evidence.

**Classification:** high-risk unresolved errata relationship. Record the
barrier as structurally retained with changed placement, not simply
removed. The affected CPU stepping, erratum conditions, and intent of the
newer barrier require authoritative platform/build evidence.

## Migration disposition

The source review supports these dispositions, not an implementation recipe:

1. **Do not copy H9.h or re-enable the T8010 machine selector** in XNU 8796.
   The historical header depends on old CPU-family, integrity, PMU, startup,
   and errata assumptions.
2. **Do not substitute H13.h.** It selects a different CPU generation,
   CTRR, a multi-cluster topology, and additional PMU/power features.
3. **Keep K2 open.** The source inventory and this manual classification
   identify high-risk interfaces, but do not yet provide a complete
   preprocessor-resolved dependency graph or product-specific build flags.
4. **Keep K4 open.** Authoritative iPhone9,1 CPU, interrupt, PMU, security,
   memory, and power contracts are still missing or incomplete.
5. **Keep K1 open.** The 20H392 version string and public XNU candidate do
   not identify Apple's exact source commit or private build inputs.

## Pinned source references

Historical XNU 7195:
- [H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [T8010 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/board_config.h)
- [ARM64 common feature mapping](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/apple_arm64_common.h)
- [ARM64 startup](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/start.s)
- [PMU implementation](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/monotonic_arm64.c)
- [PMU machine-routine registration](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines.c)
- [Single-step handling](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/pcb.c)
- [Exception handling](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/sleh.c)

XNU 8796:
- [H13.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)
- [T8101 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
- [ARM64 common feature mapping](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/apple_arm64_common.h)
- [CPU startup and CTRR cluster state](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c)
- [ARM64 startup](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/start.s)
- [VM/pmap initialization](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/arm_vm_init.c)
- [ARM64 machine assembly routines](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines_asm.s)
- [PMU implementation](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/monotonic_arm64.c)
- [PMU machine-routine registration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c)
- [Exception handling](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/sleh.c)
- [Single-step handling](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/pcb.c)

Related Sweet-10 evidence:
- [Existing H9 feature-macro consumer audit](h9-feature-macro-consumer-audit.md)
- [H9 single-step retirement erratum source comparison](h9-single-step-erratum-followup.md)
- [ARM64 interrupt and timer interface audit](interrupt-timer-interface-audit.md)
- [T8010 public-source transition](t8010-public-source-transition.md)
- [20H392 XNU version-stamp provenance](xnu-kernel-version-stamp-provenance.md)

No device operation, firmware modification, kernel build, or boot procedure
was performed. The physical iPhone 7 remains on iOS 12.1.4; SpringBoard has
not been reached.
