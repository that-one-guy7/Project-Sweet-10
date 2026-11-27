# H9/T8010 CPMU-to-AIC PMI delivery contract (source-level)

## Scope and evidence boundary

This note traces the public XNU source contract behind the historical H9
setting `CPMU_AIC_PMI=1`, then compares it with static AIC evidence from the
iPhone 7 / D10AP / 19H422 target-reference artifacts and iPhone X / D22AP /
20H392 donor-reference metadata.

This is read-only source and metadata research. It does not describe
register writes, interrupt enabling, kernel loading, boot-chain changes,
device operations, or firmware changes. The physical iPhone 7 remains on
iOS 12.1.4. The 19H422 files are reference artifacts, not firmware installed
on that phone.

The important distinction is that a DeviceTree compatible-string match, a
KEXT bundle record, a public XNU callback, a PrebuiltLoader record, and a
runtime interrupt delivery are different evidence classes. This note only
establishes the first three where explicitly stated; it does not establish
runtime delivery.

## 1. Target and donor AIC evidence

The hash-verified 19H422 target DeviceTree component has SHA-256
`906a2708d3d15828c447ee1d7211f628dfeec7653a343384f3845153178c5906`.
The decompressed raw DeviceTree used by the parser has SHA-256
`39331154d60f05923da0b2c5dc9ac6395da6a8276f0952e997dbdcfa81c2420e`.

Its `/arm-io/aic` node reports:

- `compatible = aic,1`
- `device_type = interrupt-controller`
- `interrupt-controller = master`
- `aic-version = 2`
- `#main-cpus = 2`

These are static properties of the extracted 19H422 component. They do not
prove the final runtime DeviceTree, the number of CPUs that become online, or
the controller's actual interrupt-routing behavior.

The 19H422 target KernelCache metadata contains
`com.apple.driver.AppleInterruptController`, version `1.0.0d1`, with
a serialized personality whose `IOClass` is
`AppleInterruptController`, `IONameMatch` is `aic,1`, and
`IOProviderClass` is `AppleARMIODevice`. This is an exact static
match-property overlap with the target DeviceTree node.

The 20H392 donor KEXT metadata export also contains the same top-level
`com.apple.driver.AppleInterruptController` bundle ID. The selected
personality fields compared in the existing inventory did not print a
difference, but the donor export omits its displayed version field and
serializes several dependency version values as empty strings. Those empty
values are not treated as missing dependencies or binary equivalence.

Artifact identities remain separate:

| Reference | Device | Kernel identity | KernelCache SHA-256 |
|---|---|---|---|
| Target 19H422 | iPhone9,1 / D10AP / T8010 | XNU 8020.241.44~1 / RELEASE_ARM64_T8010 | `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee` |
| Donor 20H392 | iPhone10,3 / D22AP / T8015 | XNU 8796.142.1.703.8~1 / RELEASE_ARM64_T8015 | `2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221` |

The shared AIC bundle ID is metadata evidence only. It does not establish
that the two executable implementations are identical, that their private
KPI contracts match, or that either service attaches successfully.

See the [parsed target DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md),
[19H422 AIC KEXT inventory](iphone91-19h422-aic-kext-inventory.md), and
[19H422/20H392 AIC and T8010 metadata comparison](20h392-19h422-aic-t8010-kext-comparison-results.md).

## 2. Historical H9 selection

The public XNU `xnu-7195.121.3` H9 header declares:

