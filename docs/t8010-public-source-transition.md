# Public XNU T8010 configuration transition

## Scope

This document records a read-only comparison of Apple's public XNU Git repository
around the transition from the XNU 7195-era snapshot to the XNU 8019.41.5
snapshot. It narrows when the historical A10/T8010 configuration disappeared
from the public source paths reviewed by Project Sweet-10.

It does not explain Apple's internal engineering rationale, establish the
contents of Apple's private build environment, or show that the historical
profile can be restored as a working iPhone9,1 port.

## Snapshot and commit evidence

The public repository history gives the following sequence:

| Evidence point | Commit / date | Observation |
|---|---|---|
| Earlier imported source snapshot | `bb611c8fecc755a0d8e56e2fa51513527c5b7a0e`, 2020-11-19; message `xnu-7195.50.7.100.1` | `H9.h`, the T8010 board block, and the T8010 ARM64 machine mapping are present |
| Next relevant imported snapshot | `e6231be02a03711ca404e5121a151b24afbff733`, 2022-02-04; message `xnu-8019.41.5` | The commit message says the source was imported from `xnu-8019.41.5.tar.gz`; its parent is the earlier XNU 7195 snapshot |
| Later comparison tags | `xnu-8019.80.24`, then `xnu-8796.141.3` | The reviewed ARM64 board configuration and normal machine allowlist continue to omit T8010 |

The commit metadata identifies the 2022 commit as a bulk source import, not a
small, individually described upstream code change. In the public Git history,
the relevant path histories first move from the XNU 7195 snapshot to the XNU
8019.41.5 import at this boundary. The public repository therefore identifies
a concrete snapshot transition, but not the original internal change rationale
or a more granular sequence from Apple's source archive.

## What the older snapshot contains

At the earlier parent snapshot, the following three source inputs agree:

1. `pexpert/pexpert/arm64/H9.h` exists. It defines the Hurricane CPU-family
   configuration, including `APPLEHURRICANE`, `NO_MONITOR`, `HAS_MIGSTS`,
   `HAS_KTRR`, `HAS_CPMU_L2C_EVENTS`, `CORE_NCTRS`, `CPMU_AIC_PMI`,
   `__ARM_16K_PG__`, `__ARM_KERNEL_PROTECT__`,
   `__ARM_GLOBAL_SLEEP_BIT__`, `__ARM_PAN_AVAILABLE__`, and
   `SINGLE_STEP_RETIRE_ERRATA`. It also includes
   `pexpert/arm64/apple_arm64_common.h`.
2. `pexpert/pexpert/arm64/board_config.h` has an
   `ARM64_BOARD_CONFIG_T8010` block that includes H9.h and sets
   `MAX_CPUS=3`, `MAX_CPU_CLUSTERS=1`, and `MAX_L2_CLINE=7). It also
   sets the documented DEVELOPMENT/DEBUG PMAP_CS options.
3. `makedefs/MakeInc.def` includes T8010 in the normal ARM64 machine list and
   defines `MACHINE_FLAGS_ARM64_T8010 = -DARM64_BOARD_CONFIG_T8010 -mcpu=hurricane`.

Together these are stronger evidence than a lone T8010 string: the old public
snapshot contains a CPU-family header, a SoC board-configuration block, and a
build-system machine selection/flag mapping. They establish historical XNU
source support for a T8010 machine configuration in that source generation.
They do not identify an iPhone9,1 product record, D10AP board values, a device
tree, or an iPhone 7 boot contract.

## What changes at the XNU 8019.41.5 import

Comparing the old parent snapshot with the 2022 import shows:

| Path | Earlier snapshot | XNU 8019.41.5 import |
|---|---|---|
| `pexpert/pexpert/arm64/H9.h` | File exists | File is absent at this path (the repository contents lookup returns 404) |
| `pexpert/pexpert/arm64/board_config.h` | Contains `ARM64_BOARD_CONFIG_T8010` and includes H9.h | File remains, but the T8010 block and H9 include are absent |
| `makedefs/MakeInc.def` | Normal ARM64 allowlist contains T8010; T8010 maps to the Hurricane compiler flag | Normal ARM64 allowlist is `BCM2837 T6000 T8101 VMAPPLE`; no T8010 machine flag is present |

The XNU 8019.80.24 and selected XNU 8796.141.3 tagged-source checks are
consistent with this transition: neither exposes T8010 as a normal ARM64
machine selection, and neither has the historical H9.h at the same path.

## Interpretation and limitations

The evidence supports this bounded conclusion:

**The public XNU repository's 2022 XNU 8019.41.5 source import is the first
recorded post-7195 snapshot in the inspected path history where the historical
H9 header, T8010 board block, and T8010 normal ARM64 machine mapping are absent.**

It does not establish why Apple removed or reorganized these files, whether
equivalent support exists in private/downstream source, or whether the feature
definitions were migrated into other headers or implementation paths. A
complete consumer-level audit of each historical H9 macro has not been done.

Do not treat restoring `ARM64_BOARD_CONFIG_T8010`, adding T8010 back to the
allowlist, or reintroducing `-mcpu=hurricane` as a port. Those actions would
only restore names/build selectors; they would not recover the missing
implementation dependencies or provide iPhone9,1-specific board, device-tree,
memory, interrupt, peripheral, and handoff evidence.

## Sources

- [XNU 8019.41.5 import commit](https://github.com/apple-oss-distributions/xnu/commit/e6231be02a03711ca404e5121a151b24afbff733)
- [XNU 7195.50.7.100.1 parent snapshot commit](https://github.com/apple-oss-distributions/xnu/commit/bb611c8fecc755a0d8e56e2fa51513527c5b7a0e)
- [Earlier H9.h at the parent snapshot](https://github.com/apple-oss-distributions/xnu/blob/bb611c8fecc755a0d8e56e2fa51513527c5b7a0e/pexpert/pexpert/arm64/H9.h)
- [Earlier board_config.h at the parent snapshot](https://github.com/apple-oss-distributions/xnu/blob/bb611c8fecc755a0d8e56e2fa51513527c5b7a0e/pexpert/pexpert/arm64/board_config.h)
- [Earlier MakeInc.def at the parent snapshot](https://github.com/apple-oss-distributions/xnu/blob/bb611c8fecc755a0d8e56e2fa51513527c5b7a0e/makedefs/MakeInc.def)
- [XNU 8019.80.24 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8019.80.24/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/makedefs/MakeInc.def)

No device operations, firmware modifications, kernel implementation, or boot
instructions are included.
