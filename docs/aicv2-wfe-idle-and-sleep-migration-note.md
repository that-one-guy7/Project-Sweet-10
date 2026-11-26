# AICv2-aware WFE, idle, and sleep migration note

## Scope and conclusion

This is a read-only comparison of the public XNU `xnu-7195.121.3` H9/T8010-era source and the public XNU `xnu-8796.141.3` candidate. It correlates those sources with the already hash-verified iPhone9,1 / D10AP / 19H422 DeviceTree inventory.

Version boundary: the target 19H422 KernelCache reports XNU `8020.241.44~1` / `RELEASE_ARM64_T8010`, while the 20H392 donor KernelCache reports `8796.142.1.703.8~1` / `RELEASE_ARM64_T8015`. Therefore XNU 7195 is a historical H9 profile reference and XNU 8796.141.3 is a nearby public candidate, **not** either exact shipped kernel source/build. This comparison cannot establish Apple's private 20H392 source revision or product build flags.

**New finding:** XNU 8796 adds an AICv2-aware interrupt-delivery safeguard to the generic WFE/idle path. Its source comment explains that an interrupt masked during WFE can be ignored as an event; with AICv2 distribution, a transient masked interval can cause an SIQ query rejection and reroute the interrupt toward another core or cluster that may be power-gated. The newer code can temporarily unmask IRQ/FIQ, track software interrupt counters, and re-mask before returning.

The target 19H422 static DeviceTree independently reports `aic-version = 2` and `#main-cpus = 2`. That makes the newer source path relevant to investigate, but **does not prove** that the iPhone 7's private AIC driver, XNU 8796's product configuration, or the runtime interrupt topology uses this exact path.

The H9 `CPMU_AIC_PMI=1` setting is a separate contract: it selects the core performance monitor's AIC PMI generation mode and registers a PMI callback. It must not be conflated with the generic AICv2 IRQ/FIQ distribution issue in WFE.

No implementation, build, hardware operation, or device change is part of this note. The physical iPhone 7 remains on iOS 12.1.4.

## 1. Target-side evidence boundary

The target DeviceTree source artifact is the iPhone 7 Global iOS 15.8.8 (19H422) `DeviceTree.d10ap.im4p` component, decompressed to `DeviceTree.d10ap.raw`:

| Property | Recorded value |
|---|---|
| Raw length | 160,572 bytes |
| Raw SHA-256 | `39331154d60f05923da0b2c5dc9ac6395da6a8276f0952e997dbdcfa81c2420e` |
| Parsed nodes | 227, including root |
| Parse result | Complete; 160,572 bytes consumed; no trailing bytes |
| Target identity | `D10AP` / `iPhone9,1` / `arm-io,t8010` |

The static `/arm-io/aic` node reports:

- `compatible = aic,1`
- `device_type = interrupt-controller`
- `interrupt-controller = master`
- `#interrupt-cells = 1`
- `#main-cpus = 2`
- `aic-version = 2`
- `#shared-timestamps = 16`

Its two register tuples are `0x0e100000 / 0x8000` and `0x0e108000 / 0x1000`, relative to the ARM-IO range. The separate `/arm-io/aic-timebase` node uses the latter window.

The same static tree contains two CPU nodes (`cpu0` running and `cpu1` waiting). This does not establish the final runtime CPU count, cluster topology, IRQ routing, or power state.

The target 19H422 KernelCache KEXT metadata separately records `com.apple.driver.AppleInterruptController` version `1.0.0d1`, with a personality matching `aic,1` through `AppleARMIODevice`. This is a serialized personality/provider declaration, not proof that the service attaches or that its private implementation follows the public XNU 8796 WFE assumptions. See the [target AIC inventory](iphone91-19h422-aic-kext-inventory.md) and [public AIC source-availability audit](aic-controller-source-availability-audit.md).