- `CORE_NCTRS = 10`
- `CPMU_AIC_PMI = 1`
- `HAS_CPMU_L2C_EVENTS = 1)

The same header declares KTRR, PAN, 16K pages, and the global sleep bit;
those separate features are not the subject of this note.

The important point is that `CPMU_AIC_PMI` is not merely a label for the
existence of an AIC. It changes how the generic CPMU code selects its
interrupt generator and which handler is returned to the processor
registration layer.

Pinned source: [XNU 7195 H9.h, lines 34–48](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h#L34-L48).

## 3. What the CPMU_AIC_PMI conditional changes

In both reviewed XNU snapshots, `monotonic_arm64.c` defines the PMCR0
interrupt-generator field as AIC when `CPMU_AIC_PMI` is true and FIQ when it
is false. The enum values in that source are `PMCR0_INTGEN_AIC = 2` and
`PMCR0_INTGEN_FIQ = 4`; `PMCR0_INIT` incorporates the selected generator.

The same source has a separate `mt_cpmu_aic_pmi` callback. It obtains the
current CPU data, checks that the callback's source object equals that
CPU's stored `interrupt_nub`, panics if the identities differ, and then
calls `mt_cpu_pmi` using the current `PMCR0_EL1` value.

The FIQ callback has a corresponding split: when `CPMU_AIC_PMI` is true,
`mt_fiq` does not handle the core PMI through `mt_cpu_pmi`. A separate
uncore-FIQ path is guarded by `HAS_UNCORE_CTRS`. H9.h's
`HAS_CPMU_L2C_EVENTS` declaration is not the same macro as
`HAS_UNCORE_CTRS`; do not infer uncore-counter support from the L2-event
flag.

The header `monotonic.h` also defines `MONOTONIC_FIQ` only when
`MONOTONIC && !CPMU_AIC_PMI`. Thus the H9 setting changes both the PMCR0
interrupt-generator choice and the generic FIQ-side core-PMI handling.

Pinned source references:

- [XNU 7195 monotonic_arm64.c: PMCR0 generator selection](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/monotonic_arm64.c#L126-L140)
- [XNU 7195 monotonic_arm64.c: AIC PMI callback and FIQ split](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/monotonic_arm64.c#L1301-L1323)
- [XNU 7195 monotonic.h: MONOTONIC_FIQ condition](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/monotonic.h#L38-L45)

## 4. Per-CPU handler registration and identity contract

The public XNU source exposes two related but distinct pieces of glue:

1. `ml_processor_register` returns `mt_cpmu_aic_pmi` through
   `pmi_handler_out` only when both `CPMU_AIC_PMI` and `MONOTONIC` are
   enabled; otherwise it returns `NULL`.
2. `ml_install_interrupt_handler` stores a per-CPU tuple containing
   `interrupt_nub`, `interrupt_source`, `interrupt_target`,
   `interrupt_handler`, and `interrupt_refCon`, while interrupts are
   disabled, then restores the previous interrupt state.

The generic ARM64 `sleh_irq` path invokes the stored interrupt-handler tuple
when `USE_APPLEARMSMP` is false; the alternate branch calls
`PE_handle_ext_interrupt()`. This generic IRQ-dispatch path is not itself
proof of how the separate `pmi_handler_out` callback is wired by a private
platform driver. The exact AppleInterruptController/IOCPU callback binding
is not present in the reviewed public XNU source.

The useful static contract is narrower: the CPMU AIC callback expects its
source identity to match the current CPU's `interrupt_nub`, and the generic
XNU layer has a per-CPU slot for that nub. A correct platform integration
must satisfy that identity contract, but the public source does not show
whether the target's private KEXT does so.

Pinned source references:

- [XNU 7195 machine_routines.c: ml_install_interrupt_handler](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines.c#L810-L840)
- [XNU 7195 machine_routines.c: pmi_handler_out selection](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines.c#L1398-L1404)
- [XNU 7195 cpu_data_internal.h: per-CPU interrupt fields](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm/cpu_data_internal.h#L198-L209)
- [XNU 7195 sleh.c: generic IRQ dispatch](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/sleh.c#L1749-L1777)

## 5. What changed between XNU 7195 and the public 8796 candidate

The following source bodies/control blocks were compared directly at the
pinned tags:

| Item | XNU 7195.121.3 | XNU 8796.141.3 | Comparison |
|---|---|---|---|
| `mt_cpmu_aic_pmi` callback body | `monotonic_arm64.c`, blob `06d845f8f3332d2dec334560c06000fb3863f630` | `monotonic_arm64.c`, blob `4bb4aab1f8d454733d06fd51095cdac8b609a88d` | Extracted function body identical |
| `mt_fiq` core-PMI conditional | Same 7195 `monotonic_arm64.c` blob | Same 8796 `monotonic_arm64.c` blob | Extracted conditional identical |
| `ml_install_interrupt_handler` body | `machine_routines.c`, blob `a5c193df37ad815c715c2b8f8f6c09fbf1a5234d` | `machine_routines.c`, blob `76582da51776aa162df5e6476fb973d31997729b` | Extracted function body identical |
| `pmi_handler_out` conditional | Same 7195 `machine_routines.c` blob | Same 8796 `machine_routines.c` blob | Extracted conditional identical |
| `sleh_irq` generic dispatch block | `sleh.c`, blob `0db56a160a8cdf9683dbc501c58b06e2a9b5bc9d` | `sleh.c`, blob `c40c6eac40fd39f4490b39f5d3c7e6083aa472a6` | Dispatch block retained; assertion helper differs |

This is a source-level comparison of selected function bodies, not a
preprocessor/build result. The public XNU 8796.141.3 H13 header does not
declare `CPMU_AIC_PMI`; the public 8796 board configuration also does not
provide the historical H9/T8010 machine profile. The donor KernelCache's
embedded XNU version stamp is `8796.142.1.703.8~1`, not the public
`xnu-8796.141.3` tag. Therefore, retained generic source code does not
establish that the donor product build or any hypothetical T8010 build
selects the AIC PMI branch.

The selected 8796 source references are:

- [XNU 8796 monotonic_arm64.c: PMCR0 generator selection](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/monotonic_arm64.c#L138-L144)
- [XNU 8796 monotonic_arm64.c: AIC PMI callback and FIQ split](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/monotonic_arm64.c#L1400-L1422)
- [XNU 8796 machine_routines.c: ml_install_interrupt_handler](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c#L806-L825)
- [XNU 8796 machine_routines.c: pmi_handler_out selection](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c#L1452-L1458)
- [XNU 8796 sleh.c: generic IRQ dispatch](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/sleh.c#L1850-L1878)
- [XNU 8796 H13.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)

## 6. Migration classification and unresolved evidence

**Classification: high-risk platform-integration blocker.** The historical
H9 setting requires more than an AIC-compatible DeviceTree node or the
presence of an `AppleInterruptController` bundle. The source-level path
depends on the selected CPMU interrupt-generator mode, a non-null
per-processor PMI callback, a source-object identity match against the
per-CPU interrupt nub, and a private controller/CPU integration that is not
available in the public XNU tree.

Still unknown:

- Whether the target's private AppleInterruptController registers the
  expected per-CPU nub and delivers the CPMU callback with that same object.
- The actual AIC PMI vector/source identity, IRQ routing, trigger mode,
  affinity, acknowledgement, and EOI behavior on D10AP.
- Whether `MONOTONIC` and `CPMU_AIC_PMI` were selected together in the
  exact Apple product build.
- Whether `HAS_UNCORE_CTRS` is defined by any product-specific input for
  the target; the H9 header's L2-event flag is not sufficient evidence.
- Whether the private ApplePMGR, AppleInterruptController, and IOCPU
  implementations satisfy the selected XNU 8796 KPI/callback contract.
- The exact Apple XNU source commit and product build inputs behind the
  20H392 donor KernelCache.

Do not enable or transplant `CPMU_AIC_PMI` based on the metadata match.
Do not infer that AICv2 WFE handling, the PMU interrupt route, and the AIC
timer/decrementer path are one interchangeable mechanism. They are separate
contracts that require separate evidence.

No runtime interrupt delivery, PMU counting, AIC attachment, CPU topology,
sleep/wake behavior, ABI compatibility, build success, or device boot is
claimed. The iPhone 7 remains on iOS 12.1.4.
