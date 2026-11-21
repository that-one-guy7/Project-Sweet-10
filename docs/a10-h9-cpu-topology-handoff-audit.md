# A10/H9 CPU topology and secondary-core handoff audit

## Scope and conclusion

This is a read-only source comparison of public XNU `xnu-7195.121.3`
(the historical T8010/H9 profile) and `xnu-8796.141.3` (the iOS 16-era
candidate). It focuses on CPU topology parsing, cluster indexing, the
secondary-core start interface, and an H9-specific early-start workaround.

**Important positive finding:** XNU 8796 retains an explicit legacy topology
path whose source comment says that H10 and earlier devices are treated as
one physical cluster for MPIDR-based indexing. Since H9/T8010 predates H10,
this is directly relevant to the iPhone 7 generation. The historical H9
profile does not define `HAS_CLUSTER`, while the newer H13 profile does.
That makes the non-`HAS_CLUSTER` path a plausible architectural fit for an
H9-style profile.

**Important blocker:** the secondary-core release contract changed between
the two public source revisions. XNU 7195 passes the physical address of
`LowResetVectorBase` to `IOPMGR::enableCPUCore`; XNU 8796 passes zero on
physical (non-`APPLEVIRTUALPLATFORM`) builds and passes the reset-vector
address only for the virtual platform. The public source does not include
the matching proprietary PMGR implementation or establish that this newer
contract is valid for T8010.

This is meaningful CPU-path evidence, **not** proof that an XNU 8796
T8010 build exists, that secondary CPUs start, or that the iPhone 7 can run
the donor kernel. No target code or device state is changed.

## 1. Legacy single-cluster topology remains in XNU 8796