Primary artifact report: [19H422 parsed DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md#scope-and-provenance).

## 2. Historical XNU 7195 idle/WFE path

In XNU 7195:

- `machine_idle()` asserts the IRQ mask, calls `Idle_context()`, then clears IRQ/FIQ masks. It does not contain the later `wfe_process_recommendation()` wrapper around the context transition.
- `cpu.c`'s `wfe_to_deadline_or_interrupt()` repeatedly checks `cpu_interrupt_is_pending()` and issues WFE while no interrupt is pending. Its signature has no `unmask` parameter, and this routine does not perform the later software IRQ-counter snapshot/recheck sequence.
- The proximate-I/O WFE recommendation is handled in `cpu_idle()`, after the idle context has been loaded.

Pinned source references:

- [XNU 7195 machine_idle(), machine_routines.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines.c#L283-L291)
- [XNU 7195 WFE loop, cpu.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/cpu.c#L358-L390)
- [XNU 7195 H9 feature declarations](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h#L32-L48)

This is a source-structure comparison only. It does not prove how Apple's 19H422 product build configured or exercised this code.

## 3. XNU 8796 AICv2-aware WFE path

XNU 8796 changes both the helper and its caller:

1. `cpu_interrupt_is_pending()` reads `ISR_EL1`.
2. `wfe_to_deadline_or_interrupt()` accepts an `unmask` argument.
3. When `unmask` is true, the routine snapshots `cpu_stat.irq_ex_cnt_wake`, clears the DAIF IRQ/FIQ mask bits, and enters the WFE/pending-interrupt loop.
4. After the loop, it re-masks IRQ/FIQ and reloads the software interrupt counter. Its return value treats either a hardware-pending interrupt or a changed software counter as a reason to leave the WFE recommendation path.
5. `machine_routines.c`'s `wfe_process_recommendation()` calls the helper with `unmask = true` when the global unmasked-WFE setting is enabled and the performance controller provides a nonzero cluster WFE timeout. `machine_idle()` invokes this recommendation handler before falling back to `Idle_context()`.

The default declaration of `idle_proximate_io_wfe_unmasked` in `cpu.c` is 1. The actual WFE recommendation still depends on a nonzero timeout being supplied; the source does not establish that a particular target runtime will supply one.

The rationale is unusually relevant to the target metadata: the XNU 8796 source explicitly discusses AICv2 interrupt distribution, while the target's 19H422 static DeviceTree says `aic-version = 2`. The code comment describes a possible interrupt-routing failure when an interrupt is masked across WFE and another destination core/cluster is power-gated.

Pinned source references:

- [XNU 8796 interrupt-pending helper and AICv2 WFE rationale](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c#L363-L368)
- [XNU 8796 unmask/counter logic](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c#L392-L477)
- [XNU 8796 masked proximate-I/O WFE alternative](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c#L501-L539)
- [XNU 8796 recommendation handler and machine_idle() caller](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c#L302-L361)

### Interpretation

This is a concrete source-level difference between the historical H9-era tree and the newer candidate. It identifies an interrupt-delivery/idle contract that deserves explicit migration review alongside the existing PMU/AIC analysis.

It does **not** prove that the target's AIC implementation has the same SIQ behavior, that the target has multiple clusters, that a nonzero WFE recommendation is produced, or that the 20H392 donor's private build selects this code. The target DeviceTree's `#main-cpus = 2` and two static CPU nodes are not runtime topology evidence.

## 4. Keep core PMU PMI routing separate

The historical H9 header declares `CPMU_AIC_PMI=1`. In both reviewed XNU source generations:

- `monotonic_arm64.c` selects `PMCR0_INTGEN_AIC` when `CPMU_AIC_PMI` is true, and selects `PMCR0_INTGEN_FIQ` otherwise.
- The `mt_cpmu_aic_pmi()` implementation is conditionally compiled under `CPMU_AIC_PMI`.
- `machine_routines.c` registers that function as the PMI handler only when `CPMU_AIC_PMI && MONOTONIC`.

That is a core performance-monitor overflow path. The AICv2 WFE logic above is a general interrupt-delivery/idle path. The shared presence of an AIC does not prove that the PMU route, generic IRQ routing, WFE event semantics, and controller driver implementation are all interchangeable.

The existing [H9/T8010 migration classification](h9-t8010-migration-risk-classification.md#3-pmu-counter-interrupts-and-aic-coupling) remains correct to classify PMU/AIC coupling as high risk and unresolved.

## 5. Sleep and power context

The reviewed 7195 and 8796 `arm64_prepare_for_sleep()` implementations both retain the `__ARM_GLOBAL_SLEEP_BIT__` deep-sleep path: when the caller requests deep sleep, the code updates ACC override state and then marks the CPU as permitted to power down. This is consistent with the H9 header's declaration of `__ARM_GLOBAL_SLEEP_BIT__`, but it does not supply the target's full sleep/wake contract.

XNU 8796 additionally contains a `HAS_CLUSTER`-guarded shallow-sleep IRQ/FIQ mask path. H9 does not define `HAS_CLUSTER`; H13 does. The 8796 assembly also has a virtual-platform PSCI branch and retention-state conditionals. These must not be treated as T8010 requirements merely because they coexist in the same source file.

The separate [interrupt/timer audit](interrupt-timer-interface-audit.md) records another relevant sleep boundary: the 8796 timebase read retries across a sleep/wake race, while the static 19H422 CPU0 DeviceTree frequency properties are present but zero. Neither the static tree nor the public source defaults establish the final runtime timebase frequency or whether the hardware counter continues through sleep.

Pinned assembly references:

- [XNU 7195 deep-sleep preparation](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines_asm.s#L777-L838)
- [XNU 8796 deep-sleep preparation](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines_asm.s#L868-L931)
- [XNU 7195 H9 header](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [XNU 8796 H13 header](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)

## 6. Source identity and hash cross-check

The following blob IDs were read from the Apple XNU Git trees at the exact tag refs, rather than inferred from filenames or copied from a prior report.

| Ref | File | Git blob SHA-1 |
|---|---|---|
| `xnu-7195.121.3` | `osfmk/arm64/cpu.c` | `ad3f9a68511705fc28d7987cef52236d5ef895af` |
| `xnu-7195.121.3` | `osfmk/arm64/machine_routines.c` | `a5c193df37ad815c715c2b8f8f6c09fbf1a5234d` |
| `xnu-7195.121.3` | `osfmk/arm64/machine_routines_asm.s` | `89ab400089001b547795fe05f3b9ec197f365aef` |
| `xnu-7195.121.3` | `pexpert/pexpert/arm64/H9.h` | `53143c7b6d8efbea630bf2afc32e96fd5ed161fb` |
| `xnu-8796.141.3` | `osfmk/arm64/cpu.c` | `94e91306b14364f720ea80e46d853035aabd78e6` |
| `xnu-8796.141.3` | `osfmk/arm64/machine_routines.c` | `76582da51776aa162df5e6476fb973d31997729b` |
| `xnu-8796.141.3` | `osfmk/arm64/machine_routines_asm.s` | `2449334f5c970c7678b70a3dbfdecb3f6c4fe94b` |
| `xnu-8796.141.3` | `pexpert/pexpert/arm64/H13.h` | `22e8c4068d815da283e2bbd59c23bb5ee29b1066` |

The target DeviceTree report itself is checked in as documentation; the raw DeviceTree remains outside Git because it contains device-specific fields. Its raw SHA-256 and parser accounting are preserved in the linked audit.

## 7. Migration disposition

| Contract | Finding | Disposition |
|---|---|---|
| AICv2 IRQ distribution during WFE | Newer XNU explicitly adds an unmasked-WFE/counter-recheck path with an AICv2 rationale; target static DT reports AIC version 2. | **High risk; relevant but not validated for T8010.** |
| Core CPMU PMI routing | H9 declares AIC PMI; generic code retains the AIC-vs-FIQ selection and conditional PMI handler. | **High risk; distinct from generic AIC IRQ delivery.** |
| Generic CPU sleep | Global-sleep-bit code remains, while cluster/retention/virtual-platform branches vary by profile. | **High risk; hardware semantics and selected target configuration remain unknown.** |
| Timebase across sleep | Newer source handles a sleep/wake race; target static CPU frequency fields are zero. | **High risk; final runtime counter and frequency remain unknown.** |

The next evidence needed is the target-specific AIC driver's actual implementation/contract, authoritative interrupt routing and wake semantics, exact Apple product build flags, and final runtime CPU/timebase state. Public XNU source plus static DeviceTree/KEXT metadata cannot provide those facts.

Do not infer a device configuration, enable a WFE mode, alter boot arguments, or perform a hardware experiment from this note. No device action is requested or authorized.