The historical H9 header at
[`xnu-7195.121.3/pexpert/pexpert/arm64/H9.h`](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
defines `APPLEHURRICANE` and the H9 feature set, but does not define
`HAS_CLUSTER`. By contrast, the XNU 8796 H13 profile explicitly defines
`HAS_CLUSTER=1` for its multi-cluster generation:
[`H13.h`](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h).

In XNU 8796 `osfmk/arm64/machine_routines.c`, CPU topology parsing uses
`MPIDR_EL1.AFF1` as the physical cluster identifier when `HAS_CLUSTER`
is enabled. Without it, the code derives a legacy logical cluster from
CPU type instead (the `CLUSTER_TYPE_P` distinction). More importantly,
the non-`HAS_CLUSTER` branch at lines 1110–1115 documents that H10-era
devices have two physical clusters behind a single ACC, with AFF1 fixed at
zero and AFF0 numbered linearly. For MPIDR-based indexing, the code therefore
models H10 and earlier devices as one cluster.

Source: [XNU 8796 machine_routines.c, topology parser](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c#L1036-L1116).

This is the strongest positive CPU-compatibility clue found in this pass:
the newer generic XNU code still deliberately handles the pre-HAS_CLUSTER
topology model. The H9 header's lack of `HAS_CLUSTER` is consistent with
that legacy branch. However, the H9 board selector/header is absent from
the reviewed XNU 8796 public source tree, so no T8010 product build is
shown to select this path. The source comment also discusses H10 and earlier
as a family-level model; it is not a per-device validation of the iPhone 7.

## 2. Target DeviceTree agrees with a simple legacy topology shape, but is incomplete evidence

The parsed iPhone9,1 / 19H422 DeviceTree audit records two CPU children:

| Node | `reg` | `state` | `compatible` |
|---|---:|---|---|
| `/cpus/cpu0` | 0 | `running` | `apple,hurricane-zephyr`, `ARM,v8` |
| `/cpus/cpu1` | 1 | `waiting` | `apple,hurricane-zephyr`, `ARM,v8` |

Source: [Project Sweet-10 parsed target DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md#cpu-nodes).

XNU's topology parser reads each CPU node's `reg` as the physical ID,
uses the `state=running` node to identify the boot CPU, and derives
logical CPU/cluster indexes from the selected compile-time feature path.
That is conceptually compatible with a two-entry, single-cluster tree.

Do not confuse the historical H9 `MAX_CPUS=3` board constant with the
number of CPU nodes or the number of online CPUs. `MAX_CPUS` sizes kernel
topology/per-CPU structures; the parsed DeviceTree supplies the observed
CPU entries. The existing target DeviceTree audit explicitly cautions that
its two nodes do not independently establish the final physical or enabled
CPU count. The static tree also does not prove that the donor-era handoff
presents the same tree at runtime.

## 3. Secondary-core release is still platform-manager dependent

Both reviewed XNU revisions retain the same broad layering:

1. `osfmk/arm64/cpu.c::cpu_start()` prepares the per-CPU data and calls
   `PE_cpu_start()` for a secondary CPU.
2. `iokit/Kernel/arm/AppleARMSMP.cpp` implements the platform hook.
3. The platform hook asks `IOPMGR::enableCPUCore()` to release the core.
4. The target CPU must then enter the low reset/startup path and continue
   through the per-CPU initialization contract.

The implementation is not identical:

- **XNU 7195.121.3:** `PE_cpu_start()` always passes
  `ml_vtophys(&LowResetVectorBase)` to `enableCPUCore()`
  ([source lines 232–243](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/iokit/Kernel/arm/AppleARMSMP.cpp#L232-L243)).
- **XNU 8796.141.3:** on `APPLEVIRTUALPLATFORM`, it passes that reset-vector
  address; on physical builds, it passes `0`
  ([source lines 266–279](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/Kernel/arm/AppleARMSMP.cpp#L266-L279)).

The 8796 `cpu_start()` caller still invokes the hook
([source line 946](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c#L946)).
This shows that the generic CPU framework remains, but the physical
reset-vector contract expected by the platform manager changed. The
`IOPMGR` implementation that would explain how T8010 handles the zero
argument is not established by these public XNU files. Do not assume the
older T8010 PMGR accepts the newer call semantics.

## 4. H9-specific early CPU workaround is absent from the reviewed 8796 startup assembly

The historical XNU 7195 `osfmk/arm64/start.s` has an
`#if defined(APPLEHURRICANE)` block that writes HID5 to increase the EDB
snoop reservation before MMU enable
([lines 682–685](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/start.s#L682-L685)).
The corresponding reviewed XNU 8796 `start.s` has no matching
`APPLEHURRICANE` block.

The full-tree H9 macro audit also found three remaining 8796
`APPLEHURRICANE` occurrences in other source files, but those do not
reinstate this early-start assembly workaround. Its removal/replacement
rationale and relevance to the exact 20H392 product build remain unknown.
This should stay a separate CPU-startup question, not be silently discarded
because the legacy topology branch remains.

## 5. Hurricane-specific CPU code still exists in XNU 8796

The full-tree audit's three XNU 8796 `APPLEHURRICANE` occurrences are not
all diagnostic leftovers:

- `osfmk/arm64/proc_reg.h:168` retains Hurricane-specific instruction- and
  data-cache line-size definitions (`MMU_I_CLINE=6` and `MMU_CLINE=6`,
  i.e. 64-byte lines).
- `osfmk/arm64/monotonic_arm64.c:174` sets the EL3 PMU counter-enable
  contribution to zero for `APPLEHURRICANE`, matching the H9 profile's
  `NO_MONITOR=1` declaration.
- `osfmk/arm64/sleh.c:232` retains the `Hurricane` CPU-name string used
  in exception diagnostics.

Sources: [proc_reg.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/proc_reg.h#L164-L170),
[monotonic_arm64.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/monotonic_arm64.c#L170-L180),
and [sleh.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/sleh.c#L228-L240).

The cache-line and PMU conditionals are meaningful retained CPU-family
behavior, not just string matches. Together with the legacy topology branch,
they show that XNU 8796 still has several pieces of H9-era architecture
knowledge. But the H9 board profile itself is absent, and the source scan
does not prove that Apple's 20H392 product build defines `APPLEHURRICANE`
or selects these branches for any supported product. The CPU-name string
alone is diagnostic; do not treat it as a hardware capability check.

## 6. Evidence classification

| Question | Finding | Status |
|---|---|---|
| Does XNU 8796 retain a pre-HAS_CLUSTER topology path? | Yes; it explicitly documents H10 and earlier as single-cluster for MPIDR indexing. | **Positive source evidence** |
| Is the path consistent with the historical H9 profile? | H9 does not define `HAS_CLUSTER`; H13 does. | **Strongly suggestive, not a selected-build proof** |
| Does the target reference tree have CPU nodes compatible with simple logical IDs? | Two nodes with `reg=0/1`, one running and one waiting. | **Static DeviceTree evidence only** |
| Does the 8796 CPU framework still call a platform core-release hook? | Yes, through `PE_cpu_start()`. | **Positive framework evidence** |
| Is the physical PMGR reset-vector argument proven for T8010? | No; the newer physical path passes zero, and the relevant PMGR implementation is unavailable in this source review. | **Critical unresolved contract** |
| Is the historical H9 HID5 startup workaround retained? | No matching block in reviewed 8796 `start.s`. | **Unresolved CPU initialization difference** |
| Is CPU startup working on iPhone9,1? | No runtime evidence. | **Not established** |

## 7. IOPMGR preserves a legacy core-enable fallback in both XNU revisions

A follow-up inspection of `iokit/IOKit/IOPMGR.h` and
`iokit/Kernel/IOPMGR.cpp` in both `xnu-7195.121.3` and
`xnu-8796.141.3` changes the interpretation of the reset-vector argument
difference above.

Both revisions expose two virtual overloads:

- `enableCPUCore(unsigned int cpu_id, uint64_t entry_pa)`
- the older `enableCPUCore(unsigned int cpu_id)`

In both revisions, the base implementation of the two-argument overload
calls the one-argument overload. The one-argument base implementation
panics if no subclass implements it. Because the call is virtual, a PMGR
subclass that implements only the legacy one-argument method can still
receive the core-enable request when the newer XNU caller invokes the
two-argument method. The two-argument base method does not use
`entry_pa` when taking this fallback.

The public header also documents that the reset-vector argument is not
honored by every platform and that Apple Silicon can have its reset vector
programmed by iBoot. That documentation is consistent with a platform
where firmware/PMGR owns the reset-vector setup, but it does **not** prove
how the iPhone 7's T8010 PMGR or iBoot handles it.

Sources:
- [XNU 7195 IOPMGR.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/iokit/IOKit/IOPMGR.h)
- [XNU 7195 IOPMGR.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/iokit/Kernel/IOPMGR.cpp)
- [XNU 8796 IOPMGR.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/IOKit/IOPMGR.h)
- [XNU 8796 IOPMGR.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/Kernel/IOPMGR.cpp)

### Revised interpretation

The earlier observation that XNU 8796 passes zero on physical builds remains
correct, but treating that alone as a changed T8010 reset-vector contract
was too strong. The public IOPMGR compatibility shim shows that a legacy
PMGR subclass may continue to receive the old one-argument call. Therefore:

- **Resolved at the generic XNU API layer:** the two-argument API retains a
  backward-compatibility route to the legacy one-argument override.
- **Still unresolved for T8010:** whether the relevant target PMGR subclass
  implements the legacy override, whether it is present/loaded in the
  candidate environment, and how the iPhone 7 firmware establishes the
  secondary-core reset vector.
- **Not established:** secondary-core startup, interrupt delivery to the
  secondary CPU, CPU online status, or runtime stability.

This downgrades the reset-vector API difference from a presumed hard
incompatibility to a narrower platform-implementation and firmware question.
It is a positive source-compatibility finding, not proof of hardware
compatibility.

## Next read-only CPU research

1. Trace the exact XNU 8796 compile-time guards around the legacy topology
   branch and the `USE_APPLEARMSMP` implementation, without assuming a
   T8010 product build selects them.
2. Compare the target 19H422 and donor 20H392 DeviceTree CPU-node properties
   field by field, preserving the distinction between static tree content
   and the runtime tree handed to XNU.
3. Inventory public declarations/callers of `IOPMGR::enableCPUCore` and
   identify which parts of its implementation are absent from public XNU.
   Do not invent the private PMGR semantics.
4. Continue tracing the H9 HID5 workaround's related register definitions
   and all historical consumers to determine whether the 8796 startup path
   has a documented replacement.
5. Keep CPU topology, CPU release, PMU/AIC interrupt delivery, and CPU
   power/idle as separate contracts; a positive result in one does not
   close the others.

No kernel profile, CPU constant, assembly instruction, reset-vector
argument, or device setting is approved by this audit. The physical iPhone 7
remains on iOS 12.1.4.
